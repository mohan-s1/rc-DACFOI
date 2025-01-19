import typing
import logging

from app.utils.http_client import HttpClient
from app.utils.institution_utils import InstitutionUtils
from app.services.scraper.base_scraper import BaseScraper
from lxml import html

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SOMScraper(BaseScraper):



    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    def get_profile_endpoints_from_people(self, people_url: str) -> typing.List[str]: # only one page, so no need for for max_pages unlike SEAS sites
        if not InstitutionUtils.is_valid_url(people_url):
            logger.error(f'Invalid URL: {people_url}')
            raise ValueError("Invalid URL")
        
        profile_urls = []

    def get_name_from_profile(self, profile_url: str) -> str:
        if not InstitutionUtils.is_valid_url(profile_url):
            logger.error(f'Invalid URL: {profile_url}')
            raise
    
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
