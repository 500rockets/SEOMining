#!/usr/bin/env python3
"""Test the fixed content extraction"""

import sys
sys.path.append('/app')
from app.services.scraping.service import ScrapingService

# Test the fixed extraction
service = ScrapingService()

html = """<html>
<head>
<title>Marketing Agency Services - 500 Rockets</title>
<meta name="description" content="Professional digital marketing services for growing businesses.">
</head>
<body>
<h1>Marketing Agency Services</h1>
<p>We provide comprehensive digital marketing services including SEO, PPC, social media marketing, and content creation.</p>
<p>Our team of experts helps businesses grow their online presence and reach their target audience effectively.</p>
<p>Contact us today to learn more about our services and how we can help your business succeed online.</p>
</body>
</html>"""

result = service.extract_content(html, 'https://500rockets.io')
print('Extraction result:')
print('Method:', result.get('extraction_method'))
print('Title:', result.get('title'))
print('Text length:', result.get('content_length'))
print('Word count:', result.get('word_count'))
print('First 200 chars:', result.get('text', '')[:200])
