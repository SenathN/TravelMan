
import database
import engine
import re
import json

def run_audit():
    database.initialise_db()
    
    results = []

    def log_test(test_id, area, test_case, expected_desc, result_data):
        status = "PASS" if result_data['passed'] else "FAIL"
        results.append({
            "id": test_id,
            "area": area,
            "case": test_case,
            "expected": expected_desc,
            "status": status,
            "output": str(result_data['output']),
            "notes": result_data.get('notes', '')
        })
        print(f"[{status}] {test_id}: {test_case}")

    print("--- Starting Core Query Engine Audit ---")

    # --- GEOGRAPHICAL AREA FILTERING ---
    
    # G1: Exact match
    resp = engine.process_user_input("Show me Bali tours")
    passed = resp is not None and "Bali Bliss" in resp
    log_test("G1", "Geo Filtering", "Exact match: 'Bali'", "Returns Bali packages", {"passed": passed, "output": resp})

    # G2: Partial match
    resp = engine.process_user_input("packages in Indo")
    passed = resp is not None and "Bali Bliss" in resp
    log_test("G2", "Geo Filtering", "Partial match: 'Indo'", "Returns Bali (Indonesia) packages", {"passed": passed, "output": resp})

    # G3: Continent match
    resp = engine.process_user_input("tours in Europe")
    passed = resp is not None and ("European Explorer" in resp or "Swiss Alps" in resp)
    log_test("G3", "Geo Filtering", "Continent match: 'Europe'", "Returns European packages", {"passed": passed, "output": resp})

    # G4: Invalid input
    resp = engine.process_user_input("Show me packages in Zarnonia")
    passed = resp is not None and "couldn't find any packages" in resp.lower()
    log_test("G4", "Geo Filtering", "Invalid input: 'Zarnonia'", "Returns not found message", {"passed": passed, "output": resp})


    # --- DAY/LIGHT COUNT SORTING ---
    
    # D1: Sort Ascending
    resp = engine.process_user_input("shortest tours")
    if resp:
        days = [int(d) for d in re.findall(r'⏱.*?(\d+)\s+day', resp, re.DOTALL)]
        passed = len(days) > 1 and all(days[i] <= days[i+1] for i in range(len(days)-1))
        notes = f"Days extracted: {days}"
    else:
        passed = False
        notes = "No response from engine"
    log_test("D1", "Day/Light Count", "Sort Ascending: 'shortest'", "Results sorted by duration asc", {"passed": passed, "output": resp, "notes": notes})

    # D2: Sort Descending
    resp = engine.process_user_input("longest tours")
    if resp:
        days = [int(d) for d in re.findall(r'⏱.*?(\d+)\s+day', resp, re.DOTALL)]
        passed = len(days) > 1 and all(days[i] >= days[i+1] for i in range(len(days)-1))
        notes = f"Days extracted: {days}"
    else:
        passed = False
        notes = "No response from engine"
    log_test("D2", "Day/Light Count", "Sort Descending: 'longest'", "Results sorted by duration desc", {"passed": passed, "output": resp, "notes": notes})

    # D3: Cross-dataset comparison (GAP)
    resp = engine.process_user_input("compare Bali Bliss and Maldives Dream Escape")
    if resp:
        passed = "Bali Bliss" in resp and "Maldives Dream Escape" in resp and "comparison" in resp.lower()
    else:
        passed = False
    log_test("D3", "Day/Light Count", "Cross-dataset comparison", "Returns comparative data", {"passed": passed, "output": resp, "notes": "Engine currently lacks explicit multi-item comparison logic."})


    # --- PRICE-RELATED OPERATIONS ---
    
    # P1: Price Sort Ascending
    resp = engine.process_user_input("cheapest packages")
    if resp:
        prices = [float(p) for p in re.findall(r'💰\s+\$(\d+\.?\d*)', resp)]
        passed = len(prices) > 1 and all(prices[i] <= prices[i+1] for i in range(len(prices)-1))
        notes = f"Prices extracted: {prices}"
    else:
        passed = False
        notes = "No response from engine"
    log_test("P1", "Price Sorting", "Sort Ascending: 'cheapest'", "Results sorted by price asc", {"passed": passed, "output": resp, "notes": notes})

    # P2: Price Sort Descending
    resp = engine.process_user_input("expensive tours")
    if resp:
        prices = [float(p) for p in re.findall(r'💰\s+\$(\d+\.?\d*)', resp)]
        passed = len(prices) > 1 and all(prices[i] >= prices[i+1] for i in range(len(prices)-1))
        notes = f"Prices extracted: {prices}"
    else:
        passed = False
        notes = "No response from engine"
    log_test("P2", "Price Sorting", "Sort Descending: 'expensive'", "Results sorted by price desc", {"passed": passed, "output": resp, "notes": notes})

    # P3: Price Analysis - Percentage difference (GAP)
    resp = engine.process_user_input("what is the price difference between Bali and Maldives?")
    if resp:
        passed = "%" in resp or "percent" in resp.lower()
    else:
        passed = False
    log_test("P3", "Price Analysis", "Percentage difference", "Returns % difference calculation", {"passed": passed, "output": resp, "notes": "Engine currently lacks price variance calculation logic."})

    # P4: Price Analysis - Absolute variance (GAP)
    resp = engine.process_user_input("price variance of packages")
    if resp:
        passed = "variance" in resp.lower() or "difference" in resp.lower()
    else:
        passed = False
    log_test("P4", "Price Analysis", "Absolute variance", "Returns absolute variance analysis", {"passed": passed, "output": resp, "notes": "Engine currently lacks variance analysis."})

    # P5: Range filtering (GAP)
    resp = engine.process_user_input("packages under $1000")
    if resp:
        prices = [float(p) for p in re.findall(r'💰\s+\$(\d+\.?\d*)', resp)]
        passed = all(p < 1000 for p in prices) if prices else False
    else:
        passed = False
    log_test("P5", "Price Analysis", "Range filtering: 'under $1000'", "Only returns packages < $1000", {"passed": passed, "output": resp, "notes": "Engine currently lacks numerical range filtering logic."})


    # --- GENERIC QUERY METHODS ---
    
    # Q1: Full-text search
    resp = engine.process_user_input("show me beach tours")
    passed = resp is not None and "beach" in resp.lower()
    log_test("Q1", "Generic Query", "Full-text search: 'beach'", "Returns packages with 'beach' in description", {"passed": passed, "output": resp})

    # Q2: Combined multi-parameter
    resp = engine.process_user_input("cheap Asia tours")
    if resp:
        prices = [float(p) for p in re.findall(r'💰\s+\$(\d+\.?\d*)', resp)]
        is_asia = "Bali Bliss" in resp or "Maldives" in resp or "Thailand" in resp
        is_sorted = len(prices) > 1 and all(prices[i] <= prices[i+1] for i in range(len(prices)-1))
        passed = is_asia and is_sorted
        notes = f"Prices: {prices}"
    else:
        passed = False
        notes = "No response from engine"
    log_test("Q2", "Generic Query", "Multi-parameter: 'cheap Asia tours'", "Filters by Asia AND sorts by price asc", {"passed": passed, "output": resp, "notes": notes})

    # Q3: Pagination
    resp = engine.process_user_input("show all packages")
    passed = resp is not None and "more" in resp.lower() and "Contact us for details" in resp
    log_test("Q3", "Generic Query", "Pagination", "Shows top results and mentions remaining", {"passed": passed, "output": resp})


    # --- COMPILE REPORT ---
    print("\n--- Audit Summary Report ---")
    summary = {
        "total": len(results),
        "passed": len([r for r in results if r['status'] == "PASS"]),
        "failed": len([r for r in results if r['status'] == "FAIL"]),
        "results": results
    }
    
    with open("audit_report.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print(f"Tests Run: {summary['total']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print("\nDetailed results saved to audit_report.json")

if __name__ == "__main__":
    run_audit()
