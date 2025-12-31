# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "imap-tools",
#     "python-dateutil",
#     "pytest",
# ]
# ///

from datetime import datetime, timezone
import pytest

# Helper to import the script module which is in tools/email-to-links/process_emails.py
# Since it's a script not a module, we can import it if we add __init__.py or just use importlib.
# Given the directory structure 'tools/email-to-links', let's use importlib to load it
import importlib.util
import sys
import os

spec = importlib.util.spec_from_file_location("process_emails", "tools/email-to-links/process_emails.py")
process_emails_module = importlib.util.module_from_spec(spec)
sys.modules["process_emails"] = process_emails_module
spec.loader.exec_module(process_emails_module)

def test_clean_subject():
    assert process_emails_module.clean_subject("Link: Cool Article") == "Cool Article"
    assert process_emails_module.clean_subject("link:Cool Article") == "Cool Article"
    assert process_emails_module.clean_subject("LINK:   Cool Article  ") == "Cool Article"
    assert process_emails_module.clean_subject("Just a Subject") == "Just a Subject"
    assert process_emails_module.clean_subject("") == "No Title"

def test_extract_url_and_tags_basic():
    # Basic URL + Tag
    body = "Check this: https://example.com #cool"
    url, tags = process_emails_module.extract_url_and_tags(body)
    assert url == "https://example.com"
    assert tags == ["cool"]

    # Multiple URLs (take first)
    body = "https://first.com and https://second.com"
    url, tags = process_emails_module.extract_url_and_tags(body)
    assert url == "https://first.com"
    assert tags == []

    # Complex Tags
    body = "https://site.com #python #web_dev"
    url, tags = process_emails_module.extract_url_and_tags(body)
    assert url == "https://site.com"
    assert tags == ["python", "web_dev"]

    # No URL
    body = "Just text #tag"
    url, tags = process_emails_module.extract_url_and_tags(body)
    assert url is None
    assert tags == ["tag"]

    # No Tags
    body = "https://site.com"
    url, tags = process_emails_module.extract_url_and_tags(body)
    assert url == "https://site.com"
    assert tags == []

def test_generate_markdown_content():
    title = "My Title"
    date_obj = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    url = "https://example.com"
    tags = ["one", "two"]

    slug, content = process_emails_module.generate_markdown_content(title, date_obj, url, tags)

    assert slug == "20240101T120000"
    assert "title: My Title" in content
    assert "slug: 20240101T120000" in content
    assert "date: 2024-01-01T12:00:00+00:00" in content
    assert "url: https://example.com" in content
    assert "- one" in content
    assert "- two" in content

    # Test special characters in title (YAML escaping)
    title_special = 'Title: with "quotes" and \'apostrophes\''
    slug_special, content_special = process_emails_module.generate_markdown_content(title_special, date_obj, url, tags)
    assert "---" in content_special
    # Should not break YAML parsing
    import yaml
    try:
        # Extract frontmatter between --- delimiters
        parts = content_special.split('---')
        frontmatter_yaml = parts[1]
        parsed = yaml.safe_load(frontmatter_yaml)
        assert parsed['title'] == title_special
    except yaml.YAMLError:
        assert False, "Generated YAML should be valid"


def test_extract_url_and_tags_html():
    # URL in HTML <a> tag
    body = 'Check this out: <a href="https://example.com">Example Site</a> #cool'
    url, tags = process_emails_module.extract_url_and_tags(body)
    assert url == "https://example.com"
    assert tags == ["cool"]

    # Multiple <a> tags (take first)
    body = 'Links: <a href="https://first.com">First</a> and <a href="https://second.com">Second</a>'
    url, tags = process_emails_module.extract_url_and_tags(body)
    assert url == "https://first.com"
    assert tags == []

    # HTML with tags
    body = '<p>Check out <a href="https://site.com">this site</a> for #python #tutorials</p>'
    url, tags = process_emails_module.extract_url_and_tags(body)
    assert url == "https://site.com"
    assert tags == ["python", "tutorials"]

    # Mixed HTML and plain text
    body = 'Some text <a href="https://example.com">link</a> more text #tag'
    url, tags = process_emails_module.extract_url_and_tags(body)
    assert url == "https://example.com"
    assert tags == ["tag"]

    # Complex HTML email
    body = '''<html><body>
    <p>Hi there,</p>
    <p>Check out this article: <a href="https://blog.example.com/article">Great Article</a></p>
    <p>It covers #webdev #javascript topics.</p>
    <p>Best regards,<br>Someone</p>
    </body></html>'''
    url, tags = process_emails_module.extract_url_and_tags(body)
    assert url == "https://blog.example.com/article"
    assert tags == ["webdev", "javascript"]

def test_extract_url_and_tags_edge_cases():
    # Invalid HTML should fallback to text parsing
    body = 'Broken <a href="https://example.com>link #tag'
    url, tags = process_emails_module.extract_url_and_tags(body)
    assert url == "https://example.com"
    assert tags == ["tag"]

    # No href in <a> tag, should find plain text URL
    body = 'Link: <a>https://example.com</a> #tag'
    url, tags = process_emails_module.extract_url_and_tags(body)
    assert url == "https://example.com"
    assert tags == ["tag"]

    # Relative URL in href should be ignored, find plain text URL
    body = 'Link: <a href="/relative">text</a> and https://example.com #tag'
    url, tags = process_emails_module.extract_url_and_tags(body)
    assert url == "https://example.com"
    assert tags == ["tag"]