
import engine
import database

def test_longest_tours():
    database.initialise_db()
    print("Testing 'What are the longest night tours'")
    response = engine.process_user_input("What are the longest night tours")
    print(f"Response:\n{response}")
    
    if "European Explorer" in response:
        print("\nSUCCESS: Found the actual longest tour (13 days).")
    else:
        print("\nFAILURE: Did not find the actual longest tour.")

if __name__ == "__main__":
    test_longest_tours()
