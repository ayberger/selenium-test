import pytest
from pages.home_page import HomePage
from pages.careers_page import CareersPage  
from pages.qa_jobs_page import QAJobsPage
from pages.job_detail_page import JobDetailPage

@pytest.mark.usefixtures('driver')
class TestQAJobsFlow:
    def test_end_to_end_qa_flow(self, driver):
        """
        Test automation flow as per requirements:
        1. Visit Insider homepage and verify it opens
        2. Navigate to Careers page and verify sections
        3. Go to QA jobs page and apply filters
        4. Verify filtered jobs meet criteria
        5. Click View Role and verify Lever application form
        """
        
        # Step 1: Visit homepage and verify it opens
        print("Step 1: Opening Insider homepage...")
        home_page = HomePage(driver)
        home_page.open()
        
        # Step 2: Navigate to Careers and verify sections
        print("Step 2: Navigating to Careers page...")
        home_page.navigate_to_careers()
        
        careers_page = CareersPage(driver)
        careers_page.verify_sections()
        
        # Step 3: Go to QA jobs page
        print("Step 3: Going to Quality Assurance jobs page...")
        careers_page.go_to_quality_assurance()
        
        # Step 4: Open job listings and apply filters
        print("Step 4: Opening job listings and applying filters...")
        qa_page = QAJobsPage(driver)
        qa_page.open_all_jobs()
        
        # Apply filters as required: Istanbul, Turkey + Quality Assurance
        qa_page.apply_filters(
            location="Istanbul, Turkiye", 
            department="Quality Assurance"
        )
        
        # Step 5: Verify filtered jobs meet criteria
        print("Step 5: Verifying filtered jobs meet criteria...")
        qa_page.verify_job_filters(
            expected_location="Istanbul, Turkiye",
            expected_department="Quality Assurance"
        )
        
        # Step 6: Click first job's View Role button
        print("Step 6: Clicking on first job's View Role button...")
        qa_page.open_first_job()
        
        # Step 7: Verify redirect to Lever application form
        print("Step 7: Verifying redirect to Lever application form...")
        job_detail_page = JobDetailPage(driver)
        job_detail_page.verify_application_form_displayed()
        
        print("Test completed successfully!")