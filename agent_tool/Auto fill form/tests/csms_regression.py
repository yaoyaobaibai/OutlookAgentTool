#!/usr/bin/env python3
"""
CSMS Create Proposal Group - Regression Test Script
====================================================
Test Objective: Document the existing CSMS automation flow for regression testing
Prerequisites: - Playwright installed (pip install playwright)
               - Chromium browser installed (playwright install chromium)
               - Access to CSMS test environment (csmstest.ncs.com.sg)
Expected Result: All 8 steps execute without errors
"""

import sys
import time
from typing import Optional


# ============================================================
# Skip Mechanism
# ============================================================
SKIP_REASON: Optional[str] = None

# Test data (dict-based, no pandas/excel dependency)
TEST_DATA = {
    "username": "testuser",
    "password": "testpass",
    "proposal_no": "P001234",
    "date_of_award": "07/22/2026",
    "pm_login_id": "john.doe",
    "currency_code": "SGD",
    "cust_ref_no": "CR-2026-001",
    "contract_value": "1500000.00",
}

# Key URLs
LOGIN_URL = "https://csmstest.ncs.com.sg/UAT/"
CREATE_PG_URL = "https://csmstest.ncs.com.sg/UAT/app/consol_cs/details_pg.aspx"

# Core selectors used across the 8 steps
SELECTORS = {
    "proposal_no": "#ctl00_ContentPlaceHolder1_txtProposalNo",
    "crm_info_btn": "#ctl00_ContentPlaceHolder1_btnInfo",
    "crm_loading": "#ctl00_ContentPlaceHolder1_upgProject",
    "date_of_award": "#ctl00_ContentPlaceHolder1_dtDateofAward_txtDate",
    "pm_search_btn": "#ctl00_ContentPlaceHolder1_ucEmpSearch_txtUserName",
    "pm_login_id": "#txtOAID",
    "pm_search_submit": 'input[type="submit"][value*="Search"]',
    "pm_result_row": "table tr:nth-child(2)",
    "pm_select_btn": 'input[type="submit"][value*="Select"]',
    "currency_code": "#ctl00_ContentPlaceHolder1_ddlSelPriceCurrCode",
    "cust_ref_no": "#ctl00_ContentPlaceHolder1_txtCustRefNo",
    "contract_value": "#ctl00_ContentPlaceHolder1_txtContractValue",
}

# Login fallback selectors (tried in order — first match wins)
LOGIN_USERNAME_SELECTORS = [
    'input[name="username"]',
    'input[name="userName"]',
    'input[id="username"]',
    'input[type="text"]',
]

LOGIN_PASSWORD_SELECTORS = [
    'input[name="password"]',
    'input[name="passwd"]',
    'input[id="password"]',
    'input[type="password"]',
]

LOGIN_SUBMIT_SELECTORS = [
    'input[type="submit"]',
    'button[type="submit"]',
    'button:has-text("Login")',
    'button:has-text("Sign In")',
    'input[value="Login"]',
    'input[value="Sign In"]',
]

# Module-level Playwright objects shared across tests
_playwright = None
_browser = None
_context = None
_page = None


# ============================================================
# Environment Check
# ============================================================

def check_environment() -> bool:
    """Check if Playwright is installed and target URL is reachable.

    Sets SKIP_REASON if either check fails.
    Returns True if the environment is usable, False otherwise.
    """
    global SKIP_REASON

    # Check 1: Playwright import
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        SKIP_REASON = (
            "Playwright is not installed.\n"
            "  Install: pip install playwright\n"
            "  Then:    playwright install chromium"
        )
        return False

    # Check 2: URL reachability (lightweight HEAD request)
    try:
        import urllib.request
        import urllib.error
        try:
            req = urllib.request.Request(LOGIN_URL, method="HEAD")
            urllib.request.urlopen(req, timeout=5)
        except urllib.error.URLError:
            SKIP_REASON = (
                f"Target URL {LOGIN_URL} is not reachable.\n"
                "  Check your network connection / VPN access to CSMS."
            )
            return False
        except Exception:
            # Timeouts, connection refused, etc.
            SKIP_REASON = (
                f"Could not connect to {LOGIN_URL}.\n"
                "  The server may be down or your network may be restricted."
            )
            return False
    except ImportError:
        pass  # urllib is stdlib — should never happen

    return True


# ============================================================
# Test Functions
# ============================================================

