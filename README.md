# Company Email Scrapers

This repository contains two Python scripts for finding company contact information:
1. A basic web scraper (`scraper.py`)
2. An API-enhanced scraper (`newscraper.py`) using Marcom Robot API

## Features

### Basic Scraper (scraper.py)
- Generates and verifies possible company website URLs
- Uses pattern matching to find company domains
- Scrapes email addresses from homepage and contact pages

### API Scraper (newscraper.py)
- Uses Marcom Robot API for accurate company domain lookup
- More reliable domain identification
- Enhanced email scraping with API verification
- Better rate limiting and error handling

## Requirements

```bash
pip install requests beautifulsoup4 pandas
```

## Usage

### Basic Scraper
```python
# 1. Edit companies list in scraper.py
# 2. Run:
python scraper.py
```

### API Scraper
```python
# 1. Add your Marcom Robot API key to newscraper.py
# 2. Edit companies list
# 3. Run:
python newscraper.py
```

## Configuration

### scraper.py Settings
- `HEADERS`: User agent for web requests
- `SLEEP_TIME`: Delay between requests (default: 2 seconds)
- `EMAIL_REGEX`: Pattern for matching email addresses

### newscraper.py Settings
- `API_KEY`: Your Marcom Robot API key
- `API_URL`: API endpoint URL
- `SLEEP_TIME`: API request delay (default: 1 second)
- `HEADERS`: API request headers

## Output Format

Both scripts generate a CSV file (`sponsorship_contacts.csv`) with:
- `Company`: Company name
- `Emails`: Found email addresses or status message

## Choosing a Scraper

### Use scraper.py when:
- You don't have an API key
- You're working with a small list of companies
- You want a simple, dependency-light solution

### Use newscraper.py when:
- You have a Marcom Robot API key
- You need more accurate domain identification
- You're working with a large company list
- You need better error handling and reliability

## Notes

- Both scripts implement rate limiting
- Some websites may block automated access
- Results depend on website structure and security
- API scraper requires valid API key and may have usage limits

## Legal Considerations

Ensure compliance with:
- Website terms of service
- Robot exclusion standards
- API terms of service
- Local data protection laws
- Rate limiting requirements

## License

This project is open source and available under the MIT License.