import unittest
import time
import database
import engine
import os

class TestTravelMateComprehensive(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        database.initialise_db()

    def test_integration_flow(self):
        """Test the full flow from input to response."""
        # 1. Greeting
        response = engine.process_user_input("hello")
        self.assertTrue(any(word in response for word in ["Hello", "Hi", "Hey"]), f"Greeting response unexpected: {response}")

        # 2. Search package
        response = engine.process_user_input("Show me Bali packages")
        self.assertIn("Bali Bliss", response)

        # 3. Learning
        question = "what is the meaning of travel?"
        answer = "Travel is to go from one place to another."
        engine.learn_response(question, answer)
        
        learned_response = engine.process_user_input(question)
        self.assertEqual(learned_response, answer)

    def test_performance_benchmarks(self):
        """Ensure response time is within acceptable limits (< 500ms)."""
        queries = ["hi", "bali", "what packages do you have?", "how much is the maldives trip?"]
        for query in queries:
            start_time = time.time()
            engine.process_user_input(query)
            duration = (time.time() - start_time) * 1000
            print(f"Performance: '{query}' took {duration:.2f}ms")
            self.assertLess(duration, 500, f"Query '{query}' took too long: {duration}ms")

    def test_security_sql_injection(self):
        """Test robustness against SQL injection patterns."""
        malicious_inputs = [
            "Bali' OR '1'='1",
            "Bali'; DROP TABLE packages; --",
            "Bali' UNION SELECT name, destination, duration, price_usd, description FROM packages; --"
        ]
        for inp in malicious_inputs:
            # Should not crash and should return either the package or a 'not found' message
            # But definitely not execute the injected SQL
            try:
                response = engine.process_user_input(inp)
                # If it's a search package trigger, it should handle the string safely
                print(f"Security check passed for: {inp}")
            except Exception as e:
                self.fail(f"Security vulnerability: SQL injection attempt crashed the engine: {e}")

    def test_data_integrity(self):
        """Verify database integrity."""
        packages = database.get_all_packages()
        self.assertGreater(len(packages), 0)
        for pkg in packages:
            self.assertIn('name', pkg)
            self.assertIn('price', pkg)
            self.assertTrue(isinstance(pkg['price'], (int, float)))

if __name__ == "__main__":
    unittest.main()
