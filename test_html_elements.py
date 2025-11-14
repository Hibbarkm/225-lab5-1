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

    def test_add_and_delete_part(self):
        driver = self.driver
        driver.get(BASE_URL + "/")

        # Wait for the table to load
        self.wait.until(EC.presence_of_element_located((By.ID, "parts-table")))

        # Click Add Part link
        add_link = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Add Part")))
        add_link.click()

        # Fill the form and submit
        self.wait.until(EC.presence_of_element_located((By.ID, "add-part-form")))
        driver.find_element(By.ID, "part_name").send_keys("TEST-UNIT-123")
        driver.find_element(By.ID, "quantity").send_keys("7")
        driver.find_element(By.ID, "location").send_keys("UnitTestShelf")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        # Wait for the new row to appear
        rows = self.wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#parts-table tbody tr"))
        )
        found = any("TEST-UNIT-123" in r.text for r in rows)
        self.assertTrue(found)

        # Delete the part
        delete_button = None
        for r in rows:
            if "TEST-UNIT-123" in r.text:
                delete_button = r.find_element(By.CSS_SELECTOR, "button[type='submit']")
                break
        self.assertIsNotNone(delete_button)
        delete_button.click()

        # Wait for row to be removed
        rows_after = self.wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "#parts-table tbody tr"))
        )
        found_after = any("TEST-UNIT-123" in r.text for r in rows_after)
        self.assertFalse(found_after)

if __name__ == '__main__':
    unittest.main()

