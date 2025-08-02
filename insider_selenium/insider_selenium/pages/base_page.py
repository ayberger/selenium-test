from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os
import time
from datetime import datetime

class BasePage:
    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)  # Reduced from 15 to 10 seconds

    def go_to(self, url: str):
        """Navigate to a URL with error handling"""
        try:
            self.driver.get(url)
            # Wait for page to load
            self.wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            print(f"Successfully navigated to: {url}")
        except Exception as e:
            self.take_screenshot(f"navigation_error_{url.split('/')[-1]}")
            raise Exception(f"Failed to navigate to {url}: {str(e)}")

    def find(self, locator, timeout=10):
        """Find element with custom timeout and error handling"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located(locator))
            return element
        except TimeoutException:
            self.take_screenshot(f"element_not_found_{locator[1]}")
            raise Exception(f"Element not found: {locator}")

    def find_clickable(self, locator, timeout=10):
        """Find clickable element with custom timeout"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable(locator))
            return element
        except TimeoutException:
            self.take_screenshot(f"element_not_clickable_{locator[1]}")
            raise Exception(f"Element not clickable: {locator}")

    def click(self, locator, timeout=10):
        """Click element with error handling and retry logic"""
        try:
            element = self.find_clickable(locator, timeout)
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", element)
            time.sleep(0.5)  # Brief pause after scrolling
            element.click()
        except Exception as e:
            # Try JavaScript click as fallback
            try:
                element = self.find(locator, timeout)
                self.driver.execute_script("arguments[0].click();", element)
                print("Used JavaScript click as fallback")
            except:
                self.take_screenshot(f"click_failed_{locator[1]}")
                raise Exception(f"Failed to click element {locator}: {str(e)}")

    def get_elements(self, locator, timeout=10):
        """Get multiple elements with error handling"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            elements = wait.until(EC.presence_of_all_elements_located(locator))
            return elements
        except TimeoutException:
            self.take_screenshot(f"elements_not_found_{locator[1]}")
            raise Exception(f"Elements not found: {locator}")

    def dismiss_cookie_banner(self):
        """Remove Insider's cookie consent banner and other overlays if present"""
        try:
            self.driver.execute_script("""
                // Remove cookie banner
                const banner = document.getElementById('wt-cli-cookie-banner');
                if (banner) { 
                    banner.remove(); 
                    console.log('Cookie banner removed');
                }
                
                // Remove any other overlay modals
                const overlays = document.querySelectorAll('[class*="modal"], [class*="overlay"], [class*="popup"], [class*="notification"]');
                overlays.forEach(overlay => {
                    if (overlay.style.display !== 'none') {
                        overlay.remove();
                        console.log('Overlay removed:', overlay.className);
                    }
                });
                
                // Remove fixed positioned elements that might interfere
                const fixedElements = document.querySelectorAll('[style*="position: fixed"], [style*="position:fixed"]');
                fixedElements.forEach(element => {
                    if (element.offsetHeight > 50) { // Only remove medium+ fixed elements
                        element.style.display = 'none';
                        console.log('Fixed element hidden:', element.className);
                    }
                });
                
                // Remove any ads or promotional banners
                const adSelectors = [
                    '[class*="ad-"]', '[class*="advertisement"]', '[class*="promo"]',
                    '[id*="ad-"]', '[id*="advertisement"]', '[id*="promo"]'
                ];
                
                adSelectors.forEach(selector => {
                    const ads = document.querySelectorAll(selector);
                    ads.forEach(ad => {
                        if (ad.offsetHeight > 30) { // Only remove visible ads
                            ad.style.display = 'none';
                            console.log('Ad element hidden:', ad.className || ad.id);
                        }
                    });
                });
                
                // Remove any floating elements that might block clicks
                const floatingElements = document.querySelectorAll('[style*="z-index"]');
                floatingElements.forEach(element => {
                    const zIndex = window.getComputedStyle(element).zIndex;
                    if (zIndex && parseInt(zIndex) > 1000) {
                        element.style.zIndex = '1';
                        console.log('High z-index element lowered:', element.className);
                    }
                });
            """)
            
            # Small wait to ensure DOM changes take effect
            time.sleep(0.5)
            
        except Exception as e:
            print(f"Could not dismiss overlays: {str(e)}")

    def wait_for_page_load(self, timeout=10):
        """Wait for page to fully load"""
        try:
            wait = WebDriverWait(self.driver, timeout)
            wait.until(lambda driver: driver.execute_script("return document.readyState") == "complete")
            # Additional wait for any AJAX requests
            time.sleep(0.5)  # Reduced from 1 to 0.5 seconds
        except TimeoutException:
            print("Page load timeout - continuing anyway")

    def scroll_to_element(self, element):
        """Scroll element into view"""
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center', behavior:'smooth'});", element)
            time.sleep(0.5)
        except Exception as e:
            print(f"Could not scroll to element: {str(e)}")

    def take_screenshot(self, name=None):
        """Take screenshot for debugging/failure cases"""
        try:
            if not name:
                name = f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create screenshots directory if it doesn't exist
            screenshot_dir = "screenshots"
            if not os.path.exists(screenshot_dir):
                os.makedirs(screenshot_dir)
            
            screenshot_path = os.path.join(screenshot_dir, f"{name}.png")
            self.driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            print(f"Could not take screenshot: {str(e)}")
            return None

    def get_page_source_debug(self):
        """Get page source for debugging"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            debug_dir = "debug"
            if not os.path.exists(debug_dir):
                os.makedirs(debug_dir)
            
            with open(f"{debug_dir}/page_source_{timestamp}.html", "w", encoding="utf-8") as f:
                f.write(self.driver.page_source)
            print(f"Page source saved for debugging: debug/page_source_{timestamp}.html")
        except Exception as e:
            print(f"Could not save page source: {str(e)}")

    def wait_and_handle_loading(self, additional_wait=2):
        """Wait for any loading indicators to disappear"""
        try:
            # Wait for common loading indicators to disappear
            loading_selectors = [
                "//div[contains(@class, 'loading')]",
                "//div[contains(@class, 'spinner')]", 
                "//div[contains(@class, 'loader')]",
                "//*[contains(text(), 'Loading')]"
            ]
            
            for selector in loading_selectors:
                try:
                    WebDriverWait(self.driver, 5).until(
                        EC.invisibility_of_element_located(("xpath", selector))
                    )
                except:
                    pass  # Ignore if loading indicator not found
            
            time.sleep(additional_wait)
        except Exception as e:
            print(f"Loading handler error: {str(e)}")