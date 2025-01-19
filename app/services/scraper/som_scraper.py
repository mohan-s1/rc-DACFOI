import typing
import logging

from app.utils.http_client import HttpClient
from app.utils.institution_utils import InstitutionUtils
from app.services.scraper.base_scraper import BaseScraper
from lxml import html

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SOMScraper(BaseScraper): # TODO Implement neuroscience as well 
    SCHOOL_ID = "SOM"
    CONTACT_BLOCK_NAME_XPATH = '//a[contains(@href, "?facbio")]'
    SOM_FACULTY_NAME_XPATH= '//h1[@class="post-title"]/text()'
    EMAIL_XPATH = '//a[starts-with(@href, "mailto:")]/@href'
    ABOUT_XPATH = '//h4[@class="faculty underlined-heading" and contains(text(), "Research Description")]'
    RESEARCH_INTERESTS_XPATH = '//h4[@class="faculty underlined-heading" and contains(text(), "Research Interests")]'
    RESEARCH_DISCIPLINES_XPATH = '//h4[@class="faculty underlined-heading" and contains(text(), "Research Disciplines")]'

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    def get_profile_endpoints_from_people(self, people_url: str) -> typing.List[str]:
        if not InstitutionUtils.is_valid_url(people_url):
            logger.error(f'Invalid URL: {people_url}')
            raise ValueError("Invalid URL")
        
        profile_urls = []

        try: # TODO: fix formatting of anchors to avoid extra logic extracting data from returned tuple 
            response = self.http_client.get(people_url) 
            tree = html.fromstring(response.content)
            anchors = tree.xpath(self.CONTACT_BLOCK_NAME_XPATH) # all anchor tags 
            links = [(anchor.get('href'), anchor.text_content()) for anchor in anchors] # tuple of form (url, faculty_name) where faculty_name has to be re-formated
            for href, text in links:
                profile_urls.append(str(href))

        except html.etree.XMLSyntaxError as e:
                logger.error(f"Failed to parse HTML for {[people_url]}: {e}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error processing page {people_url}: {e}")
            raise

        if not(profile_urls): # ensure url_list isn't empty if no prior errors were raised
            raise ValueError(f"There were no HTML errors, but no URLs were found. Are you sure `{self.CONTACT_BLOCK_NAME_XPATH}` is the correct XPATH and/or `{people_url}` is correct?")
        return list(dict.fromkeys(profile_urls)) # return list with no duplicates and order maintained since dictionary keys are unique 

    def get_name_from_profile(self, profile_url: str) -> str:
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f'Invalid URL: {profile_url}')
            raise

        try:
            response = self.http_client.get(profile_url) 
            tree = html.fromstring(response.content)
            name = tree.xpath(self.SOM_FACULTY_NAME_XPATH)

            if not name:
                raise ValueError(f"No name found using the XPATH `{self.SOM_FACULTY_NAME_XPATH}` for `{profile_url}`")

            parts = name[0].split(',', maxsplit=1)
            last_name = parts[0]
            first_name = parts[1].strip()  
            
            return f"{first_name} {last_name}" 
        
        except html.etree.XMLSyntaxError as e:
                logger.error(f"Failed to parse HTML for {profile_url}: {e}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error processing page {profile_url}: {e}")
            raise 
    
    def get_emails_from_profile(self, profile_url: str) -> typing.List[str]:
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f'Invalid URL: {profile_url}')
            raise ValueError("Invalid URL")
        try:
            response = self.http_client.get(profile_url)
            tree = html.fromstring(response.content)
            raw_emails = tree.xpath(self.EMAIL_XPATH)
            emails = {email.replace("mailto:", "").strip() for email in raw_emails}
            return list(emails)
        except html.etree.XMLSyntaxError as e:
            logger.error(f"Failed to parse HTML for {profile_url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing page {profile_url}: {e}")
            raise
    
    def get_about_from_profile(self, profile_url: str) -> str: # This fails for James E. Casanova https://med.virginia.edu/faculty/faculty-listing/jec9e/; why?
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f'Invalid URL: {profile_url}')
            raise ValueError("Invalid URL")
        
        try:
            response = self.http_client.get(profile_url)
            tree = html.fromstring(response.content)
            if not tree:
                logger.warning(f"No research description section text found for profile: {profile_url}")
                return ""
            else:
                research_description = self.extract_text_until_next_section(tree.xpath(self.ABOUT_XPATH)) 
                return research_description
        except Exception as e:
            logger.error(f"Unexpected error processing page {profile_url}: {e}")
            raise
        
    def get_research_interests_from_profile(self, profile_url: str) -> typing.List[str]:
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f'Invalid URL: {profile_url}')
            raise ValueError("Invalid URL")
        try:
            response = self.http_client.get(profile_url)
            tree = html.fromstring(response.content)
            research_disciplines = self.extract_text_until_next_section(tree.xpath(self.RESEARCH_DISCIPLINES_XPATH)) 
            research_interests = self.extract_text_until_next_section(tree.xpath(self.RESEARCH_INTERESTS_XPATH)) 
            if not research_disciplines and research_interests:
                logger.warning(f"No research interests section text found for profile: {profile_url}")
                return ""
            elif not research_disciplines:
                return research_interests
            elif not research_interests:
                return research_disciplines
            else:
                return f"{research_disciplines}, {research_interests}" # SOM webpages may have a research interest and research discipline section 
        except html.etree.XMLSyntaxError as e:
            logger.error(f"Failed to parse HTML for {profile_url}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error processing page {profile_url}: {e}")
            raise

    def extract_text_until_next_section(self, start_tag) -> str:
    # Check if start_tag is None or empty
        if not start_tag:
            return "The specified section could not be found."
        
        # Assume start_tag is a list, and we use the first element
        start_tag = start_tag[0]

        section_text = []
        for element in start_tag.itersiblings():
            if element.tag == 'h4':  # Stop if another <h4> is encountered
                break
            if element.tag in ('p',):  # Include only <p> tags
                # Add element text or a placeholder if text is None
                section_text.append(element.text.strip() if element.text else "Nothing was found for this section.")

        # Join the extracted text
        return "\n".join(section_text)


