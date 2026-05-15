"""Quick test of the engine without interactive input."""
import database
import engine

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
    response = engine.process_user_input(inp)
    if response:
        print(f"Bot:  {response}\n")
    else:
        print(f"Bot:  [Unknown - would trigger learning]\n")
