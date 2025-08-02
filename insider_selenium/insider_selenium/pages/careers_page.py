from selenium.webdriver.common.by import By
from .base_page import BasePage

class CareersPage(BasePage):
    PAGE_HEADING = (By.TAG_NAME, "h1")

    def verify_sections(self):
        heading = self.find(self.PAGE_HEADING)
        assert heading and heading.text.strip(), "Careers page heading not found!"

    def go_to_quality_assurance(self):
        self.go_to("https://useinsider.com/careers/quality-assurance/")
