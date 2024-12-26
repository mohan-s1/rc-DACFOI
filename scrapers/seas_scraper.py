#/* --------------------------------------------------------------------------------
#   UVA Research Computing
#   University of Virginia
#   Matthew Galitz, Mohan Shankar
#
#   This file scrapes UVA websites for information about faculty
#-------------------------------------------------------------------------------- */
import requests
from bs4 import BeautifulSoup
import pandas as pd
from lxml import html
import requests
#-------------------------------------------------------------------------------- */
# FUNCTION DEFINITIONS

def get_page_title(url):
    # Send a GET request to the webpage
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find the <h1> tag with the specific class and id
        page_title = soup.find('h1', class_='page_title', id='page_title')
        
        # Extract and return the text if the tag is found
        if page_title:
            return page_title.get_text(strip=True)
        else:
            print("The page title element was not found.")
            return None
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return None
    
def get_emails(url):
    response = requests.get(url)
    if response.status_code == 200:
        tree = html.fromstring(response.content)
        emails = {email.replace('mailto:', '') for email in tree.xpath("//a[contains(@class, 'people_meta_detail_info_link') and starts-with(@href, 'mailto:')]/@href")}
        
        if emails:
            print("Emails found:")
            for email in emails:
                print(email)
        else:
            print("No emails found.")
            emails.add(url)  # Add the URL to emails set if no email is found
        
        return list(emails)
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return url
    
def get_about(url):
    # Fetch the webpage content
    response = requests.get(url)
    
    if response.status_code == 200:
        # Parse the HTML content
        tree = html.fromstring(response.content)
        
        # Check if the 'Education' header exists
        education_exists = tree.xpath("//h2[text()='Education']")
        
        if education_exists:
            # XPath expression to select all elements between <h2>About</h2> and <h2>Education</h2>
            elements_between = tree.xpath("//h2[text()='About']/following-sibling::*[following-sibling::h2[text()='Education']]")
        else:
            # XPath expression to select everything after <h2>About</h2>
            elements_between = tree.xpath("//h2[text()='About']/following-sibling::*")
        
        # Extract and print the text content from the selected elements
        text_content = [elem.text_content().strip() for elem in elements_between if elem.text_content().strip()]
        
        if text_content:
            print("Extracted text:")
            for text in text_content:
                print(text)
            return text_content
        else:
            print("No text found after <h2>About</h2> or between <h2>About</h2> and <h2>Education</h2>.")
            return None
    else:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
        return None
    
def get_links(url):
    """
    Finds overall link to SEAS faculty page; starts at a generalized url and iterates until no more content is found
    """
    
    i = 0

    url_list = []

    while True:
        # Construct the URL with the current page index
        url = url+str(i)
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content using lxml
            tree = html.fromstring(response.content)
            
            # Check for the "no results" message that occurs when you've exceeded the number of pages on an engineering site with actual contnent 
            no_results = tree.xpath('//div[contains(@class, "results_message_inner typography") and contains(text(), "There are no results matching these criteria.")]')
            if no_results:
                print("No more results found. Exiting.")
                break
            
            # Find all 'a' tags with the class 'contact_block_name_link'
            links = tree.xpath('//a[contains(@class, "contact_block_name_link")]/@href')
            
            # Print the extracted URLs and add them to the list
            for link in links:
                # print(link)
                url_list.append(link)
        else:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
            break

        # Increment the page index
        i += 1

    return url_list
#-------------------------------------------------------------------------------- */
SEAS_departments = {'Biomedical Engineering': "https://engineering.virginia.edu/department/biomedical-engineering/people?keyword=&position=2&impact_area=All&research_area=All&page=",
                    'Chemical Engineering': "https://engineering.virginia.edu/department/chemical-engineering/people?keyword=&position=2&impact_area=All&research_area=All&page=",
                    'Civil and Environmental Engineering': "https://engineering.virginia.edu/department/civil-and-environmental-engineering/people?keyword=&position=2&impact_area=All&research_area=All&page=",
                    'Electrical and Computer Engineering': "https://engineering.virginia.edu/department/electrical-and-computer-engineering/faculty?keyword=&position=2&impact_area=All&research_area=All&page=",
                    'Engineering and Society': "https://engineering.virginia.edu/department/engineering-and-society/people?keyword=&position=2&impact_area=All&research_area=All&page=",
                    'Materials Science and Engineering': "https://engineering.virginia.edu/department/materials-science-and-engineering/people?impact_area=All&keyword=&position=2&research_area=All&page=",
                    'Mechanical and Aerospace Engineering': "https://engineering.virginia.edu/department/mechanical-and-aerospace-engineering/people?keyword=&position=2&impact_area=All&research_area=All&page=",
                    'Systems and Information Engineering': "https://engineering.virginia.edu/department/systems-and-information-engineering/people?keyword=&position=2&impact_area=All&research_area=All&page="}
    
from concurrent.futures import ThreadPoolExecutor

def get_dept_info(department, url) -> pd.DataFrame: 
    """
    Function that takes returns scraped information about a department's faculty members as a Pandas DataFrame

    Leverages the pattern that SEAS pages end like 

    research_area=All&page=0, research_area=All&page=1, research_area=All&page=2, ... 

    Args:
        department (str): Department Name
        url (str): Base url that an incremental pattern applies 

    Returns:
        pd.DataFrame: Pandas DateFrame containing the faculty name, email address, about section, and SEAS website 
    """
    url_list = get_links(url)
    faculty_emails = []
    faculty_about = []
    engineering_url = "https://engineering.virginia.edu"
    faculty_names = []

    for link in url_list:
        full_url = engineering_url + link
        name = get_page_title(full_url)
        if name:
            faculty_names.append(name)

    for link in url_list:
        full_url = engineering_url + link
        email = get_emails(full_url)
        about_section = get_about(full_url)
        faculty_emails.append(email if email else "No Email Found")
        faculty_about.append(about_section if about_section else "No About Section Found")

    data = {
        'Faculty Name': faculty_names,
        'About Section': faculty_about,
        'Faculty Email': faculty_emails,
        'Engineering Page': url_list
    }

    df = pd.DataFrame(data)
    df['Department'] = department
    return df

# Function to process departments in parallel
def process_departments_in_parallel(departments):
    results = {}
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(get_dept_info, dept, url): dept for dept, url in departments.items()
        }
        for future in futures:
            dept = futures[future]
            try:
                results[dept] = future.result()
            except Exception as e:
                print(f"Error processing department {dept}: {e}")
    return results

# Run the processing
results = process_departments_in_parallel(SEAS_departments)

# Save each DataFrame to a variable dynamically
for dept, df in results.items():
    globals()[f"{dept.replace(' ', '_')}_df"] = df

    # Concatenate all dataframes from the results dictionary
all_data = pd.concat(results.values(), ignore_index=True)

# Combine rows based on 'Faculty Name'
df_combined = all_data.groupby('Faculty Name', as_index=False).agg({
    'About Section': 'first',  # Keep the first non-null value
    'Faculty Email': 'first',  # Keep the first non-null value
    'Engineering Page': 'first',  # Keep the first non-null value
    'Department': ' '.join  # Concatenate department data
})

# Optionally, save to variables dynamically
for dept, df in results.items():
    globals()[f"{dept.replace(' ', '_')}_df"] = df

outfile_path = "" # Add path to save csv locally

df_combined.to_csv(f"{outfile_path}")