# Reading List PDF Generator

This tool generates PDF reading lists from your Pinboard bookmarks, perfect for reading on devices like the reMarkable 2.

## Features

- Fetches recent bookmarks from your Pinboard RSS feed
- Generates A4-sized PDFs optimized for e-readers
- Includes table of contents for easy navigation
- Can filter out articles with specific tags (e.g., "read" articles)
- Uses percollate for high-quality PDF generation

## Requirements

- Python 3
- Node.js with percollate installed globally (`npm install -g percollate`)
- Internet connection to fetch articles

## Usage

```bash
# Generate PDF with 10 most recent articles
python3 generate-reading-pdf.py

# Generate PDF with 5 articles, custom filename
python3 generate-reading-pdf.py 5 my-reading-list.pdf

# Exclude articles tagged as "read" or "archived"
python3 generate-reading-pdf.py 10 reading-list.pdf --exclude-tags read,archived

# Show help
python3 generate-reading-pdf.py --help
```

## Configuration

The script defaults to fetching from `https://feeds.pinboard.in/rss/u:williballenthin/`. To use with a different Pinboard account, modify the `fetch_pinboard_rss()` function in the script.

## Output

Generates a PDF with:
- A4 page format with 2cm margins
- Table of contents
- Article titles, content, and metadata
- Optimized for reading on tablets and e-readers

## Integration

This tool is designed to be integrated into GitHub Actions workflows for automatic generation and hosting of reading lists.