def test_browser_launch():
    """Step 1: Launch browser with Chrome channel, create context + page."""
    if SKIP_REASON:
        print(f"  SKIP: {SKIP_REASON}")
        return

    global _playwright, _browser, _context, _page

    from playwright.sync_api import sync_playwright

    _playwright = sync_playwright().start()

    # Try Chrome channel first; fall back to plain chromium
    try:
        _browser = _playwright.chromium.launch(channel="chrome", headless=False)
        print("  ✓ Browser launched with chrome channel")
    except Exception:
        _browser = _playwright.chromium.launch(headless=False)
        print("  ✓ Browser launched with chromium (chrome channel unavailable)")

    _context = _browser.new_context()
    _page = _context.new_page()

    assert _page is not None, "Page object should not be None"
    print("  ✓ Context and page created successfully")


def test_login():
    """Step 2: Navigate to login URL, fill username/password using fallback selectors."""
    if SKIP_REASON:
        print(f"  SKIP: {SKIP_REASON}")
        return

    global _page

    print(f"  Navigating to {LOGIN_URL}...")
    _page.goto(LOGIN_URL)
    _page.wait_for_load_state("networkidle")
    print("  ✓ Login page loaded")

    # --- Fill username (try selectors in order) ---
    username_filled = False
    for sel in LOGIN_USERNAME_SELECTORS:
        locator = _page.locator(sel).first
        if locator.count() > 0:
            locator.fill(TEST_DATA["username"])
            print(f"  ✓ Username filled (selector: {sel})")
            username_filled = True
            break

    if not username_filled:
        print("  ⚠  Username field not found — continuing")

    # --- Fill password (try selectors in order) ---
    password_filled = False
    for sel in LOGIN_PASSWORD_SELECTORS:
        locator = _page.locator(sel).first
        if locator.count() > 0:
            locator.fill(TEST_DATA["password"])
            print(f"  ✓ Password filled (selector: {sel})")
            password_filled = True
            break

    if not password_filled:
        print("  ⚠  Password field not found — continuing")

    # --- Click submit (try selectors in order) ---
    submit_clicked = False
    for sel in LOGIN_SUBMIT_SELECTORS:
        locator = _page.locator(sel).first
        if locator.count() > 0:
            locator.click()
            print(f"  ✓ Submit clicked (selector: {sel})")
            submit_clicked = True
            break

    if submit_clicked:
        _page.wait_for_load_state("networkidle")
        _page.wait_for_timeout(2000)
        print("  ✓ Login flow completed")
    else:
        print("  ⚠  Submit button not found — manual login needed")
        _page.wait_for_timeout(5000)


def test_navigate_to_create_pg():
    """Step 3: Navigate to Create PG page, wait for Proposal # field."""
    if SKIP_REASON:
        print(f"  SKIP: {SKIP_REASON}")
        return

    global _page

    print(f"  Navigating to {CREATE_PG_URL}...")
    _page.goto(CREATE_PG_URL)
    _page.wait_for_load_state("networkidle")
    print("  ✓ Create PG page loaded")

    # Wait for Proposal # field as confirmation
    proposal_locator = _page.locator(SELECTORS["proposal_no"])
    proposal_locator.wait_for(state="visible", timeout=15000)
    assert proposal_locator.count() > 0, "Proposal # field should be visible"
    print("  ✓ Proposal # field is visible — page is ready")


def test_proposal_and_crm():
    """Step 4: Fill Proposal #, click GET CRM INFO, wait for loading to complete."""
    if SKIP_REASON:
        print(f"  SKIP: {SKIP_REASON}")
        return

    global _page

    # --- Fill Proposal # ---
    elem = _page.locator(SELECTORS["proposal_no"])
    elem.wait_for(state="visible", timeout=5000)
    elem.fill("")
    elem.fill(TEST_DATA["proposal_no"])
    print(f"  ✓ Proposal # filled: {TEST_DATA['proposal_no']}")

    # --- Click GET CRM INFO ---
    crm_btn = _page.locator(SELECTORS["crm_info_btn"])
    crm_btn.wait_for(state="visible", timeout=5000)
    assert crm_btn.count() > 0, "CRM INFO button should exist"
    crm_btn.click()
    print("  ✓ GET CRM INFO button clicked")

    # --- Wait for CRM data loading indicator to appear then disappear ---
    print("  Waiting for CRM data to load...")
    try:
        _page.wait_for_selector(
            SELECTORS["crm_loading"], state="visible", timeout=5000
        )
        _page.wait_for_selector(
            SELECTORS["crm_loading"], state="hidden", timeout=15000
        )
        print("  ✓ CRM data loaded successfully")
    except Exception as e:
        print(f"  ⚠  CRM loading indicator not observed: {e}")
        _page.wait_for_timeout(3000)


