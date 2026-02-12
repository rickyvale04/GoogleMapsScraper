#!/usr/bin/env python3
import sys

print("🧪 Test 1: Import Playwright...")
try:
    from playwright.sync_api import sync_playwright
    print("✅ Playwright imported")
except Exception as e:
    print(f"❌ Cannot import: {e}")
    sys.exit(1)

print("\n🧪 Test 2: Launch browser...")
try:
    with sync_playwright() as p:
        print("   Starting Chromium...")
        browser = p.chromium.launch(
            headless=True,
        )
        print("✅ Browser launched!")
        
        page = browser.new_page()
        print("✅ Page created")
        
        print("   Navigating to Google...")
        page.goto("https://www.google.com", timeout=30000)
        print("✅ Google loaded!")
        
        print("\n⏸️  Verifying page loaded correctly...")
        page.wait_for_timeout(2000)
        
        browser.close()
        print("✅ Browser closed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n✅ ALL TESTS PASSED!")

