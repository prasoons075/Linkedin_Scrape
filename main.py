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

# Login to LinkedIn
actions.login(driver, CONFIG.email, CONFIG.password)

# driver.implicitly_wait(100)

# Create lists to store data for Excel
data = []
# columns = ['Company_Name', 'Employee_Count', 'where_they_live','where_they_studied','what_they_do','What_they_are_skilled_at','what_they_studied','Total_Job_Posting_Count',"Recently Posted Jobs"]
columns = ['Company_Name', 'Employee_Count', 'Company_employee_data','Total_Job_Posting_Count', "Recently Posted Jobs"]


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
    driver.implicitly_wait(10)

    # Find the element containing the number of employees using XPath
    # Note: Make sure to use the correct XPath based on your page structure
    xpath_for_employee_count = "//span[@class='t-normal t-black--light link-without-visited-state link-without-hover-state']"

    employee_element_count = driver.find_element(By.XPATH, xpath_for_employee_count)

    # Extract and print the number of employees
    number_of_employees = employee_element_count.text
    print(f"Company: {row['Company Name']}, Number of employees: {number_of_employees}")

    # Find the "Show more" button using the relative CSS selector
    show_more_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Show more people filters']")

    # Click the "Show more" button
    show_more_button.click()

    geo_loc_employees = []
    # Click the "Show more" button repeatedly until it's unclickable
    for _ in range(5):
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "button[aria-label='Next']")
            xpath_for_employee_geographical_location = "//body/div[@class='application-outlet']/div[@class='authentication-outlet']/div[@class='organization-outlet relative']/div[2]/div[1]/div[2]/main[1]/div[2]/div[1]/div[1]/div[1]/div[1]"#"//body/div[@class='application-outlet']/div[@class='authentication-outlet']/div[@class='organization-outlet relative']/div[2]/div[1]/div[2]/main[1]/div[2]/div[1]/div[1]/div[1]/div[1]" #".artdeco-card.p4.m2.org-people-bar-graph-module__geo-region"

            # employee_element_geo_loc = driver.find_element(By.XPATH, xpath_for_employee_geographical_location)
            employee_element_geo_loc = driver.find_element(By.XPATH, xpath_for_employee_geographical_location)

            # Extract and print the number of employees
            geo_loc_company = str(employee_element_geo_loc.text.replace("toggle off", ""))
            geo_loc_employees.append(geo_loc_company)
            print(f"Company: {row['Company Name']}, Geo Location of Employees: {geo_loc_company}")
            next_button.click()
        except NoSuchElementException:
            break
    
    formatted_company_data = format_company_data(geo_loc_employees)

    formatted_company_data = [string.replace('\n', ' ') for string in formatted_company_data]

    # Capture the URL before clicking the "Show more" button
    initial_url = driver.current_url

    # Append "/people/" to the company URL
    company_people_url = company_url.rstrip('/') + "/jobs/"

    # Open the LinkedIn company people page
    driver.get(company_people_url)

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

    # print(single_string)

    # Append data to the list
    # data.append([row['Company Name'], number_of_employees, formatted_company_data[0],formatted_company_data[1],formatted_company_data[2],formatted_company_data[3],formatted_company_data[4], numbers, single_string])
    data.append([row['Company Name'], number_of_employees, formatted_company_data, numbers, single_string])

# Close the browser after iterating through all companies
driver.quit()

# Create a DataFrame from the collected data
output_df = pd.DataFrame(data, columns=columns)

# Save the DataFrame to an Excel file
output_df.to_excel("LinkedIn_Company_Output.xlsx", index=False)


