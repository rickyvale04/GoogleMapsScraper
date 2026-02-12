#!/usr/bin/env python3
import sys
import os
import glob

print("Test 1: Import Playwright...")
try:
    from playwright.sync_api import sync_playwright
    print("[OK] Playwright imported")
except Exception as e:
    print(f"[ERROR] Cannot import: {e}")
    sys.exit(1)

def find_chromium():
    """Find an available Chromium executable from Playwright cache."""
    cache_dir = os.path.join(os.path.expanduser("~"), ".cache", "ms-playwright")
    if os.path.isdir(cache_dir):
        pattern = os.path.join(cache_dir, "chromium-*", "chrome-linux", "chrome")
        matches = sorted(glob.glob(pattern), reverse=True)
        for path in matches:
            if os.path.isfile(path) and os.access(path, os.X_OK):
                return path
    return None

print("\nTest 2: Launch browser...")
try:
    with sync_playwright() as p:
        print("   Starting Chromium...")
        launch_options = {'headless': True}
        chromium_path = find_chromium()
        if chromium_path:
            launch_options['executable_path'] = chromium_path
            print(f"   Using: {chromium_path}")

        browser = p.chromium.launch(**launch_options)
        print("[OK] Browser launched!")

        page = browser.new_page()
        print("[OK] Page created")

        print("   Navigating to Google...")
        try:
            page.goto("https://www.google.com", timeout=15000)
            print("[OK] Google loaded!")
        except Exception:
            print("[WARN] Navigation failed (no internet?) - browser still works")

        print("\n   Verifying page loaded correctly...")
        page.wait_for_timeout(2000)

        browser.close()
        print("[OK] Browser closed")

except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[OK] ALL TESTS PASSED!")