def test_date_of_award():
    """Step 5: Fill Date of Award, trigger change event."""
    if SKIP_REASON:
        print(f"  SKIP: {SKIP_REASON}")
        return

    global _page

    date_input = _page.locator(SELECTORS["date_of_award"])
    date_input.wait_for(state="visible", timeout=5000)
    assert date_input.count() > 0, "Date of Award field should exist"

    date_input.fill("")
    date_input.fill(TEST_DATA["date_of_award"])
    print(f"  ✓ Date of Award filled: {TEST_DATA['date_of_award']}")

    # Trigger change event (ASP.NET requires this for postback)
    _page.evaluate(
        """() => {
            var elem = document.getElementById(
                'ctl00_ContentPlaceHolder1_dtDateofAward_txtDate'
            );
            if (elem) {
                elem.dispatchEvent(new Event('change', { bubbles: true }));
            }
        }"""
    )
    _page.wait_for_timeout(500)
    print("  ✓ Change event triggered")


def test_project_manager_popup():
    """Step 6: Click PM search, handle popup, search and select user."""
    if SKIP_REASON:
        print(f"  SKIP: {SKIP_REASON}")
        return

    global _page

    pm_search_btn = _page.locator(SELECTORS["pm_search_btn"]).first
    pm_search_btn.wait_for(state="visible", timeout=5000)
    assert pm_search_btn.count() > 0, "PM search button should exist"

    pm_search_btn.click()
    _page.wait_for_timeout(2000)
    print("  ✓ PM search button clicked")

    # --- Detect popup (try popup event, then iframe, then main page) ---
    popup = None

    # Strategy 1: wait_for_event('popup')
    try:
        popup = _page.wait_for_event("popup", timeout=3000)
        print("  ✓ Popup window detected")
    except Exception:
        pass

    # Strategy 2: check for iframe
    if popup is None:
        try:
            iframe = _page.frame_locator(
                'iframe[name*="popup"], iframe[id*="popup"]'
            ).first
            # Verify iframe has content
            if iframe.locator("body").count() > 0:
                popup = iframe
                print("  ✓ Popup detected (iframe)")
        except Exception:
            pass

    # Strategy 3: fall back to main page
    if popup is None:
        print("  ⚠  No popup/iframe detected — searching in main page")
        popup = _page

    popup.wait_for_load_state("networkidle")

    # --- Fill LoginID ---
    login_input = popup.locator(SELECTORS["pm_login_id"])
    if login_input.count() > 0:
        login_input.fill(TEST_DATA["pm_login_id"])
        print(f"  ✓ LoginID filled: {TEST_DATA['pm_login_id']}")

        # --- Click Search ---
        search_btn = popup.locator(SELECTORS["pm_search_submit"]).first
        search_btn.wait_for(state="visible", timeout=5000)
        assert search_btn.count() > 0, "Search button should exist"
        search_btn.click()
        print("  ✓ Search button clicked")
        popup.wait_for_timeout(2000)

        # --- Select first result row ---
        first_row = popup.locator(SELECTORS["pm_result_row"]).first
        first_row.wait_for(state="visible", timeout=5000)
        assert first_row.count() > 0, "Search results should appear"
        first_row.click()
        print("  ✓ First search result selected")

        # --- Click Select ---
        select_btn = popup.locator(SELECTORS["pm_select_btn"]).first
        select_btn.wait_for(state="visible", timeout=5000)
        assert select_btn.count() > 0, "Select button should exist"
        select_btn.click()
        print("  ✓ Select button clicked")
        _page.wait_for_timeout(1000)
    else:
        print("  ⚠  LoginID input (#txtOAID) not found in popup")


