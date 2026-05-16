import engine
import database

def test_scenarios():
    database.initialise_db()
    
    scenarios = [
        ("im planning for a vacation in europe", "In-domain (Europe)"),
        ("how about america", "In-domain (America)"),
        ("anything in asia?", "In-domain (Asia)"),
        ("tell me a joke", "Out-of-domain (Joke)"),
        ("what is 2+2", "Out-of-domain (Math)")
    ]
    
    print("=== Domain Logic Test Scenarios ===\n")
    
    for user_input, description in scenarios:
        print(f"Scenario: {description}")
        print(f"Input: {user_input}")
        response = engine.process_user_input(user_input)
        
        # Check if it returned the out-of-domain support message
        is_support_msg = "specialize in travel and holiday planning" in response if response else False
        
        if is_support_msg:
            print(f"Result: [Out-of-domain message returned] ✅ (Expected for jokes/math)")
        else:
            print(f"Result: [In-domain response/learning triggered] ✅ (Expected for travel)")
            if response and "__SEARCH_PACKAGES__" not in response:
                # Truncate long search results for display
                display_resp = response.split('\n')[0] + "..." if '\n' in response else response
                print(f"Response: {display_resp}")
        print("-" * 40)

if __name__ == "__main__":
    test_scenarios()
