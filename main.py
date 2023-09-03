import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from linkedin_scraper import actions
import re
from selenium.common.exceptions import NoSuchElementException
import config as CONFIG

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import openpyxl
import time

def convert_int_to_intType(pagination_list):
    pagination_list_updated = []
    for item in pagination_list:
        if item.isdigit():
            pagination_list_updated.append(int(item))
        else:
            pagination_list_updated.append(item)
    return pagination_list_updated

def process_job_data(data, worksheet):
    # Split the data into lines
    lines = data.strip().split('\n')

    # Define the list of words to filter out
    words_to_filter = ["Promoted","alumni work here","Vision, 401(k)","Medical, 401(k)","Your profile matches this job","Medical, Dental","$","Easy Apply","applicants","applicant", "Actively recruiting", "benefits", "benefit", "Within the past"]
    
    # Filter out lines containing any of the specified words
    filtered_lines = [line for line in lines if all(word not in line for word in words_to_filter)]

    # Initialize variables to hold job posting information
    job_posting = []

    # Iterate through the filtered lines and extract job posting information
    for line in filtered_lines:
        job_posting.append(line)
        if len(job_posting) == 4:
            # Append the job posting information to the worksheet
            worksheet.append(job_posting)
            # Reset the job posting information
            job_posting = []


def format_company_data(texts):
    words_to_remove = ['employees', 'Search employees by title, keyword or school', 'Previous', 'Next', 'Add']

    formatted_data = []
    filtered_texts = []
    for text in texts:
        lines = text.split('\n')
    
        # Filter out lines that contain the words to remove
        filtered_lines = [line for line in lines if not any(word in line for word in words_to_remove)]
    
        # Join the filtered lines back into a text
        filtered_text = "\n".join(filtered_lines)
        filtered_texts.append(filtered_text)
    temp_text = filtered_texts
    # filtered_texts = filtered_texts[1:]
    # _where_they_live = filtered_texts[0]
    # _where_they_studied = filtered_texts[1]
    # _what_they_do = filtered_texts[2]
    # What_they_are_skilled_at = filtered_texts[3].split("What they studied")[0]
    # what_they_studied = filtered_texts[3].split("What they studied")[1]
    
    # # Find the index where "Where they studied" occurs
    # start_index = _where_they_live.find("Where they studied")
    
    # if start_index != -1:
    #     # Remove everything from the "Where they studied" onward
    #     where_they_live = _where_they_live[:start_index]
    #     # print(where_they_live)
    #     formatted_data.append(where_they_live)
    
    # start_index = _where_they_studied.find("What they do")
    
    # if start_index != -1:
    #     where_they_studied = _where_they_studied[:start_index]
    #     formatted_data.append(where_they_studied)
    
    # start_index = _what_they_do.find("What they are skilled at")
    
    # if start_index != -1:
    #     what_they_do = _what_they_do[:start_index]
    #     formatted_data.append(what_they_do)
    
    # formatted_data.append(What_they_are_skilled_at)
    # formatted_data.append(what_they_studied)

    # return formatted_data
    return filtered_texts

# Loading companies list to scrap data
company_list = pd.read_excel(CONFIG.data)

# Initialize the Chrome driver
driver = webdriver.Chrome()

# wait = WebDriverWait(driver, 200)

# Login to LinkedIn
actions.login(driver, CONFIG.email, CONFIG.password, timeout=60)

# wait = WebDriverWait(driver, 60)
# driver.implicitly_wait(30)

# Create lists to store data for Excel
data = []
columns = ['Company_Name', 'Industry' ,'Employee_Count', 'where_they_live','what_they_do','What_they_are_skilled_at','what_they_studied','Total_Job_Posting_Count',"Recently Posted Jobs", "Employee Satisfaction"]
# columns = ['Company_Name', 'Employee_Count', 'Company_employee_data','Total_Job_Posting_Count', "Recently Posted Jobs", "Employee Satisfaction"]

job_listing = []

# columns_job_posting = ['Company_Name', 'industry', "Job_posting", "Posted_on"]