scraper = SOMScraper(HttpClient())

base_url = "https://med.virginia.edu/cell-biology/department-faculty/"

profile_urls = scraper.get_profile_endpoints_from_people(people_url=base_url)

name = scraper.get_name_from_profile(base_url + profile_urls[1])

# SOM =   {
#         "departments": {
#             "Cell Biology": {
#                 "people_url": "https://med.virginia.edu/cell-biology/department-faculty/",
#             },
#             "Biochemistry and Molecular Genetics": {
#                 "people_url": "https://med.virginia.edu/bmg/faculty/",
#             },
#             "Microbiology, Immunology, Cancer Biology": {
#                 "people_url": "https://med.virginia.edu/mic/faculty/primary-faculty/",
#             },
#             "Neuroscience": {
#                 "people_url": "https://med.virginia.edu/neuroscience/faculty/primary-faculty/",
#             },
#             "Molecular Physiology and Biological Physics": {
#                 "people_url": "https://med.virginia.edu/physiology-biophysics/faculty/",
#             },
#             "Pharmacology": {
#                 "people_url": "https://med.virginia.edu/pharm/primary-faculty/",
#             },
#         },
#     }

# SOM =   {
#         "departments": {
#             "Cell Biology": {
#                 "people_url": "https://med.virginia.edu/cell-biology/department-faculty/",
#             },
#             "Biochemistry and Molecular Genetics": {
#                 "people_url": "https://med.virginia.edu/bmg/faculty/",
#             },
#             "Microbiology, Immunology, Cancer Biology": {
#                 "people_url": "https://med.virginia.edu/mic/faculty/primary-faculty/",
#             },
#             "Molecular Physiology and Biological Physics": {
#                 "people_url": "https://med.virginia.edu/physiology-biophysics/faculty/",
#             },
#             "Pharmacology": {
#                 "people_url": "https://med.virginia.edu/pharm/primary-faculty/",
#             },
#         },
#     }

SOM =   {
        "departments": {
            "Cell Biology": {
                "people_url": "https://med.virginia.edu/cell-biology/department-faculty/",
            },
            "Pharmacology": {
                "people_url": "https://med.virginia.edu/pharm/primary-faculty/",
            },
        },
    }

 

for department, details in SOM["departments"].items():
    base_url = details.get("people_url")  # Safely get the URL
    profile_urls = scraper.get_profile_endpoints_from_people(people_url=base_url)

    names_per_dept = []

    for profile in profile_urls:
        name = scraper.get_name_from_profile(base_url + profile)
        names_per_dept.append(name)
        print(f"DEPT: {department} NAME: {name} EMAIL: {scraper.get_emails_from_profile(base_url + profile)} RESEARCH: {scraper.get_research_interests_from_profile(base_url + profile)} DESC: {scraper.get_about_from_profile(base_url + profile)}")
        
    
    print(f"Department URLs: {len(profile_urls)}; Names: {len(names_per_dept)}")