"""
engine.py — Inference Engine for TravelMate chatbot
Implements three AI traits:
1. NLP/Lemmatization — tokenizes and lemmatizes user input for intent matching
2. Searching — queries SQLite database for live package data
3. Learning — stores new Q&A pairs learned from user interaction
"""

import os
import json
import random
import difflib
import re
import sys
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import database

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# Set NLTK data path
# For the executable, we prefer a local path that is bundled or in the app data
nltk_data_path = get_resource_path("nltk_data")
if not os.path.exists(nltk_data_path):
    os.makedirs(nltk_data_path, exist_ok=True)
nltk.data.path.append(nltk_data_path)

# Download required NLTK data (only if not bundled)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', download_dir=nltk_data_path, quiet=True)
try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet', download_dir=nltk_data_path, quiet=True)
try:
    nltk.data.find('corpora/omw-1.4')
except LookupError:
    nltk.download('omw-1.4', download_dir=nltk_data_path, quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', download_dir=nltk_data_path, quiet=True)

# Load static knowledge base (intents.json)
intents_file = get_resource_path('intents.json')
with open(intents_file, 'r', encoding='utf-8') as f:
    intents_data = json.load(f)

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))
# Add common domain words to stop words to avoid noisy matching (e.g., 'travel' matching 'trail')
# NOTE: We keep 'package', 'tour', 'trip', etc. as they are important keywords for intent matching
stop_words.update({'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being'}) 
CONTINENTS = {'asia', 'europe', 'america', 'africa', 'oceania', 'middle east', 'caribbean'}


def preprocess_input(user_input, remove_stopwords=False):
    """
    AI Trait 1: NLP / Lemmatization
    Tokenize and lemmatize user input to normalize words for matching.
    Optionally removes stop words to focus on intent-carrying keywords.
    """
    tokens = word_tokenize(user_input.lower())
    lemmatized = [lemmatizer.lemmatize(token) for token in tokens if token.isalnum()]
    
    if remove_stopwords:
        lemmatized = [token for token in lemmatized if token not in stop_words]
        
    return lemmatized


def fuzzy_match_tokens(user_tokens, pattern_tokens):
    """
    Checks if tokens in user input match pattern tokens, 
    allowing for slight spelling mistakes (fuzzy matching).
    """
    match_count = 0
    for u_token in user_tokens:
        # Direct match
        if u_token in pattern_tokens:
            match_count += 1
            continue
        
        # Fuzzy match for typos (only for words longer than 3 chars)
        if len(u_token) > 3:
            matches = difflib.get_close_matches(u_token, pattern_tokens, n=1, cutoff=0.8)
            if matches:
                match_count += 1
                
    return match_count


def match_intent(user_input):
    """
    Match user input against intent patterns using NLP and fuzzy matching.
    Robust against:
    - Restructured sentences (bag-of-words approach)
    - Grammar/Syntax (lemmatization)
    - Typos (fuzzy matching)
    """
    user_tokens = preprocess_input(user_input)
    user_tokens_no_stop = preprocess_input(user_input, remove_stopwords=True)
    
    # Keyword boost: if user mentions a destination, boost the 'packages' intent
    all_packages = database.get_all_packages()
    destinations = [p['destination'].lower() for p in all_packages]
    names = [p['name'].lower() for p in all_packages]
    
    has_geo_keyword = False
    for kw in user_tokens_no_stop:
        if len(kw) < 3 and kw not in CONTINENTS: continue
        if kw in CONTINENTS or any(kw in d for d in destinations) or any(kw in n for n in names) or \
           difflib.get_close_matches(kw, destinations, n=1, cutoff=0.8) or \
           difflib.get_close_matches(kw, names, n=1, cutoff=0.8):
            has_geo_keyword = True
            break

    best_tag = None
    best_score = 0

    for intent in intents_data['intents']:
        tag = intent['tag']
        patterns = intent['patterns']

        for pattern in patterns:
            pattern_tokens = word_tokenize(pattern.lower())
            pattern_lemmatized = [lemmatizer.lemmatize(t) for t in pattern_tokens if t.isalnum()]
            
            # 1. Try matching with full tokens
            matches = fuzzy_match_tokens(user_tokens, pattern_lemmatized)
            score = matches / max(len(pattern_lemmatized), 1)
            
            # 2. Try matching with keywords only
            pattern_keywords = [t for t in pattern_lemmatized if t not in stop_words]
            if pattern_keywords:
                kw_matches = fuzzy_match_tokens(user_tokens_no_stop, pattern_keywords)
                kw_score = kw_matches / len(pattern_keywords)
                score = max(score, kw_score)

            # Penalize very short pattern matches in very long sentences 
            # (e.g., "see you" matching "I want to see... you...")
            if len(pattern_lemmatized) <= 2 and len(user_tokens) > 6:
                score *= 0.5

            # 3. Apply geo-boost to package-related intents
            if has_geo_keyword and tag in ['packages', 'destination', 'price', 'duration']:
                score += 0.5

            if score > best_score and score > 0.7:
                best_score = score
                best_tag = tag

    return best_tag


