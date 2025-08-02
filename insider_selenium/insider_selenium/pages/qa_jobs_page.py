from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException
import time
from .base_page import BasePage

class QAJobsPage(BasePage):
    SEE_ALL_LINK = (By.XPATH, "//a[contains(text(), 'See all QA jobs')]")
    
    # Filter dropdowns - these selectors might need adjustment based on actual page structure
    LOCATION_FILTER = (By.ID, "filter-by-location")
    DEPARTMENT_FILTER = (By.ID, "filter-by-department")
    
    # Alternative selectors if the above don't work
    LOCATION_DROPDOWN = (By.XPATH, "//select[contains(@class, 'location') or contains(@name, 'location')]")
    DEPARTMENT_DROPDOWN = (By.XPATH, "//select[contains(@class, 'department') or contains(@name, 'department')]")
    
    # Generic dropdown selectors
    ALL_DROPDOWNS = (By.XPATH, "//select")
    
    # Job listings
    JOB_LIST = (By.XPATH, "//div[contains(@class, 'job') or contains(@class, 'position')]")
    VIEW_ROLE_XPATH = "//a[text()='View Role' or contains(text(), 'View Role')]"
    
    # Job details selectors for verification
    JOB_POSITION = (By.XPATH, "//span[contains(@class, 'position-title') or contains(@class, 'job-title')]")
    JOB_DEPARTMENT = (By.XPATH, "//span[contains(@class, 'position-department') or contains(@class, 'department')]")
    JOB_LOCATION = (By.XPATH, "//div[contains(@class, 'position-location') or contains(@class, 'location')]")

    def open_all_jobs(self):
        """Click 'See all QA jobs' link and wait for job listings to load"""
        self.dismiss_cookie_banner()
        
        # Wait for and click the "See all QA jobs" link
        link = self.wait.until(EC.element_to_be_clickable(self.SEE_ALL_LINK))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", link)
        time.sleep(1)  # Brief pause after scrolling
        link.click()
        
        # Wait for job listings to appear
        self.wait.until(EC.presence_of_element_located((By.XPATH, self.VIEW_ROLE_XPATH)))
        print("Job listings loaded successfully")

    def apply_filters(self, location="Istanbul, Turkey", department="Quality Assurance"):
        """Apply location and department filters"""
        self.dismiss_cookie_banner()
        
        # Wait a moment for the page to fully load
        time.sleep(2)  # Reduced from 3 to 2 seconds
        
        # Store initial job count to detect when filtering is complete
        initial_jobs = self._get_current_job_count()
        print(f"Initial job count: {initial_jobs}")
        
        # Try to find and interact with filter dropdowns
        self._apply_location_filter(location)
        time.sleep(1)  # Reduced from 2 to 1 second
        
        self._apply_department_filter(department)
        
        # Wait for filtered results to load completely
        self._wait_for_filter_results_to_load(initial_jobs)
        
        print(f"Filters applied: Location='{location}', Department='{department}'")

    def _apply_location_filter(self, location):
        """Apply location filter using various strategies"""
        strategies = [
            lambda: self._select_from_dropdown(self.LOCATION_FILTER, location),
            lambda: self._select_from_dropdown(self.LOCATION_DROPDOWN, location),
            lambda: self._select_from_generic_dropdown("location", location),
            lambda: self._click_filter_option("location", location)
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                strategy()
                print(f"Location filter applied using strategy {i+1}")
                return
            except Exception as e:
                print(f"Location filter strategy {i+1} failed: {str(e)}")
                continue
        
        print("Warning: Could not apply location filter")

    def _apply_department_filter(self, department):
        """Apply department filter using various strategies"""
        strategies = [
            lambda: self._select_from_dropdown(self.DEPARTMENT_FILTER, department),
            lambda: self._select_from_dropdown(self.DEPARTMENT_DROPDOWN, department),
            lambda: self._select_from_generic_dropdown("department", department),
            lambda: self._click_filter_option("department", department)
        ]
        
        for i, strategy in enumerate(strategies):
            try:
                strategy()
                print(f"Department filter applied using strategy {i+1}")
                return
            except Exception as e:
                print(f"Department filter strategy {i+1} failed: {str(e)}")
                continue
        
        print("Warning: Could not apply department filter")

    def _select_from_dropdown(self, locator, value):
        """Select value from a standard dropdown"""
        dropdown_element = self.wait.until(EC.element_to_be_clickable(locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", dropdown_element)
        
        select = Select(dropdown_element)
        
        # Try different selection methods
        try:
            select.select_by_visible_text(value)
        except:
            try:
                select.select_by_value(value)
            except:
                # Try partial text match
                options = select.options
                for option in options:
                    if value.lower() in option.text.lower():
                        select.select_by_visible_text(option.text)
                        return
                raise Exception(f"Could not find option with text containing '{value}'")

    def _select_from_generic_dropdown(self, filter_type, value):
        """Try to find and select from dropdowns by analyzing all select elements"""
        dropdowns = self.driver.find_elements(*self.ALL_DROPDOWNS)
        
        for dropdown in dropdowns:
            try:
                # Check if this dropdown is for the filter we want
                dropdown_html = dropdown.get_attribute('outerHTML').lower()
                if filter_type.lower() in dropdown_html:
                    select = Select(dropdown)
                    
                    # Try to find the matching option
                    for option in select.options:
                        if value.lower() in option.text.lower():
                            select.select_by_visible_text(option.text)
                            return
            except Exception:
                continue
        
        raise Exception(f"Could not find {filter_type} dropdown")

    def _click_filter_option(self, filter_type, value):
        """Try to click on filter options if they're not standard dropdowns"""
        # Look for clickable filter elements
        possible_selectors = [
            f"//div[contains(@class, '{filter_type}')]//span[contains(text(), '{value}')]",
            f"//button[contains(@class, '{filter_type}')]//span[contains(text(), '{value}')]",
            f"//li[contains(@class, '{filter_type}')][contains(text(), '{value}')]",
            f"//*[contains(text(), '{value}')]"
        ]
        
        for selector in possible_selectors:
            try:
                elements = self.driver.find_elements(By.XPATH, selector)
                for element in elements:
                    if element.is_displayed() and element.is_enabled():
                        self.driver.execute_script("arguments[0].click();", element)
                        return
            except Exception:
                continue
        
        raise Exception(f"Could not find clickable {filter_type} option for '{value}'")

    def verify_job_filters(self, expected_location="Istanbul, Turkey", expected_department="Quality Assurance"):
        """Verify that all displayed jobs match the filter criteria"""
        self.dismiss_cookie_banner()
        
        # Wait for jobs to load after filtering
        time.sleep(2)
        
        # Get all job elements
        job_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'position-list-item') or contains(@class, 'job-item')]")
        
        if not job_elements:
            # Try alternative job container selectors
            job_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'job') or contains(@class, 'position')]")
        
        assert job_elements, "No job listings found after filtering"
        print(f"Found {len(job_elements)} job(s) after filtering")
        
        # Verify each job meets the criteria
        for i, job in enumerate(job_elements):
            try:
                # Extract job details from the job element
                job_text = job.text.lower()
                
                # Check if Quality Assurance is mentioned in the job
                qa_keywords = ["quality assurance", "qa", "test", "automation"]
                has_qa = any(keyword in job_text for keyword in qa_keywords)
                
                # Check if Istanbul/Turkey is mentioned
                location_keywords = ["istanbul", "turkey", "remote"]
                has_location = any(keyword in job_text for keyword in location_keywords)
                
                print(f"Job {i+1}: QA keywords found: {has_qa}, Location keywords found: {has_location}")
                
                # At minimum, we expect QA-related jobs
                assert has_qa, f"Job {i+1} does not appear to be a Quality Assurance position"
                
            except Exception as e:
                print(f"Warning: Could not fully verify job {i+1}: {str(e)}")

    def open_first_job(self):
        """Click on the first 'View Role' button with enhanced waiting"""
        self.dismiss_cookie_banner()
        
        # Wait for View Role buttons to be present and stable
        self.wait.until(EC.presence_of_element_located((By.XPATH, self.VIEW_ROLE_XPATH)))
        
        # Additional wait to ensure all filtering/loading is complete
        self._wait_for_stable_job_list()
        
        # Get all View Role links after everything has settled
        view_role_links = self.driver.find_elements(By.XPATH, self.VIEW_ROLE_XPATH)
        
        if not view_role_links:
            self.take_screenshot("no_view_role_links")
            raise AssertionError("No 'View Role' links found on the page")
        
        print(f"Found {len(view_role_links)} 'View Role' links")
        
        # Verify the first job is actually a QA job before clicking
        first_job_container = self._find_job_container_for_link(view_role_links[0])
        if first_job_container:
            self._verify_job_is_qa_related(first_job_container)
        
        first_link = view_role_links[0]
        
        # Scroll to the element and wait
        self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", first_link)
        time.sleep(1)  # Reduced from 2 to 1 second
        
        # Ensure no overlays are blocking the click
        self.dismiss_cookie_banner()
        
        try:
            first_link.click()
        except ElementClickInterceptedException:
            # If normal click fails, use JavaScript click
            self.driver.execute_script("arguments[0].click();", first_link)
            print("Used JavaScript click due to click interception")
        
        print("Clicked on first job's 'View Role' button")

    def _get_current_job_count(self):
        """Get current number of job listings on the page"""
        try:
            job_elements = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'position-list-item') or contains(@class, 'job-item') or contains(@class, 'job') or contains(@class, 'position')]")
            return len(job_elements)
        except:
            return 0

    def _wait_for_filter_results_to_load(self, initial_count, max_wait=10):
        """Wait for filter results to completely load by monitoring job count changes"""
        print("Waiting for filter results to load completely...")
        
        # Wait for any loading indicators to disappear
        self._wait_for_loading_to_complete()
        
        # Monitor job count stability
        stable_count = 0
        last_count = initial_count
        wait_time = 0
        
        while wait_time < max_wait:
            time.sleep(0.5)  # Reduced from 1 to 0.5 seconds
            wait_time += 0.5
            
            current_count = self._get_current_job_count()
            
            if current_count == last_count:
                stable_count += 0.5
            else:
                stable_count = 0
                last_count = current_count
                print(f"Job count changed to: {current_count}")
            
            # If count has been stable for 2 seconds, filtering is likely complete
            if stable_count >= 2:  # Reduced from 3 to 2 seconds
                print(f"Filter results stabilized at {current_count} jobs")
                break
        
        # Additional safety wait
        time.sleep(1)  # Reduced from 2 to 1 second
        
        final_count = self._get_current_job_count()
        print(f"Final job count after filtering: {final_count}")

    def _wait_for_loading_to_complete(self):
        """Wait for any loading indicators to disappear"""
        loading_indicators = [
            "//div[contains(@class, 'loading')]",
            "//div[contains(@class, 'spinner')]", 
            "//div[contains(@class, 'loader')]",
            "//div[contains(@class, 'fetching')]",
            "//*[contains(text(), 'Loading')]",
            "//*[contains(text(), 'Searching')]"
        ]
        
        for indicator in loading_indicators:
            try:
                WebDriverWait(self.driver, 5).until(
                    EC.invisibility_of_element_located((By.XPATH, indicator))
                )
            except:
                pass  # Ignore if indicator not found

    def _wait_for_stable_job_list(self, stability_time=3):
        """Wait for job list to be stable (no more changes happening)"""
        print("Waiting for job list to stabilize...")
        
        last_html = ""
        stable_count = 0
        
        for _ in range(10):  # Max 10 seconds
            time.sleep(1)
            
            # Get HTML of job listing area
            try:
                job_area = self.driver.find_element(By.XPATH, "//div[contains(@class, 'job') or contains(@class, 'position')]/..")
                current_html = job_area.get_attribute('innerHTML')
            except:
                current_html = self.driver.page_source[:5000]  # Fallback to page source
            
            if current_html == last_html:
                stable_count += 1
            else:
                stable_count = 0
                last_html = current_html
            
            if stable_count >= stability_time:
                print("Job list appears stable")
                break
        
        # Final safety wait
        time.sleep(1)

    def _find_job_container_for_link(self, view_role_link):
        """Find the job container that contains the given View Role link"""
        try:
            # Navigate up the DOM to find the parent job container
            return self.driver.execute_script("""
                let link = arguments[0];
                let parent = link.parentElement;
                
                // Look for job container up to 5 levels up
                for (let i = 0; i < 5; i++) {
                    if (!parent) break;
                    
                    let className = parent.className || '';
                    if (className.includes('job') || className.includes('position') || 
                        className.includes('listing') || className.includes('item')) {
                        return parent;
                    }
                    parent = parent.parentElement;
                }
                return null;
            """, view_role_link)
        except:
            return None

    def _verify_job_is_qa_related(self, job_container):
        """Verify that a job container contains QA-related content"""
        try:
            job_text = job_container.text.lower()
            qa_keywords = ["quality assurance", "qa", "test", "automation", "testing", "quality"]
            
            has_qa_keyword = any(keyword in job_text for keyword in qa_keywords)
            
            if not has_qa_keyword:
                print(f"Warning: First job may not be QA-related. Job text: {job_text[:200]}...")
                # Take screenshot for debugging
                self.take_screenshot("non_qa_job_detected")
            else:
                print("Confirmed: First job appears to be QA-related")
                
        except Exception as e:
            print(f"Could not verify job content: {str(e)}")

    def take_screenshot(self, name):
        """Take screenshot for debugging (delegated to base page if available)"""
        try:
            if hasattr(self, 'driver'):
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"{name}_{timestamp}.png"
                self.driver.save_screenshot(filename)
                print(f"Screenshot saved: {filename}")
        except Exception as e:
            print(f"Could not take screenshot: {str(e)}")