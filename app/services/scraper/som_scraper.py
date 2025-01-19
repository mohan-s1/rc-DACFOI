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

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    def get_profile_endpoints_from_people(self, people_url: str) -> typing.List[str]: # only one page, so no need for for max_pages unlike SEAS sites
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

        if len(profile_urls) == 0: # ensure url_list isn't empty if no prior errors were raised
            raise ValueError(f"There were no HTML errors, but no URLs were found. Are you sure `{self.CONTACT_BLOCK_NAME_XPATH}` is the correct XPATH and/or `{people_url}` is correct?")
        return profile_urls

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
            
            return f"{first_name} {last_name}" # TODO: Find out why Molecular Physiology and Biological Physics, Pharmacology returns names twice 
        
        except html.etree.XMLSyntaxError as e:
                logger.error(f"Failed to parse HTML for {profile_url}: {e}")
                raise
        except Exception as e:
            logger.error(f"Unexpected error processing page {profile_url}: {e}")
            raise # maybe use RuntimeError instead?        
    
    def get_emails_from_profile(self, profile_url: str) -> typing.List[str]:
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f'Invalid URL: {profile_url}')
            raise ValueError("Invalid URL")
    
    def get_about_from_profile(self, profile_url: str) -> str:
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f'Invalid URL: {profile_url}')
            raise ValueError("Invalid URL")
        
    def get_research_interests_from_profile(self, profile_url: str) -> typing.List[str]:
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f'Invalid URL: {profile_url}')
            raise ValueError("Invalid URL")

scraper = SOMScraper(HttpClient())

base_url = "https://med.virginia.edu/cell-biology/department-faculty/"

profile_urls = scraper.get_profile_endpoints_from_people(people_url=base_url)

name = scraper.get_name_from_profile(base_url + profile_urls[1])

SOM =   {
        "departments": {
            "Cell Biology": {
                "people_url": "https://med.virginia.edu/cell-biology/department-faculty/",
            },
            "Biochemistry and Molecular Genetics": {
                "people_url": "https://med.virginia.edu/bmg/faculty/",
            },
            "Microbiology, Immunology, Cancer Biology": {
                "people_url": "https://med.virginia.edu/mic/faculty/primary-faculty/",
            },
            "Molecular Physiology and Biological Physics": {
                "people_url": "https://med.virginia.edu/physiology-biophysics/faculty/",
            },
            "Pharmacology": {
                "people_url": "https://med.virginia.edu/pharm/primary-faculty/",
            },
        },
    }

for department, details in SOM["departments"].items():
    base_url = details.get("people_url")  # Safely get the URL
    print(f"{department}: {base_url}")

    profile_urls = scraper.get_profile_endpoints_from_people(people_url=base_url)

    names_per_dept = []

    for profile in profile_urls:
        name = scraper.get_name_from_profile(base_url + profile)
        names_per_dept.append(name)
        print(f"{department}: {name}")
    
    print(f"Department URLs: {len(profile_urls)}; Names: {len(names_per_dept)}")