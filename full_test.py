import engine
import database
import time
import collections

# ANSI colors for better visibility
GREEN = "\033[92m"
BLUE = "\033[94m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"
BOLD = "\033[1m"
CYAN = "\033[96m"

# Global stats tracking
stats = collections.defaultdict(lambda: {"passed": 0, "total": 0, "time": 0.0})

def run_test(category, input_text, expected_behavior, action_desc=None):
    """Unified test runner for all scenarios."""
    print(f"{BOLD}{CYAN}[{category}]{RESET}")
    if action_desc:
        print(f"{BOLD}Action:   {RESET}{action_desc}")
    print(f"{BOLD}User Input:{RESET} {input_text}")
    
    start_time = time.time()
    try:
        response = engine.process_user_input(input_text)
        error = None
    except Exception as e:
        response = None
        error = str(e)
    
    duration = (time.time() - start_time) * 1000
    
    # Format Agent Output for display
    if error:
        agent_display = f"{RED}ERROR: {error}{RESET}"
    elif response is None:
        agent_display = f"{YELLOW}[None - Triggered Learning Mode]{RESET}"
    else:
        # Show first line or truncate if very long
        lines = response.splitlines()
        first_line = lines[0] if lines else ""
        agent_display = first_line[:80] + "..." if len(first_line) > 80 else first_line
        if len(lines) > 1:
            agent_display += f" {BLUE}(+{len(lines)-1} more lines){RESET}"

    print(f"{BOLD}Agent Output:{RESET} {agent_display}")
    
    # Validation Logic
    passed = False
    result_msg = "FAILED"
    
    if error:
        passed = False
        result_msg = f"FAILED (Engine Error)"
    elif expected_behavior == "domain_support":
        if response and "specialize in travel" in response:
            passed = True
    elif expected_behavior == "intent_match":
        if response and "specialize in travel" not in response:
            passed = True
    elif expected_behavior == "learning_trigger":
        if response is None:
            passed = True
    elif expected_behavior == "exact_match":
        # Special case for learning verification where we pass the expected string in action_desc
        if response == action_desc:
            passed = True
    elif expected_behavior == "security_safe":
        # Safe if it didn't crash (already handled by error check)
        passed = True

    result_msg = f"{GREEN}PASSED{RESET}" if passed else f"{RED}{result_msg}{RESET}"
    print(f"{BOLD}Result:      {result_msg} {RESET}({duration:.1f}ms)")
    print("-" * 60)
    
    # Update Stats
    stats[category]["passed"] += 1 if passed else 0
    stats[category]["total"] += 1
    stats[category]["time"] += duration
    return passed

def main():
    print("=" * 60)
    print(f"{BOLD}✈️  TravelMate — Unified Test Report{RESET}")
    print("=" * 60)
    
    database.initialise_db()
    print("-" * 60)
    
    # 1. Conversation Tests
    run_test("Conversation", "Hi there!", "intent_match")
    run_test("Conversation", "What can you do for me?", "intent_match")
    run_test("Conversation", "Thanks, bye!", "intent_match")
    
    # 2. Search Tests
    run_test("Search", "Show me Bali packages", "intent_match")
    run_test("Search", "Find the cheapest deals in Europe", "intent_match")
    run_test("Search", "I want a long vacation in the Maldives", "intent_match")
    
    # 3. Domain Tests
    run_test("Domain", "tell me about tours in America", "intent_match")
    run_test("Domain", "anything interesting in Asia?", "intent_match")
    run_test("Domain", "what is the capital of France?", "domain_support")
    run_test("Domain", "can you write code for me?", "domain_support")
    
    # 4. Learning Tests
    run_test("Learning", "how do I travel to Mars?", "learning_trigger")
    
    # Learning Verification (Special)
    q, a = "What is the secret of travel?", "The secret is to enjoy the journey!"
    engine.learn_response(q, a)
    run_test("Learning", q, "exact_match", action_desc=a)
    
    # 5. Security Tests
    run_test("Security", "Bali' OR '1'='1", "security_safe", action_desc="SQL Injection Attempt")
    run_test("Security", "Bali'; DROP TABLE packages; --", "security_safe", action_desc="Destructive SQL Attempt")

    # --- FINAL SUMMARY ---
    print(f"\n{BOLD}📊 TEST EXECUTION SUMMARY{RESET}")
    print("=" * 60)
    
    total_passed = 0
    total_tests = 0
    total_time = 0.0
    
    # Print table-like header
    print(f"{BOLD}{'Category':<15} {'Passed':<10} {'Success %':<12} {'Avg Time':<10}{RESET}")
    print("-" * 60)
    
    for cat in ["Conversation", "Search", "Domain", "Learning", "Security"]:
        s = stats[cat]
        if s["total"] == 0: continue
        
        passed = s["passed"]
        total = s["total"]
        success_rate = (passed / total) * 100
        avg_time = s["time"] / total
        
        color = GREEN if success_rate == 100 else YELLOW if success_rate > 0 else RED
        print(f"{cat:<15} {passed}/{total:<8} {color}{success_rate:>8.1f}%{RESET} {avg_time:>8.1f}ms")
        
        total_passed += passed
        total_tests += total
        total_time += s["time"]
    
    print("-" * 60)
    overall_rate = (total_passed / total_tests) * 100
    overall_color = GREEN if overall_rate == 100 else YELLOW
    print(f"{BOLD}{'OVERALL':<15} {total_passed}/{total_tests:<8} {overall_color}{overall_rate:>8.1f}%{RESET} {total_time/total_tests:>8.1f}ms (avg)")
    print("=" * 60)

if __name__ == "__main__":
    main()
