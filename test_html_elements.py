import os
import unittest
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.environ.get('BASE_URL', 'http://flask-dev-service:5000')


class PartsUITest(unittest.TestCase):
    def setUp(self):
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.driver.set_window_size(1280, 800)
        self.wait = WebDriverWait(self.driver, 10)

    def tearDown(self):
        if hasattr(self, 'driver'):
            self.driver.quit()

    # ---------------------------------------------------
    # TEST 1 — Add Part + Delete Part (you already had)
    # ---------------------------------------------------
    def test_add_and_delete_part(self):
        driver = self.driver
        driver.get(BASE_URL + "/")

        # Wait for table
        self.wait.until(EC.presence_of_element_located((By.ID, "parts-table")))

        # Go to Add Part page
        self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Add Part"))).click()

        # Fill form
        self.wait.until(EC.presence_of_element_located((By.ID, "add-part-form")))
        driver.find_element(By.ID, "part_name").send_keys("TEST-UNIT-123")
        driver.find_element(By.ID, "quantity").send_keys("7")
        driver.find_element(By.ID, "location").send_keys("UnitTestShelf")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Verify row exists
        rows = self.wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#parts-table tbody tr"))
        )
        self.assertTrue(any("TEST-UNIT-123" in r.text for r in rows))

        # Delete
        for r in rows:
            if "TEST-UNIT-123" in r.text:
                r.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
                break

        # Verify row removed
        rows_after = self.wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#parts-table tbody tr"))
        )
        self.assertFalse(any("TEST-UNIT-123" in r.text for r in rows_after))

    # ---------------------------------------------------
    # TEST 2 — Homepage Loads and Elements Are Present
    # ---------------------------------------------------
    def test_homepage_loads(self):
        driver = self.driver
        driver.get(BASE_URL + "/")

        # Page loads
        header = self.wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        )
        self.assertIn("Parts", header.text)

        # Table exists
        table = self.wait.until(
            EC.presence_of_element_located((By.ID, "parts-table"))
        )
        self.assertIsNotNone(table)

    # ---------------------------------------------------
    # TEST 3 — Add Part Validation (should reject empty form)
    # ---------------------------------------------------
    def test_add_part_validation(self):
        driver = self.driver
        driver.get(BASE_URL + "/add")

        self.wait.until(EC.presence_of_element_located((By.ID, "add-part-form")))

        # Submit empty form
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Check that the page shows validation error
        error = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "error-message"))
        )
        self.assertIn("required", error.text.lower())

    # ---------------------------------------------------
    # TEST 4 — Prevent Duplicate Part Names
    # ---------------------------------------------------
    def test_duplicate_part_prevented(self):
        driver = self.driver

        # Add first part
        driver.get(BASE_URL + "/add")
        self.wait.until(EC.presence_of_element_located((By.ID, "add-part-form")))
        driver.find_element(By.ID, "part_name").send_keys("DUPLICATE_TEST")
        driver.find_element(By.ID, "quantity").send_keys("5")
        driver.find_element(By.ID, "location").send_keys("Shelf1")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Try adding the **same name again**
        driver.get(BASE_URL + "/add")
        self.wait.until(EC.presence_of_element_located((By.ID, "add-part-form")))
        driver.find_element(By.ID, "part_name").send_keys("DUPLICATE_TEST")
        driver.find_element(By.ID, "quantity").send_keys("3")
        driver.find_element(By.ID, "location").send_keys("Shelf2")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Look for duplicate warning
        error = self.wait.until(
            EC.presence_of_element_located((By.CLASS_NAME, "error-message"))
        )
        self.assertIn("already exists", error.text.lower())

    # ---------------------------------------------------
    # TEST 5 — Search Filter (if search bar exists)
    # ---------------------------------------------------
    def test_search_filter(self):
        driver = self.driver

        driver.get(BASE_URL + "/")

        # If no search bar, skip test
        try:
            search = self.wait.until(
                EC.presence_of_element_located((By.ID, "search"))
            )
        except:
            self.skipTest("Search bar not implemented yet.")

        # Type text into search
        search.send_keys("engine")

        # Table updates
        rows = self.wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#parts-table tbody tr"))
        )

        # Verify rows contain the filtered text
        for r in rows:
            self.assertIn("engine", r.text.lower())


if __name__ == '__main__':
    unittest.main()
