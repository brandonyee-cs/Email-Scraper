import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from time import sleep
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import random
from collections import defaultdict
import time
import json
from datetime import datetime, timedelta
from duckduckgo_search import ddg
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

load_dotenv()

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
EMAIL_REGEX = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
GOOGLE_CSE_ID = os.getenv('GOOGLE_CSE_ID')

if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
    raise ValueError("Missing required environment variables. Please check your .env file contains GOOGLE_API_KEY and GOOGLE_CSE_ID")

class RateLimiter:
    def __init__(self, requests_per_second=1):
        self.delay = 0.1 / requests_per_second
        self.last_request = defaultdict(float)
    
    def wait(self, domain):
        now = time.time()
        wait_time = self.last_request[domain] + self.delay - now
        if wait_time > 0:
            time.sleep(wait_time)
        self.last_request[domain] = time.time()

rate_limiter = RateLimiter(requests_per_second=0.5)

class ResultsCache:
    def __init__(self, cache_file='cache.json', expire_days=7):
        self.cache_file = cache_file
        self.expire_days = expire_days
        self.cache = self._load_cache()
    
    def _load_cache(self):
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def get(self, company):
        if company in self.cache:
            timestamp = datetime.fromisoformat(self.cache[company]['timestamp'])
            if datetime.now() - timestamp < timedelta(days=self.expire_days):
                return self.cache[company]['emails']
        return None
    
    def set(self, company, emails):
        self.cache[company] = {
            'emails': emails,
            'timestamp': datetime.now().isoformat()
        }
        self._save_cache()

    def _save_cache(self):
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f)

def get_possible_urls(company_name):
    """Generate possible website URLs from company name"""
    base = company_name.lower() \
        .replace(' ', '') \
        .replace("'", '') \
        .replace('&', 'and') \
        .replace(',', '') \
        .replace('.', '')
    return [
        f'https://www.{base}.com',
        f'https://{base}.com',
        f'https://www.{base}.org',
        f'https://{base}.org',
        f'https://www.{base}.net',
        f'https://{base}.net',
        f'https://www.{base}.co',
        f'https://{base}.co',
        *[f'https://{base.replace(" ", sep)}.com' for sep in ['-', '_']],
    ]

def verify_url(url):
    """Check if URL exists and is accessible"""
    try:
        response = requests.head(url, headers=HEADERS, timeout=10)
        return response.status_code == 200
    except:
        return False

def get_company_url(company_name):
    """Search for company website using Google Custom Search"""
    try:
        service = build("customsearch", "v1", developerKey=GOOGLE_API_KEY)
        result = service.cse().list(
            q=f"{company_name} official website",
            cx=GOOGLE_CSE_ID,  
            num=1
        ).execute()
        
        if 'items' in result:
            url = result['items'][0]['link']
            if not url.startswith('http'):
                url = 'https://' + url
            return url
        return None
    except Exception as e:
        print(f"Search error for {company_name}: {str(e)}")
        return None

def find_website_url(company_name):
    """Try to find company website URL"""
    url = get_company_url(company_name)
    if url and verify_url(url):
        return url
    return None

def create_session():
    """Create requests session with retry logic"""
    session = requests.Session()
    retries = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504]
    )
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

def get_proxy():
    """Rotate through proxy servers"""
    PROXY_LIST = [
        'http://proxy1.example.com:8080',
        'http://proxy2.example.com:8080'
    ]
    return random.choice(PROXY_LIST)

def scrape_emails(url, session):
    """Scrape emails from a webpage"""
    try:
        response = session.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        emails = set()
        
        for link in soup.select('a[href^="mailto:"]'):
            try:
                href = link['href'].lower()
                email = href.split('mailto:')[1].split('?')[0]
                if EMAIL_REGEX.match(email):
                    emails.add(email)
            except:
                continue
        
        try:
            text = soup.get_text().lower()
            found_emails = EMAIL_REGEX.findall(text)
            emails.update(found_emails)
        except:
            pass
        
        return list(emails)
    except Exception as e:
        print(f"Error scraping {url}: {str(e)}")
        return []

def validate_email(email):
    """More thorough email validation"""
    INVALID_PATTERNS = {
        'noreply@', 'no-reply@', 'donotreply@',
    }
    
    email = email.lower()
    
    if any(pattern in email for pattern in INVALID_PATTERNS):
        return False
        
    return True

def get_contact_pages(base_url):
    """Get list of pages likely to contain contact info"""
    return [
        f"{base_url.rstrip('/')}/contact",
        f"{base_url.rstrip('/')}/contact-us",
        f"{base_url.rstrip('/')}/about",
        f"{base_url.rstrip('/')}/about-us",
        f"{base_url.rstrip('/')}/support",
        f"{base_url.rstrip('/')}/help",
    ]

def scrape_site(url):
    """Scrape multiple pages on site"""
    emails = set()
    session = create_session()
    
    domain = url.split('/')[2]
    rate_limiter.wait(domain)
    
    homepage_emails = scrape_emails(url, session)
    if homepage_emails:
        emails.update(homepage_emails)
    
    for page_url in get_contact_pages(url):
        try:
            rate_limiter.wait(domain)
            page_emails = scrape_emails(page_url, session)
            if page_emails:
                emails.update(page_emails)
        except Exception as e:
            print(f"Error scraping contact page {page_url}: {str(e)}")
            continue
    
    valid_emails = [email for email in emails if validate_email(email)]
    return valid_emails

def load_companies(filename='companies.txt'):
    """Load company names from text file"""
    try:
        with open(filename, 'r') as f:
            companies = [line.strip() for line in f if line.strip()]
        return companies
    except Exception as e:
        print(f"Error loading companies from {filename}: {str(e)}")
        return []

def scrape_companies():
    """Main function to scrape company emails"""
    print("Starting scraper run")
    
    companies = load_companies()
    if not companies:
        print("Error: No companies loaded from companies.txt")
        return None
    
    print(f"Loaded {len(companies)} companies")
    results = []
    cache = ResultsCache()
    
    for company in companies:
        print(f"\nProcessing: {company}")
        try:
            cached_emails = cache.get(company)
            if cached_emails:
                print(f"  Found cached emails: {', '.join(cached_emails)}")
                results.append({'Company': company, 'Emails': ', '.join(cached_emails)})
                continue
            
            url = find_website_url(company)
            
            if not url:
                print(f"  No website found for {company}")
                results.append({'Company': company, 'Emails': 'No website found'})
                continue
            
            print(f"  Found website: {url}")
            
            emails = scrape_site(url)
            
            if emails:
                print(f"  Found emails: {', '.join(emails)}")
                results.append({'Company': company, 'Emails': ', '.join(emails)})
                cache.set(company, emails)
            else:
                print(f"  No emails found for {company}")
                results.append({'Company': company, 'Emails': 'Not found'})
            
        except Exception as e:
            error_msg = str(e)
            print(f"Error processing {company}: {error_msg}")
            results.append({'Company': company, 'Emails': f'Error: {error_msg}'})
            continue
    
    return pd.DataFrame(results)