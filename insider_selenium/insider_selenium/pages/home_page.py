from selenium.webdriver.common.by import By
from .base_page import BasePage

class HomePage(BasePage):
    

    def open(self):
        self.go_to("https://useinsider.com/")

    def navigate_to_careers(self):
        self.go_to("https://useinsider.com/careers/")
