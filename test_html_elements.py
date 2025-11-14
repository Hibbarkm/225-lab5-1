import os
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

BASE_URL = os.environ.get('BASE_URL', 'http://localhost:5000')
SELENIUM_REMOTE = os.environ.get('SELENIUM_REMOTE_URL')

class PartsUITest(unittest.TestCase):
    def setUp(self):
        if SELENIUM_REMOTE:
            from selenium.webdriver import Remote
            caps = {"browserName": "chrome"}
            self.driver = Remote(command_executor=SELENIUM_REMOTE, desired_capabilities=caps)
        else:
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
        self.wait.until(EC.presence_of_element_located((By.ID, "parts-table")))

        add_link = self.wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Add Part")))
        add_link.click()

        self.wait.until(EC.presence_of_element_located((By.ID, "add-part-form")))
        driver.find_element(By.ID, "part_name").send_keys("TEST-UNIT-123")
        driver.find_element(By.ID, "quantity").send_keys("7")
        driver.find_element(By.ID, "location").send_keys("UnitTestShelf")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        time.sleep(1)
        rows = driver.find_elements(By.CSS_SELECTOR, "#parts-table tbody tr")
        texts = [r.text for r in rows]
        found = any("TEST-UNIT-123" in t for t in texts)
        self.assertTrue(found)

        delete_button = None
        for r in rows:
            if "TEST-UNIT-123" in r.text:
                delete_button = r.find_element(By.CSS_SELECTOR, "button[type='submit']")
                break
        self.assertIsNotNone(delete_button)
        delete_button.click()

        time.sleep(1)
        rows_after = driver.find_elements(By.CSS_SELECTOR, "#parts-table tbody tr")
        texts_after = [r.text for r in rows_after]
        found_after = any("TEST-UNIT-123" in t for t in texts_after)
        self.assertFalse(found_after)

if __name__ == '__main__':
    unittest.main()