def get_response_for_intent(tag, user_input):
    """
    Generate response based on matched intent tag.
    Handles special cases like database queries.
    """
    intent = next((i for i in intents_data['intents'] if i['tag'] == tag), None)
    if not intent:
        return None

    responses = intent['responses']

    # Special case: database search trigger
    if responses == ["__SEARCH_PACKAGES__"]:
        return search_packages_response(user_input)

    # Return random static response
    return random.choice(responses)


def _extract_days(duration_str):
    """Helper to extract the number of days from a duration string for comparison."""
    match = re.search(r'(\d+)\s+day', duration_str.lower())
    if match:
        return int(match.group(1))
    return 0


def search_packages_response(user_input):
    """
    AI Trait 2: Searching
    Query SQLite database for packages matching keywords in user input.
    Robust against typos, multiple keywords, and handles superlatives (cheapest, longest, etc.).
    """
    # 1. Preprocess and identify intent context
    raw_tokens = word_tokenize(user_input.lower())
    keywords = preprocess_input(user_input, remove_stopwords=True)
    
    # Contextual keywords that should trigger a FULL dataset scan if no specific destination is found
    # These represent "show me everything" or "show me based on a filter" requests.
    general_trigger_keywords = {
        'package', 'tour', 'deal', 'offer', 'trip', 'holiday', 'vacation', 
        'available', 'show', 'list', 'give', 'find', 'getaway', 'quick', 'everything',
        'anything', 'interesting', 'recommend', 'suggestion', 'idea', 'popular',
        'compare', 'difference', 'variance', 'vs', 'versus'
    }.union(CONTINENTS)
    
    # Superlative flags
    sort_by_price_asc = any(w in raw_tokens for w in ['cheapest', 'cheap', 'lowest', 'budget'])
    sort_by_price_desc = any(w in raw_tokens for w in ['expensive', 'luxurious', 'luxury', 'highest', 'best', 'premium'])
    sort_by_duration_desc = any(w in raw_tokens for w in ['longest', 'long', 'max'])
    sort_by_duration_asc = any(w in raw_tokens for w in ['shortest', 'short', 'minimum', 'quick'])
    
    # Keywords for superlatives/filtering that shouldn't be treated as specific search terms
    filter_keyword_stems = {
        'cheap', 'low', 'budget', 'expensive', 'luxury', 'high', 'best', 'premium',
        'long', 'short', 'duration', 'price', 'cost', 'under', 'over', 'above', 'below',
        'day', 'night'
    }

    # Numerical filters (Range filtering)
    price_limit = None
    price_operator = None # 'under' or 'over'
    
    price_match = re.search(r'(under|below|less than|over|above|more than|budget of)\s+\$?\s*(\d+)', user_input.lower())
    if price_match:
        price_operator = price_match.group(1)
        price_limit = float(price_match.group(2))
    
    # Comparison check
    is_comparison = any(w in raw_tokens for w in ['compare', 'difference', 'variance', 'vs', 'versus'])

    # 2. Search for specific destinations/names
    all_results = []
    seen_names = set()
    all_packages = database.get_all_packages()
    
    # Create a matching pool of individual words from names and destinations
    matching_pool = set()
    for p in all_packages:
        matching_pool.update(preprocess_input(p['name']))
        matching_pool.update(preprocess_input(p['destination']))
    
    dest_name_list = list(matching_pool)
    found_specific_destination = False
    is_explicit_general_request = False
    unknown_geo_keywords = []
    
    for kw in keywords:
        # Identify explicit requests for general information
        if kw in general_trigger_keywords:
            is_explicit_general_request = True
            # For continent-specific general requests, we still want to filter by that continent
            if kw in CONTINENTS:
                packages = database.search_packages(kw)
                if packages:
                    found_specific_destination = True
                    for pkg in packages:
                        if pkg['name'] not in seen_names:
                            all_results.append(pkg)
                            seen_names.add(pkg['name'])
            continue
            
        # Ignore filter-related keywords for destination search
        if any(stem in kw for stem in filter_keyword_stems):
            continue

        # Ignore very short words
        if len(kw) < 3:
            continue
            
        # Try direct search (only for words > 3 chars to avoid noisy substring matches)
        packages = []
        if len(kw) > 3 or kw in CONTINENTS:
            packages = database.search_packages(kw)
        
        # Try fuzzy search (only for words > 3 chars)
        if not packages and len(kw) > 3:
            # Match against the pool of individual words
            fuzzy_matches = difflib.get_close_matches(kw, dest_name_list, n=1, cutoff=0.7)
            for match in fuzzy_matches:
                packages.extend(database.search_packages(match))
                
        # Substring search as a last resort (only for words > 3 chars)
        if not packages and len(kw) > 3:
            for d in dest_name_list:
                if kw in d:
                    packages.extend(database.search_packages(d))
                
        if packages:
            found_specific_destination = True
            for pkg in packages:
                if pkg['name'] not in seen_names:
                    all_results.append(pkg)
                    seen_names.add(pkg['name'])
        elif kw not in ['show', 'find', 'give', 'list', 'tours', 'packages'] and not kw.isdigit():
            # Keep track of words that might be unknown destinations (exclude numbers)
            unknown_geo_keywords.append(kw)

    # 3. Decision Logic: 
    is_superlative_query = any([sort_by_price_asc, sort_by_price_desc, sort_by_duration_asc, sort_by_duration_desc])
    
    if not found_specific_destination:
        # If they asked for a specific unknown place, don't fallback to "all"
        if unknown_geo_keywords:
            return f"I couldn't find any packages for '{', '.join(unknown_geo_keywords)}'. Try asking about 'Bali', 'Europe', or 'Thailand'!"
            
        if is_explicit_general_request or is_superlative_query or price_limit or is_comparison:
            all_results = all_packages
        else:
            return None

    # Apply Numerical Filtering
    if price_limit:
        if any(op in price_operator for op in ['under', 'below', 'less', 'budget']):
            all_results = [p for p in all_results if p['price'] <= price_limit]
        elif any(op in price_operator for op in ['over', 'above', 'more']):
            all_results = [p for p in all_results if p['price'] >= price_limit]

    if not all_results:
        return "I couldn't find any packages matching your specific criteria. Try adjusting your filters or destination!"

    # 4. Handle Comparisons
    if is_comparison and len(all_results) >= 2:
        # If more than 2, just compare the top 2
        p1, p2 = all_results[0], all_results[1]
        diff = abs(p1['price'] - p2['price'])
        perc = (diff / min(p1['price'], p2['price'])) * 100
        
        d1 = _extract_days(p1['duration'])
        d2 = _extract_days(p2['duration'])
        
        response = f"📊 **Comparison: {p1['name']} vs {p2['name']}**\n\n"
        response += f"💰 **Price:** ${p1['price']} vs ${p2['price']} "
        response += f"(Difference: ${diff:.2f}, ~{perc:.1f}%)\n"
        response += f"⏱ **Duration:** {p1['duration']} vs {p2['duration']}\n"
        response += f"📍 **Destination:** {p1['destination']} vs {p2['destination']}\n"
        response += f"📝 **Highlights:** {p1['description'][:50]}... vs {p2['description'][:50]}...\n\n"
        response += "Which one looks better for your next adventure?"
        return response

    # 5. Apply Intelligence: Sorting
    if sort_by_price_asc:
        all_results.sort(key=lambda x: x['price'])
        intro = "Based on your request, here are our most budget-friendly packages:\n\n"
    elif sort_by_price_desc:
        all_results.sort(key=lambda x: x['price'], reverse=True)
        intro = "Based on your request, here are our premium luxury packages:\n\n"
    elif sort_by_duration_desc:
        all_results.sort(key=lambda x: _extract_days(x['duration']), reverse=True)
        intro = "Based on your request, here are our longest available tours:\n\n"
    elif sort_by_duration_asc:
        all_results.sort(key=lambda x: _extract_days(x['duration']))
        intro = "Based on your request, here are our shortest quick-getaway packages:\n\n"
    else:
        intro = "Here are some packages I found:\n\n"

    # 6. Format Response
    response = intro
    for pkg in all_results[:3]:
        response += f"📦 {pkg['name']}\n"
        response += f"   📍 {pkg['destination']}\n"
        response += f"   ⏱ {pkg['duration']}\n"
        response += f"   💰 ${pkg['price']}\n"
        response += f"   📝 {pkg['description']}\n\n"

    if len(all_results) > 3:
        response += f"...and {len(all_results) - 3} more. Contact us for details!"

    return response


