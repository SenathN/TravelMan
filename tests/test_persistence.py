import database
import engine

def test_persistence():
    database.initialise_db()
    
    q = "what is your favorite color?"
    a = "I like travel blue! ✈️"
    
    print(f"Teaching: {q} -> {a}")
    engine.learn_response(q, a)
    
    print("Checking if learned immediately...")
    res1 = engine.process_user_input(q)
    assert res1 == a
    
    print("Simulating restart and checking again...")
    # engine state is stateless, so we just check the DB again
    res2 = engine.get_learned_answer(q)
    assert res2 == a
    print("Persistence check passed!")

if __name__ == "__main__":
    test_persistence()
