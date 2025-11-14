"""
Selenium test that verifies basic add/delete flows for the parts inventory.

This test expects the app to be running and reachable at BASE_URL (default http://localhost:5000).
If you're using a Selenium Grid, set SELENIUM_REMOTE_URL to point at the remote webdriver
(e.g., http://selenium:4444/wd/hub) and the test will use Remote WebDriver. Otherwise it will
attempt to use a local ChromeDriver (you may need it installed in your CI image).
"""

import os
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
SELENIUM_REMOTE = os.environ.get('SELENIUM_REMOTE_URL')  # optional

class PartsUITest(unittest.TestCase):
    def setUp(self):
        if SELENIUM_REMOTE:
            from selenium.webdriver import Remote
            caps = {"browserName": "chrome"}
            self.driver = Remote(command_executor=SELENIUM_REMOTE, desired_capabilities=caps)
        else:
            # Try local Chrome
            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            self.driver = webdriver.Chrome(options=options)

        self.driver.set_window_size(1280, 800)
        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

    def test_add_and_delete_part(self):
        driver = self.driver
        driver.get(BASE_URL + "/")
        # Wait until page loads and table exists
        self.wait.until(EC.presence_of_element_located((By.ID, "parts-table")))

        # Click "Add Part"
        add_link = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Add Part")))
        add_link.click()

        # On add page: fill form
        self.wait.until(EC.presence_of_element_located((By.ID, "add-part-form")))
        driver.find_element(By.ID, "part_name").send_keys("TEST-UNIT-123")
        driver.find_element(By.ID, "quantity").send_keys("7")
        driver.find_element(By.ID, "location").send_keys("UnitTestShelf")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Back on index — wait for new entry to appear in table
        self.wait.until(EC.presence_of_element_located((By.ID, "parts-table")))
        # small pause to allow DB commit / render
        time.sleep(1)

        # Assert that a row with the name exists
        rows = driver.find_elements(By.CSS_SELECTOR, "#parts-table tbody tr")
        texts = [r.text for r in rows]
        found = any("TEST-UNIT-123" in t for t in texts)
        self.assertTrue(found, f"Added part not found in table. Table contents: {texts}")

        # Find the delete button for the row containing our test item and click it
        delete_button = None
        for r in rows:
            if "TEST-UNIT-123" in r.text:
                delete_button = r.find_element(By.CSS_SELECTOR, "button[type='submit']")
                break
        self.assertIsNotNone(delete_button, "Delete button for test row not found")
        delete_button.click()

        # Confirm we return to index and the item is gone
        time.sleep(1)
        rows_after = driver.find_elements(By.CSS_SELECTOR, "#parts-table tbody tr")
        texts_after = [r.text for r in rows_after]
        found_after = any("TEST-UNIT-123" in t for t in texts_after)
        self.assertFalse(found_after, f"Deleted part still present. Table contents: {texts_after}")

if __name__ == '__main__':
    unittest.main()