# Iterate through each company URL in the company_list DataFrame
for index, row in company_list.iterrows():
    company_url = row['Linkedin_URL']
    if not company_url.startswith("http"):
        company_url = "https://" + company_url
    
    # Append "/people/" to the company URL
    company_people_url = company_url.rstrip('/') + "/people/"

    # Open the LinkedIn company people page
    driver.get(company_people_url)
    
    # Wait for the page to load (you might need to adjust the waiting time based on your internet speed)
    driver.implicitly_wait(60)

    # Find the element containing the number of employees using XPath
    # Note: Make sure to use the correct XPath based on your page structure

    industry_type= "//body/div[@class='application-outlet']/div[@class='authentication-outlet']/div[@class='organization-outlet relative']/div[2]/div[1]/div[2]/main[1]/div[1]/section[1]/div[1]/div[2]/div[1]/div[1]/div[2]/div[1]/div[1]/div[1]"
    industry_type = driver.find_element(By.XPATH, industry_type)
    industry_type_text = industry_type.text

    xpath_for_employee_count = "//span[@class='t-normal t-black--light link-without-visited-state link-without-hover-state']"

    employee_element_count = driver.find_element(By.XPATH, xpath_for_employee_count)

    # Extract and print the number of employees
    number_of_employees = employee_element_count.text
    print(f"Company: {row['Company Name']}, Number of employees: {number_of_employees}")

    # Find the "Show more" button using the relative CSS selector
    show_more_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Show more people filters']")

    # Click the "Show more" button
    show_more_button.click()
    driver.implicitly_wait(60)
    
    employee_work_location = "//div[@class='artdeco-card p4 m2 org-people-bar-graph-module__geo-region']"
    employee_work_location_text = driver.find_element(By.XPATH, employee_work_location)
    employee_work_location_text = employee_work_location_text.text.replace("toggle off", "")

    next_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
    next_button.click()
    driver.implicitly_wait(60)
    next_button.click()
    driver.implicitly_wait(60)
    employee_current_fucntion = ".artdeco-card.p4.m2.org-people-bar-graph-module__current-function"
    employee_current_fucntion_text= driver.find_element(By.CSS_SELECTOR, employee_current_fucntion)
    employee_current_fucntion_text = employee_current_fucntion_text.text.replace("toggle off", "")

    next_button.click()    
    driver.implicitly_wait(60)

    employee_skillset = ".artdeco-card.p4.m2.org-people-bar-graph-module__skill-explicit"
    employee_skillset_text = driver.find_element(By.CSS_SELECTOR, employee_skillset)
    employee_skillset_text = employee_skillset_text.text.replace("toggle off", "")

    next_button.click()
    driver.implicitly_wait(60)

    what_employees_studied =".artdeco-card.p4.m2.org-people-bar-graph-module__field-of-study"
    what_employees_studied_text = driver.find_element(By.CSS_SELECTOR, what_employees_studied)
    what_employees_studied_text= what_employees_studied_text.text.replace("toggle off", "")

    # Capture the URL before clicking the "Show more" button
    initial_url = driver.current_url

    # Append "/people/" to the company URL
    company_people_url = company_url.rstrip('/') + "/jobs/"

    # Open the LinkedIn company people page
    driver.get(company_people_url)
    driver.implicitly_wait(60)
    xpath_for_company_job_count = ".artdeco-card.org-jobs-job-search-form-module.container"
                                               
    # employee_element_geo_loc = driver.find_element(By.XPATH, xpath_for_employee_geographical_location)
    company_job_count = driver.find_element(By.CSS_SELECTOR, xpath_for_company_job_count)

    # Extract and print the number of job counts
    new_company_jobs_count = company_job_count.text
    numbers = int(re.findall(r'\d+', new_company_jobs_count)[0])
    print(f"Company: {row['Company Name']}, New Job Postings Count: {numbers}")

    recently_posted_jobs = []
    xpath_for_new_jobs = "//div[@class='artdeco-carousel__content']"
    xpath_for_next_button = "//span[normalize-space()='Next']"
    company_jobs = driver.find_element(By.XPATH, xpath_for_new_jobs)
    job_next_button = driver.find_element(By.XPATH, xpath_for_next_button)
    recently_posted_jobs.append(company_jobs.text)

    recently_posted_jobs_list = []
    

    for i in range(len(recently_posted_jobs)):
        formatting_jobs = recently_posted_jobs[i].split("\nSave\nJob Title")
        for j in range(len(formatting_jobs)):
            recently_posted_jobs_list.append(formatting_jobs[j])

    # Convert the list to a single string
    single_string = '\n'.join(recently_posted_jobs_list)

    #fetching all jobs posting for a company code start

    show_all_jobs = "//span[@class='t-black--light text-body-medium-bold']"
    show_all_jobs_click = driver.find_element(By.XPATH, show_all_jobs)
    show_all_jobs_click.click()
    driver.implicitly_wait(60)
    time.sleep(10)

    current_url = driver.current_url

    # Define a regular expression pattern to match "f_C=" followed by numbers and "%"
    pattern = r'f_C=([0-9]+)%'
    
    # Use re.search to find the pattern in the URL
    match = re.search(pattern, current_url)
    
    # Check if a match was found
    if match:
        # Extract the matched number
        number = match.group(1)
        print("Number between f_C= and %:", number)

        select_company = "//div[@data-basic-filter-parameter-name='company']"
        select_company_click = driver.find_element(By.XPATH, select_company)
        select_company_click.click()
        driver.implicitly_wait(60)
        print("filter clicked")
        reset_all_companies ="//button[@aria-label='Reset selected Company']"
        reset_all_companies_click = driver.find_element(By.XPATH, reset_all_companies)
        reset_all_companies_click.click()    
        driver.implicitly_wait(60)
        print("reset clicked")
        # Company name you want to search for
        company_name = row['Company Name'].split("|")[0].strip()
        select_top_company = "//label[@for='company-"+number+"']"
        select_top_company_click = driver.find_element(By.XPATH, select_top_company)
        select_top_company_click.click()
        driver.implicitly_wait(60)
        print("selected only company clicked")
        search_result = ".artdeco-button.artdeco-button--2.artdeco-button--primary.ember-view.ml2"
        search_result_click = driver.find_element(By.CSS_SELECTOR, search_result)
        search_result_click.click()
        driver.implicitly_wait(60)
        print("filter applied")
    else:
        print("No match found.")

    driver.implicitly_wait(60)

    job_posting_pagination = "//ul[@class='artdeco-pagination__pages artdeco-pagination__pages--number']"
    job_posting_pagination_count = driver.find_element(By.XPATH, job_posting_pagination)

    pagination_list = [job_posting_pagination_count.text][0].split('\n')

    pagination_list = convert_int_to_intType(pagination_list)
    last_page = None
    i = 1
    while True:
        try:
            # if isinstance(pagination_list[-1], int): #pagination_list[-1].isdigit()
            #     last_page = pagination_list[-1]
            #     break
            last_page = int(pagination_list[-2]) + 1
            last_known_page = "//button[@aria-label='Page " + str(last_page) + "']"
            last_known_page_click = driver.find_element(By.XPATH, last_known_page)
            print("current last page: ", last_page)
            # last_known_page_click.click()

            job_posting_pagination = "//ul[@class='artdeco-pagination__pages artdeco-pagination__pages--number']"
            job_posting_pagination_count = driver.find_element(By.XPATH, job_posting_pagination)
            #".jobs-search-results-list"
            job_posting_scrollbar = "//ul[@class='scaffold-layout__list-container']" #"//body/div[@class='application-outlet']/div[@class='authentication-outlet']/div[4]/div[1]/div[1]/main[1]/div[1]/div[1]/div[1]"
            # # Locate the left scrollable element using its XPath or other suitable locator
            left_scroll_element = driver.find_element(By.XPATH, "//body/div[@class='application-outlet']/div[@class='authentication-outlet']/div[4]/div[1]/div[1]/main[1]/div[1]/div[1]/div[1]")
            #  # Scroll the left element using JavaScript
            driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", left_scroll_element)
            driver.implicitly_wait(60)
            time.sleep(3)
            # "//body/div[@class='application-outlet']/div[@class='authentication-outlet']/div[4]/div[1]/div[1]/main[1]/div[1]/div[1]/div[1]"
            job_posting = driver.find_element(By.XPATH, job_posting_scrollbar)
            job_posting_text = job_posting.text
            # print(job_posting.text)
            # Load an existing Excel workbook and its worksheet (if it exists)
            try:
                workbook = openpyxl.load_workbook("Linkedin_Scrape/job_postings.xlsx")
                worksheet = workbook.active
            except FileNotFoundError:
                # If the file doesn't exist, create a new workbook and worksheet
                workbook = openpyxl.Workbook()
                worksheet = workbook.active
                # Define headers for the Excel file for the first time
                headers = ["Job Title", "Company", "Location", "Posted"]
                worksheet.append(headers)  
            # Call the method to process the job data and append it to the worksheet
            process_job_data(job_posting.text, worksheet)
            # Save the Excel file
            workbook.save("Linkedin_Scrape/job_postings.xlsx")
            # print("done")
            i=i+1
            next_page = "//button[@aria-label='Page " + str(i) + "']"
            next_page_click = driver.find_element(By.XPATH, next_page)
            print(next_page)
            next_page_click.click()
            driver.implicitly_wait(60)
            # print(job_posting_pagination_count.text)
            pagination_list = [job_posting_pagination_count.text][0].split('\n')
            pagination_list = convert_int_to_intType(pagination_list)
        except:
            break

        #fetching all jobs posting for a company code ends
    
    # Employee Satisfaction from Indeed Feed
    indeed_url = "https://www.indeed.com/companies?hl=en&co=US&isid=us_tmp_ca_browse-companies_ch_webpage_au_enterprise_pe__pr__cr_&ikw=browse-companies"
    driver.get(indeed_url)
    driver.implicitly_wait(60)
    # Company name you want to search for
    company_name = row['Company Name'].split("|")[0].strip()

    # XPaths for search input and search button
    xpath_for_search = "//input[@name='q']"
    xpath_for_search_button = "//button[normalize-space()='Find Companies']"

    # Locate the search input element and enter the company name
    search_page = driver.find_element(By.XPATH, xpath_for_search)
    search_page.send_keys(company_name)
    search_button_click = driver.find_element(By.XPATH, xpath_for_search_button)
    search_button_click.click()
    driver.implicitly_wait(60)
    xpath_company ="body > div:nth-child(2) > div:nth-child(1) > main:nth-child(1) > div:nth-child(1) > div:nth-child(2) > section:nth-child(1) > div:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > div:nth-child(1) > a:nth-child(1) > div:nth-child(1)"
    company_click = driver.find_element(By.CSS_SELECTOR, xpath_company)
    company_click.click()
    driver.implicitly_wait(3)      
    xpath_for_satisfaction_feed = "//div[@class='css-1cosc8r e37uo190']"#"//body/div/div/main[@class='css-q1edpo eu4oa1w0']/div[@class='css-f9in6m eu4oa1w0']/div[@class='css-qkv3x5 eu4oa1w0']/section[@class='css-u74ql7 eu4oa1w0']/div[1]"    
    satisfaction_rate = driver.find_element(By.XPATH, xpath_for_satisfaction_feed)
    
    print(satisfaction_rate.text)

    # Append data to the list
    data.append([row['Company Name'], industry_type_text, number_of_employees, employee_work_location_text, employee_current_fucntion_text, employee_skillset_text, what_employees_studied_text, numbers, single_string, satisfaction_rate.text])
        
# Close the browser after iterating through all companies
driver.quit()

# Create a DataFrame from the collected data
output_df = pd.DataFrame(data, columns=columns)

# Save the DataFrame to an Excel file
output_df.to_excel("Linkedin_Scrape/LinkedIn_Company_Output_sep2.xlsx", index=False)


