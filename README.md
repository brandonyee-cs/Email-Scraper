# Company Email Scrapers

A Python script that finds company contact information using Google Custom Search API and web scraping.

## Features

- Uses Google Custom Search API for accurate website discovery
- Scrapes email addresses from:
  - Homepage content
  - Contact pages
  - Mailto links
- Caches results to avoid re-scraping
- Rate limiting to respect website access
- Exports results to CSV format

## Requirements

```bash
pip install -r requirements.txt
```

## Configuration

1. Create a `.env` file in the project root:
```
GOOGLE_API_KEY = 'your_google_api_key'
GOOGLE_CSE_ID = 'your_google_cse_id'
```

2. Get your API credentials:
   - Create a Google Cloud Project
   - Enable the Custom Search API
   - Create an API key
   - Create a Custom Search Engine (CSE) and get its ID

3. Add company names to `companies.txt`, one per line

## Usage

```bash
python scraper.py
```

Results will be saved to `sponsorship_contacts.csv`

## Output Format

The script generates a CSV file with:
- `Company`: Company name
- `Emails`: Found email addresses or status message

## Settings

Adjustable constants in `scraper.py`:
- `HEADERS`: User agent for web requests
- `SLEEP_TIME`: Delay between requests (default: 0.1 seconds)
- `EMAIL_REGEX`: Pattern for matching email addresses

## Notes

- Uses caching to avoid repeated requests
- Implements rate limiting for respectful scraping
- Some websites may block automated access
- Results depend on website structure and API availability

## Legal Considerations

Ensure compliance with:
- Google API terms of service
- Website terms of service
- Robot exclusion standards
- Local data protection laws
- Rate limiting requirements

## License

This project is open source and available under the MIT License.