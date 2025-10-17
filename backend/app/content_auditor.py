#!/usr/bin/env python3
"""
Content Audit and Re-analysis Tool
Allows auditing raw scraped data and re-analyzing with different methods
"""
import json
import os
import sys
from pathlib import Path
from datetime import datetime

# Add the app directory to Python path
sys.path.append('/app')

from app.services.content import get_hierarchical_extractor


class ContentAuditor:
    """Audit and re-analyze scraped content"""
    
    def __init__(self, project_name: str = "500rockets"):
        self.project_name = project_name
        self.project_dir = Path(f"/app/projects/{project_name}")
        self.backup_dir = self.project_dir / "03_competitor_content" / "raw_backups"
        self.extracted_dir = self.project_dir / "03_competitor_content" / "extracted_content"
        
    def list_backups(self):
        """List all available raw backups"""
        print("=" * 60)
        print("  RAW CONTENT BACKUPS")
        print("=" * 60)
        
        if not self.backup_dir.exists():
            print("❌ No backup directory found")
            return []
        
        backup_files = list(self.backup_dir.glob("*.json"))
        
        if not backup_files:
            print("❌ No backup files found")
            return []
        
        print(f"📁 Found {len(backup_files)} backup files:")
        print()
        
        for i, file in enumerate(backup_files, 1):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                print(f"{i:2d}. {file.name}")
                print(f"    URL: {data.get('url', 'N/A')}")
                print(f"    Title: {data.get('title', 'N/A')}")
                print(f"    Content Length: {data.get('content_length', 0)} chars")
                print(f"    Word Count: {data.get('word_count', 0)} words")
                print(f"    Query: {data.get('query', 'N/A')}")
                print(f"    Ranking: #{data.get('serp_ranking', 'N/A')}")
                print()
                
            except Exception as e:
                print(f"{i:2d}. {file.name} - ERROR: {e}")
                print()
        
        return backup_files
    
    def audit_backup(self, filename: str):
        """Audit a specific backup file"""
        backup_file = self.backup_dir / filename
        
        if not backup_file.exists():
            print(f"❌ Backup file not found: {filename}")
            return
        
        print("=" * 60)
        print(f"  AUDITING: {filename}")
        print("=" * 60)
        
        with open(backup_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"URL: {data.get('url', 'N/A')}")
        print(f"Title: {data.get('title', 'N/A')}")
        print(f"Query: {data.get('query', 'N/A')}")
        print(f"SERP Ranking: #{data.get('serp_ranking', 'N/A')}")
        print(f"Scraping Timestamp: {data.get('scraping_timestamp', 'N/A')}")
        print()
        
        # Check raw HTML
        raw_html = data.get('raw_html', '')
        if raw_html:
            print(f"✅ Raw HTML available: {len(raw_html)} characters")
            
            # Quick HTML structure analysis
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(raw_html, 'html.parser')
            
            headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            print(f"📋 Document structure:")
            print(f"   - H1 tags: {len(soup.find_all('h1'))}")
            print(f"   - H2 tags: {len(soup.find_all('h2'))}")
            print(f"   - H3 tags: {len(soup.find_all('h3'))}")
            print(f"   - Total headings: {len(headings)}")
            
            if headings:
                print(f"   - First few headings:")
                for i, heading in enumerate(headings[:5]):
                    print(f"     {i+1}. {heading.name.upper()}: {heading.get_text().strip()[:80]}...")
        else:
            print("❌ No raw HTML available")
        
        print()
        
        # Check extracted content
        extracted_text = data.get('extracted_text', '')
        if extracted_text:
            print(f"✅ Extracted text available: {len(extracted_text)} characters")
            print(f"   Word count: {len(extracted_text.split())} words")
            print(f"   Preview: {extracted_text[:200]}...")
        else:
            print("❌ No extracted text available")
        
        print()
    
    def reanalyze_with_hierarchy(self, filename: str):
        """Re-analyze content using hierarchical extraction"""
        backup_file = self.backup_dir / filename
        
        if not backup_file.exists():
            print(f"❌ Backup file not found: {filename}")
            return
        
        print("=" * 60)
        print(f"  HIERARCHICAL RE-ANALYSIS: {filename}")
        print("=" * 60)
        
        with open(backup_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        raw_html = data.get('raw_html', '')
        if not raw_html:
            print("❌ No raw HTML available for re-analysis")
            return
        
        # Use hierarchical extractor
        extractor = get_hierarchical_extractor()
        document = extractor.extract_hierarchical_content(raw_html, data.get('url', ''))
        
        print(f"📄 Document: {document.title}")
        print(f"📝 Meta Description: {document.meta_description}")
        print(f"📊 Total Word Count: {document.total_word_count}")
        print()
        
        print("🏗️  Document Structure:")
        for level, count in document.structure_summary.items():
            print(f"   {level}: {count} sections")
        print()
        
        print("📋 Hierarchical Sections:")
        self._print_sections(document.sections, indent=0)
        
        # Save hierarchical analysis
        analysis_file = self.project_dir / "03_competitor_content" / "hierarchical_analysis" / filename
        analysis_file.parent.mkdir(exist_ok=True)
        
        analysis_data = {
            "url": document.url,
            "title": document.title,
            "meta_description": document.meta_description,
            "total_word_count": document.total_word_count,
            "structure_summary": document.structure_summary,
            "sections": self._serialize_sections(document.sections),
            "flat_phrases": extractor.to_flat_phrases(document),
            "structured_phrases": extractor.to_structured_phrases(document),
            "analysis_timestamp": datetime.now().isoformat(),
            "original_backup": filename
        }
        
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Hierarchical analysis saved to: {analysis_file}")
        print()
    
    def _print_sections(self, sections, indent=0):
        """Print sections with proper indentation"""
        for section in sections:
            prefix = "  " * indent
            print(f"{prefix}📌 {section.heading} (H{section.level})")
            print(f"{prefix}   Content: {section.content[:100]}...")
            print(f"{prefix}   Phrases: {len(section.semantic_phrases)} phrases")
            
            if section.sub_sections:
                self._print_sections(section.sub_sections, indent + 1)
    
    def _serialize_sections(self, sections):
        """Serialize sections for JSON storage"""
        serialized = []
        for section in sections:
            serialized.append({
                "heading": section.heading,
                "level": section.level,
                "content": section.content,
                "word_count": section.word_count,
                "semantic_phrases": section.semantic_phrases,
                "sub_sections": self._serialize_sections(section.sub_sections)
            })
        return serialized
    
    def compare_extraction_methods(self, filename: str):
        """Compare different extraction methods"""
        backup_file = self.backup_dir / filename
        
        if not backup_file.exists():
            print(f"❌ Backup file not found: {filename}")
            return
        
        with open(backup_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        raw_html = data.get('raw_html', '')
        extracted_text = data.get('extracted_text', '')
        
        if not raw_html:
            print("❌ No raw HTML available for comparison")
            return
        
        print("=" * 60)
        print(f"  EXTRACTION METHOD COMPARISON: {filename}")
        print("=" * 60)
        
        # Original extraction
        print("📄 ORIGINAL EXTRACTION:")
        print(f"   Method: {data.get('extraction_method', 'unknown')}")
        print(f"   Length: {len(extracted_text)} chars")
        print(f"   Words: {len(extracted_text.split())} words")
        print(f"   Preview: {extracted_text[:200]}...")
        print()
        
        # Hierarchical extraction
        extractor = get_hierarchical_extractor()
        document = extractor.extract_hierarchical_content(raw_html, data.get('url', ''))
        
        print("🏗️  HIERARCHICAL EXTRACTION:")
        print(f"   Sections: {len(document.sections)} top-level sections")
        print(f"   Total words: {document.total_word_count} words")
        print(f"   Structure: {document.structure_summary}")
        
        flat_text = " ".join([section.content for section in document.sections])
        print(f"   Flat text length: {len(flat_text)} chars")
        print(f"   Preview: {flat_text[:200]}...")
        print()
        
        # Comparison
        print("📊 COMPARISON:")
        print(f"   Original vs Hierarchical word count: {len(extracted_text.split())} vs {document.total_word_count}")
        print(f"   Difference: {document.total_word_count - len(extracted_text.split())} words")
        
        if document.total_word_count > len(extracted_text.split()):
            print("   ✅ Hierarchical extraction captured more content")
        elif document.total_word_count < len(extracted_text.split()):
            print("   ⚠️  Original extraction captured more content")
        else:
            print("   ⚖️  Both methods captured similar content")


def main():
    """Main function for content auditing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Content Audit and Re-analysis Tool')
    parser.add_argument('--project', default='500rockets', help='Project name')
    parser.add_argument('--action', choices=['list', 'audit', 'reanalyze', 'compare'], 
                       default='list', help='Action to perform')
    parser.add_argument('--file', help='Specific file to audit/reanalyze')
    
    args = parser.parse_args()
    
    auditor = ContentAuditor(args.project)
    
    if args.action == 'list':
        auditor.list_backups()
    elif args.action == 'audit':
        if not args.file:
            print("❌ --file required for audit action")
            return
        auditor.audit_backup(args.file)
    elif args.action == 'reanalyze':
        if not args.file:
            print("❌ --file required for reanalyze action")
            return
        auditor.reanalyze_with_hierarchy(args.file)
    elif args.action == 'compare':
        if not args.file:
            print("❌ --file required for compare action")
            return
        auditor.compare_extraction_methods(args.file)


if __name__ == "__main__":
    main()