def learn_response(question, answer):
    """
    AI Trait 3: Learning (Machine Learning)
    Store new Q&A pair learned from user interaction.
    This allows the bot to improve over time.
    """
    database.save_learned_response(question, answer)


def get_learned_answer(question):
    """Check if we've learned an answer for this question before."""
    return database.get_learned_response(question)


def process_user_input(user_input):
    """
    Main inference pipeline:
    1. Check learned responses first (learning tier)
    2. If not found, use NLP to match intent
    3. If intent requires DB search, query database (searching tier)
    4. If no match, check if query is in-domain; if not, return support message
    5. If in-domain but unknown, return None to trigger learning mode
    """
    # Step 1: Check learned responses
    learned = get_learned_answer(user_input)
    if learned:
        return learned

    # Step 2: NLP intent matching
    tag = match_intent(user_input)

    # High-confidence intent matching
    if tag:
        return get_response_for_intent(tag, user_input)

    # Step 3: Domain check for unknown inputs
    # If no high-confidence intent matched, check if the input is travel-related
    travel_keywords = {
        'travel', 'trip', 'holiday', 'vacation', 'package', 'tour', 'flight', 'hotel',
        'booking', 'destination', 'visit', 'explore', 'adventure', 'ticket', 'visa',
        'passport', 'itinerary', 'baggage', 'luggage', 'airport', 'resort', 'stay',
        'cruise', 'island', 'beach', 'mountain', 'hiking', 'sightseeing', 'guide',
        'price', 'cost', 'budget', 'cheap', 'expensive', 'luxury', 'days', 'nights',
        'asia', 'europe', 'america', 'africa', 'oceania', 'middle east', 'caribbean'
    }
    
    user_tokens = preprocess_input(user_input)
    is_travel_related = any(token in travel_keywords for token in user_tokens)
    
    # Also check if it mentions any known destinations or package names from DB
    if not is_travel_related:
        all_packages = database.get_all_packages()
        user_input_lower = user_input.lower()
        for pkg in all_packages:
            if pkg['destination'].lower() in user_input_lower or pkg['name'].lower() in user_input_lower:
                is_travel_related = True
                break
            
    # Before failing domain check, check if it's a very short greeting/farewell that missed threshold
    if not is_travel_related:
        short_tokens = word_tokenize(user_input.lower())
        greetings = {'hi', 'hello', 'hey', 'bye', 'thanks'}
        if any(t in greetings for t in short_tokens):
            is_travel_related = True

    if not is_travel_related:
        return "I'm sorry, but I specialize in travel and holiday planning! 🌍 For other inquiries, please refer to our Help and Support section. How can I help you with your next adventure? ✈️"

    # Step 4: No match found but seems travel-related — signal that we need to learn
    return None


# ─── Quick test ───────────────────────────────────────────────────
if __name__ == "__main__":
    database.initialise_db()

    test_inputs = [
        "Hello",
        "What packages do you have?",
        "Show me Bali tours",
        "How much is the Maldives trip?",
        "Goodbye"
    ]

    print("=== Engine Test ===\n")
    for inp in test_inputs:
        print(f"User: {inp}")
        response = process_user_input(inp)
        if response:
            print(f"Bot:  {response}\n")
        else:
            print(f"Bot:  [Unknown - would trigger learning]\n")
