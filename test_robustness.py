import engine
import database
import os

# Initialize database
database.initialise_db()

def test_nlp_robustness():
    """
    Stress test the NLP engine with various linguistic challenges:
    1. Grammar/Syntax errors
    2. Restructured sentences
    3. Typos/Fuzzy matching
    4. Slang/Informal phrasing
    """
    
    # Format: (input_query, expected_keyword_in_response, category)
    test_cases = [
        # --- TYPOS & FUZZY MATCHING ---
        ("Helllo there", "Hello!", "Typo"),
        ("pakages", "packages", "Typo"),
        ("wht packges aare available", "packages", "Human-like/Typo"),
        ("destinaton", "packages", "Typo"),
        ("Bli tours", "Bali Bliss", "Typo/Entity"),
        ("Maldivs price", "Maldives Dream Escape", "Typo/Entity"),
        ("Erope trip", "European Explorer (Europe)", "Typo/Entity"),
        
        # --- GRAMMAR & SYNTAX ---
        ("i wanting to go Bali", "Bali Bliss", "Grammar"),
        ("give me the informations about tours", "packages", "Grammar"),
        ("what be the cost for Thailand?", "Thailand Adventure", "Grammar"),
        ("me looking for cheap deal", "packages", "Grammar"),
        
        # --- RESTRUCTURING ---
        ("Bali tours show me please", "Bali Bliss", "Restructuring"),
        ("Price for Maldives tell me", "Maldives Dream Escape", "Restructuring"),
        ("Available any packages are?", "packages", "Restructuring"),
        ("To Sri Lanka I want to go", "Sri Lanka Heritage", "Restructuring"),
        
        # --- SLANG & INFORMAL ---
        ("yo what's up", "Hello!", "Informal"),
        ("sup travelmate", "Hello!", "Informal"),
        ("gimme some deals", "packages", "Informal"),
        ("cheapest trip u got?", "packages", "Informal"),
        
        # --- COMPLEX/NATURAL ---
        ("I'm planning a holiday and I want to see what you have for Europe", "European Explorer", "Complex"),
        ("Can you please help me find a 7 day trip to Sri Lanka?", "Sri Lanka Heritage", "Complex"),
        ("I am interested in visiting Dubai, how much does it cost?", "Dubai Luxury Getaway", "Complex"),
        
        # --- INTELLIGENCE / SUPERLATIVES ---
        ("whats the cheapest place", "budget-friendly", "Intelligence"),
        ("what is the cheapest package", "Sri Lanka Heritage", "Intelligence"),
        ("show me the most expensive luxury trip", "premium luxury", "Intelligence"),
        ("lowest price packages", "budget-friendly", "Intelligence"),
        ("best luxurious deals", "premium luxury", "Intelligence")
    ]

    print("="*60)
    print(f"{'CATEGORY':<15} | {'INPUT':<40} | {'RESULT'}")
    print("-"*60)
    
    passed = 0
    for inp, expected, category in test_cases:
        response = engine.process_user_input(inp)
        
        # Check if the response contains the expected keyword or matches the intent
        is_match = False
        if response:
            if expected.lower() in response.lower():
                is_match = True
            # Special case for "Hello!" which matches greeting responses
            elif expected == "Hello!" and any(word in response for word in ["Hello", "Hi", "Hey"]):
                is_match = True
            # Special case for "packages" which triggers the search response
            elif expected == "packages" and "Here are some packages" in response:
                is_match = True

        result_icon = "✅" if is_match else "❌"
        if is_match: passed += 1
        
        print(f"{category:<15} | {inp[:40]:<40} | {result_icon}")
        if not is_match:
            print(f"{' ':18} Expected: '{expected}' | Got: {str(response)[:50]}...")

    print("-"*60)
    print(f"OVERALL PERFORMANCE: {passed}/{len(test_cases)} ({passed/len(test_cases)*100:.1f}%)")
    print("="*60)

if __name__ == "__main__":
    test_nlp_robustness()
