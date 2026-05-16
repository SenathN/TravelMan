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
import nltk
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
import database

# Set NLTK data path to current directory to avoid permission issues
nltk_data_path = os.path.join(os.path.dirname(__file__), "nltk_data")
if not os.path.exists(nltk_data_path):
    os.makedirs(nltk_data_path)
nltk.data.path.append(nltk_data_path)

# Download required NLTK data (only first time)
nltk.download('punkt_tab', download_dir=nltk_data_path, quiet=True)
nltk.download('wordnet', download_dir=nltk_data_path, quiet=True)
nltk.download('omw-1.4', download_dir=nltk_data_path, quiet=True)
nltk.download('stopwords', download_dir=nltk_data_path, quiet=True)

# Load static knowledge base (intents.json)
with open('intents.json', 'r') as f:
    intents_data = json.load(f)

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))


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
        if len(kw) < 3: continue
        if any(kw in d for d in destinations) or any(kw in n for n in names) or \
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
            
            # Penalize very short pattern matches in very long sentences 
            # (e.g., "see you" matching "I want to see... you...")
            if len(pattern_lemmatized) <= 2 and len(user_tokens) > 6:
                score *= 0.5

            # 2. Try matching with keywords only
            pattern_keywords = [t for t in pattern_lemmatized if t not in stop_words]
            if pattern_keywords:
                kw_matches = fuzzy_match_tokens(user_tokens_no_stop, pattern_keywords)
                kw_score = kw_matches / len(pattern_keywords)
                score = max(score, kw_score * 1.2)

            # 3. Apply geo-boost to package-related intents
            if has_geo_keyword and tag in ['packages', 'destination', 'price', 'duration']:
                score += 0.5

            if score > best_score and score > 0.4:
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


def search_packages_response(user_input):
    """
    AI Trait 2: Searching
    Query SQLite database for packages matching keywords in user input.
    Robust against typos, multiple keywords, and handles superlatives (cheapest, etc.).
    """
    # 1. Preprocess and identify intent context
    raw_tokens = word_tokenize(user_input.lower())
    keywords = preprocess_input(user_input, remove_stopwords=True)
    
    # Contextual keywords that should NOT trigger a specific destination search
    context_keywords = [
        'package', 'tour', 'deal', 'offer', 'trip', 'holiday', 'vacation', 
        'available', 'show', 'list', 'give', 'find', 'cheapest', 'cheap', 
        'lowest', 'budget', 'expensive', 'luxurious', 'luxury', 'highest', 
        'best', 'premium', 'price', 'cost', 'money', 'value'
    ]
    
    sort_by_price_asc = any(w in raw_tokens for w in ['cheapest', 'cheap', 'lowest', 'budget'])
    sort_by_price_desc = any(w in raw_tokens for w in ['expensive', 'luxurious', 'luxury', 'highest', 'best', 'premium'])
    
    # 2. Search for specific destinations/names
    all_results = []
    seen_names = set()
    all_packages = database.get_all_packages()
    
    destinations = [p['destination'].lower() for p in all_packages]
    names = [p['name'].lower() for p in all_packages]
    
    found_specific_destination = False
    
    for kw in keywords:
        # Ignore very short words or general context words
        if len(kw) < 3 or kw in context_keywords:
            continue
            
        # Try direct search
        packages = database.search_packages(kw)
        
        # Try fuzzy search
        if not packages:
            # Balanced cutoff for typo tolerance without false positives
            fuzzy_matches = difflib.get_close_matches(kw, destinations + names, n=1, cutoff=0.6)
            for match in fuzzy_matches:
                # Extract first word to search (e.g., "Bali" from "Bali, Indonesia")
                search_term = match.split(',')[0].split(' ')[0]
                packages.extend(database.search_packages(search_term))
                
        # Substring search as a last resort
        if not packages:
            for d in destinations + names:
                if kw in d:
                    search_term = d.split(',')[0].split(' ')[0]
                    packages.extend(database.search_packages(search_term))
                
        if packages:
            found_specific_destination = True
            for pkg in packages:
                if pkg['name'] not in seen_names:
                    all_results.append(pkg)
                    seen_names.add(pkg['name'])

    # 3. Decision Logic: Use full dataset if no specific destination was found 
    # OR if the user is asking a general superlative question
    if not found_specific_destination or (not all_results and (sort_by_price_asc or sort_by_price_desc)):
        all_results = all_packages

    if not all_results:
        return "I couldn't find any packages matching your query. Try asking about 'Bali', 'Maldives', 'Europe', 'Thailand', 'Sri Lanka', or 'Dubai'."

    # 4. Apply Intelligence: Sorting
    if sort_by_price_asc:
        all_results.sort(key=lambda x: x['price'])
        intro = "Based on your request, here are our most budget-friendly packages:\n\n"
    elif sort_by_price_desc:
        all_results.sort(key=lambda x: x['price'], reverse=True)
        intro = "Based on your request, here are our premium luxury packages:\n\n"
    else:
        intro = "Here are some packages I found:\n\n"

    # 5. Format Response
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
    4. If no match, return None to trigger learning mode
    """
    # Step 1: Check learned responses
    learned = get_learned_answer(user_input)
    if learned:
        return learned

    # Step 2: NLP intent matching
    tag = match_intent(user_input)

    if tag:
        return get_response_for_intent(tag, user_input)

    # Step 3: No match found — signal that we need to learn
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
