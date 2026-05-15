"""
cli.py — Command-line interface for TravelMate
Fallback for testing in headless environments without GUI display.
"""

import database
import engine

# Initialize database
database.initialise_db()

print("=" * 60)
print("✈️ TravelMate — AI Travel Assistant (CLI Mode)")
print("=" * 60)
print("Type 'quit' or 'exit' to end the conversation.\n")

while True:
    user_input = input("You: ").strip()

    if user_input.lower() in ['quit', 'exit', 'bye']:
        print("TravelMate: Goodbye! Have a wonderful trip! ✈️\n")
        break

    if not user_input:
        continue

    response = engine.process_user_input(user_input)

    if response:
        print(f"TravelMate: {response}\n")
    else:
        # Learning mode
        print(f"TravelMate: 🤔 I don't know the answer to that.")
        answer = input("Teach me (what should I say?): ").strip()
        if answer:
            engine.learn_response(user_input, answer)
            print(f"TravelMate: Thanks! I've learned that.\n")
        else:
            print(f"TravelMate: Okay, I won't learn that one.\n")
