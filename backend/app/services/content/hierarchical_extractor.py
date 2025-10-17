#!/usr/bin/env python3
"""
Hierarchical Content Extractor
Preserves document structure and semantic relationships
"""
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from bs4 import BeautifulSoup
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ContentSection:
    """Represents a hierarchical content section"""
    heading: str
    level: int  # H1=1, H2=2, etc.
    content: str
    sub_sections: List['ContentSection']
    word_count: int
    semantic_phrases: List[str]


@dataclass
class HierarchicalDocument:
    """Complete hierarchical document structure"""
    title: str
    meta_description: str
    url: str
    sections: List[ContentSection]
    total_word_count: int
    structure_summary: Dict[str, int]  # level -> count


class HierarchicalContentExtractor:
    """
    Extracts content while preserving hierarchical structure
    """
    
    def __init__(self):
        self.logger = logger
    
    def extract_hierarchical_content(self, html: str, url: str) -> HierarchicalDocument:
        """
        Extract content with full hierarchical structure
        
        Args:
            html: Raw HTML content
            url: Source URL
            
        Returns:
            HierarchicalDocument with preserved structure
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Extract metadata
        title = self._extract_title(soup)
        meta_description = self._extract_meta_description(soup)
        
        # Extract hierarchical sections
        sections = self._extract_sections(soup)
        
        # Calculate totals
        total_word_count = sum(section.word_count for section in sections)
        structure_summary = self._calculate_structure_summary(sections)
        
        return HierarchicalDocument(
            title=title,
            meta_description=meta_description,
            url=url,
            sections=sections,
            total_word_count=total_word_count,
            structure_summary=structure_summary
        )
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title"""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        return ""
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description"""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            return meta_desc.get('content', '').strip()
        return ""
    
    def _extract_sections(self, soup: BeautifulSoup) -> List[ContentSection]:
        """Extract hierarchical sections from HTML"""
        sections = []
        
        # Find all heading elements
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        
        for i, heading in enumerate(headings):
            heading_text = heading.get_text().strip()
            level = int(heading.name[1])  # h1 -> 1, h2 -> 2, etc.
            
            # Find content under this heading
            content_text = self._extract_content_under_heading(heading, headings, i)
            
            # Extract semantic phrases from this section
            semantic_phrases = self._extract_semantic_phrases(heading_text + " " + content_text)
            
            section = ContentSection(
                heading=heading_text,
                level=level,
                content=content_text,
                sub_sections=[],  # Will be populated by hierarchical processing
                word_count=len(content_text.split()),
                semantic_phrases=semantic_phrases
            )
            
            sections.append(section)
        
        # Build hierarchical relationships
        sections = self._build_hierarchy(sections)
        
        return sections
    
    def _extract_content_under_heading(self, heading, all_headings: List, current_index: int) -> str:
        """Extract content that belongs under a specific heading"""
        content_parts = []
        
        # Get the next heading level to know when to stop
        current_level = int(heading.name[1])
        next_heading_index = None
        
        # Find the next heading at same or higher level
        for i in range(current_index + 1, len(all_headings)):
            next_level = int(all_headings[i].name[1])
            if next_level <= current_level:
                next_heading_index = i
                break
        
        # Find the parent container
        parent_container = heading.find_parent(['article', 'main', 'body'])
        if not parent_container:
            parent_container = heading.parent
        
        # Get all elements in the parent container
        all_elements = parent_container.find_all()
        
        # Find our heading in the list
        heading_index = None
        for i, element in enumerate(all_elements):
            if element == heading:
                heading_index = i
                break
        
        if heading_index is None:
            return ""
        
        # Collect content from elements after our heading until next heading
        for i in range(heading_index + 1, len(all_elements)):
            element = all_elements[i]
            
            # Stop if we hit the next heading
            if next_heading_index is not None:
                next_heading = all_headings[next_heading_index]
                if element == next_heading:
                    break
            
            # Skip script, style, nav, footer, header elements
            if element.name in ['script', 'style', 'nav', 'footer', 'header']:
                continue
            
            # Get text content from this element
            text = element.get_text(strip=True)
            if text and len(text) > 10:  # Only meaningful content
                content_parts.append(text)
        
        return " ".join(content_parts)
    
    def _extract_semantic_phrases(self, text: str) -> List[str]:
        """Extract meaningful phrases from text"""
        # Clean and normalize text
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Extract phrases of different lengths
        phrases = []
        words = text.split()
        
        # Single words (important terms)
        for word in words:
            if len(word) > 3 and word.isalpha():
                phrases.append(word.lower())
        
        # Two-word phrases
        for i in range(len(words) - 1):
            phrase = f"{words[i]} {words[i+1]}".lower()
            phrases.append(phrase)
        
        # Three-word phrases
        for i in range(len(words) - 2):
            phrase = f"{words[i]} {words[i+1]} {words[i+2]}".lower()
            phrases.append(phrase)
        
        # Remove duplicates and return
        return list(set(phrases))
    
    def _build_hierarchy(self, sections: List[ContentSection]) -> List[ContentSection]:
        """Build hierarchical relationships between sections"""
        hierarchical_sections = []
        stack = []  # Stack to track parent sections
        
        for section in sections:
            # Pop sections from stack that are at same or higher level
            while stack and stack[-1].level >= section.level:
                stack.pop()
            
            # Add as sub-section to parent if exists
            if stack:
                stack[-1].sub_sections.append(section)
            else:
                hierarchical_sections.append(section)
            
            # Push current section onto stack
            stack.append(section)
        
        return hierarchical_sections
    
    def _calculate_structure_summary(self, sections: List[ContentSection]) -> Dict[str, int]:
        """Calculate summary of document structure"""
        summary = {}
        
        def count_sections(sections_list):
            for section in sections_list:
                level_key = f"H{section.level}"
                summary[level_key] = summary.get(level_key, 0) + 1
                count_sections(section.sub_sections)
        
        count_sections(sections)
        return summary
    
    def to_flat_phrases(self, document: HierarchicalDocument) -> List[str]:
        """Convert hierarchical document to flat phrase list (for backward compatibility)"""
        phrases = []
        
        def extract_phrases(sections):
            for section in sections:
                phrases.extend(section.semantic_phrases)
                extract_phrases(section.sub_sections)
        
        extract_phrases(document.sections)
        return list(set(phrases))  # Remove duplicates
    
    def to_structured_phrases(self, document: HierarchicalDocument) -> List[Dict]:
        """Convert to structured phrase format with context"""
        structured_phrases = []
        
        def process_sections(sections, parent_context=""):
            for section in sections:
                context = f"{parent_context} > {section.heading}" if parent_context else section.heading
                
                for phrase in section.semantic_phrases:
                    structured_phrases.append({
                        "phrase": phrase,
                        "heading": section.heading,
                        "level": section.level,
                        "context": context,
                        "content_preview": section.content[:100] + "..." if len(section.content) > 100 else section.content
                    })
                
                process_sections(section.sub_sections, context)
        
        process_sections(document.sections)
        return structured_phrases


def get_hierarchical_extractor() -> HierarchicalContentExtractor:
    """Get singleton instance of hierarchical extractor"""
    if not hasattr(get_hierarchical_extractor, '_instance'):
        get_hierarchical_extractor._instance = HierarchicalContentExtractor()
    return get_hierarchical_extractor._instance