def test_currency_dropdown():
    """Step 7: Select currency from dropdown with select_option() + __doPostBack."""
    if SKIP_REASON:
        print(f"  SKIP: {SKIP_REASON}")
        return

    global _page

    currency_locator = _page.locator(SELECTORS["currency_code"])
    currency_locator.wait_for(state="visible", timeout=5000)
    assert currency_locator.count() > 0, "Currency dropdown should exist"

    # Use Playwright select_option for the <select> element
    currency_locator.select_option(TEST_DATA["currency_code"])
    print(f"  ✓ Currency selected: {TEST_DATA['currency_code']}")

    # Trigger ASP.NET __doPostBack via JavaScript
    result = _page.evaluate(
        """() => {
            var elem = document.getElementById(
                'ctl00_ContentPlaceHolder1_ddlSelPriceCurrCode'
            );
            if (!elem) return 'Element not found';

            var oldVal = elem.value;
            console.log('Dropdown value:', oldVal);

            // Dispatch change event
            var changeEvent = new Event('change', {
                bubbles: true,
                cancelable: true
            });
            elem.dispatchEvent(changeEvent);

            // Call __doPostBack if available (ASP.NET pattern)
            if (typeof __doPostBack === 'function') {
                setTimeout(function() {
                    __doPostBack(elem.id, '');
                }, 100);
                return '__doPostBack scheduled';
            }
            return 'change event dispatched (no __doPostBack)';
        }"""
    )
    print(f"    JS result: {result}")

    _page.wait_for_load_state("networkidle")
    _page.wait_for_timeout(1000)
    print("  ✓ Currency dropdown postback handled")


def test_other_fields():
    """Step 8: Fill remaining input/textarea fields using fill()."""
    if SKIP_REASON:
        print(f"  SKIP: {SKIP_REASON}")
        return

    global _page

    # --- Cust Ref No ---
    cust_ref_locator = _page.locator(SELECTORS["cust_ref_no"])
    if cust_ref_locator.count() > 0:
        cust_ref_locator.wait_for(state="visible", timeout=5000)
        cust_ref_locator.fill("")
        cust_ref_locator.fill(TEST_DATA["cust_ref_no"])
        print(f"  ✓ Cust Ref No filled: {TEST_DATA['cust_ref_no']}")
    else:
        print("  ⚠  Cust Ref No field not found")

    # --- Contract Value ---
    contract_locator = _page.locator(SELECTORS["contract_value"])
    if contract_locator.count() > 0:
        contract_locator.wait_for(state="visible", timeout=5000)
        contract_locator.fill("")
        contract_locator.fill(TEST_DATA["contract_value"])
        print(f"  ✓ Contract Value filled: {TEST_DATA['contract_value']}")
    else:
        print("  ⚠  Contract Value field not found")

    _page.wait_for_timeout(200)


# ============================================================
# Orchestration
# ============================================================

def cleanup():
    """Close browser and stop Playwright."""
    global _playwright, _browser, _context, _page
    try:
        if _context:
            _context.close()
    except Exception:
        pass
    try:
        if _browser:
            _browser.close()
    except Exception:
        pass
    try:
        if _playwright:
            _playwright.stop()
    except Exception:
        pass


def main():
    """Run all test functions sequentially and report results.

    Exit code: 0 if all pass, 1 if any fail.
    """
    print("=" * 60)
    print("  CSMS Create Proposal Group - Regression Tests")
    print("=" * 60)

    # --- Environment check ---
    env_ok = check_environment()
    if not env_ok:
        print(f"\n  Environment check FAILED:\n  {SKIP_REASON}")
        print("  All tests will be skipped.\n")

    # Test registry: (display_name, function)
    tests = [
        ("test_browser_launch", test_browser_launch),
        ("test_login", test_login),
        ("test_navigate_to_create_pg", test_navigate_to_create_pg),
        ("test_proposal_and_crm", test_proposal_and_crm),
        ("test_date_of_award", test_date_of_award),
        ("test_project_manager_popup", test_project_manager_popup),
        ("test_currency_dropdown", test_currency_dropdown),
        ("test_other_fields", test_other_fields),
    ]

    passed = 0
    failed = 0
    skipped = 0

    for name, func in tests:
        print(f"\n[{name}]")

        if SKIP_REASON:
            print(f"  SKIP: {SKIP_REASON}")
            skipped += 1
            continue

        try:
            func()
            passed += 1
            print(f"  RESULT: PASS")
        except Exception as e:
            failed += 1
            import traceback
            print(f"  RESULT: FAIL — {e}")
            print(f"  {traceback.format_exc()}")

        print(f"  {'-' * 40}")

    # --- Summary ---
    print(f"\n{'=' * 60}")
    print(f"  Results:  {passed} passed, {failed} failed, {skipped} skipped")
    print(f"{'=' * 60}")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    finally:
        cleanup()
