from selenium.webdriver.support import expected_conditions as EC
from .base_page import BasePage

class JobDetailPage(BasePage):
    def verify_application_form_displayed(self):
        # 1) If it opened in a new tab/window, switch to it
        handles = self.driver.window_handles
        if len(handles) > 1:
            self.driver.switch_to.window(handles[-1])

        # 2) Wait until the URL clearly contains "lever.co"
        self.wait.until(EC.url_contains("lever.co"))
        # At this point we know we've landed on the external application page
