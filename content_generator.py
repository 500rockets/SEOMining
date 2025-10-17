#!/usr/bin/env python3
"""
Content Generator - Turns Analysis Into Actual Content
Generates specific, ready-to-use content based on semantic gaps and competitor analysis
"""

import json
import random
from pathlib import Path
from datetime import datetime
import argparse

class ContentGenerator:
    def __init__(self, project_dir: str):
        self.project_dir = Path(project_dir)
        self.output_dir = self.project_dir / "10_content_generator"
        self.output_dir.mkdir(exist_ok=True)
        
        # Load data
        self.load_data()
        
    def load_data(self):
        """Load all analysis data"""
        # Load semantic gaps
        with open(self.project_dir / "06_optimization" / "semantic_gaps.json", 'r') as f:
            self.semantic_gaps = json.load(f)
            
        # Load competitive analysis
        with open(self.project_dir / "05_competitive_analysis" / "competitive_analysis.json", 'r') as f:
            self.competitive_analysis = json.load(f)
            
        # Load project config
        with open(self.project_dir / "00_config" / "project_config.json", 'r') as f:
            self.config = json.load(f)
            
    def generate_title_variations(self):
        """Generate multiple title options using semantic gaps"""
        
        # Get top semantic gaps
        top_gaps = sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[:10]
        
        # Extract key phrases
        key_phrases = [gap['phrase'] for gap in top_gaps[:5]]
        
        # Generate title variations
        titles = []
        
        # Pattern 1: [Key Phrase] + Guide/Framework
        for phrase in key_phrases[:3]:
            titles.extend([
                f"High Quality Message Building: {phrase.title()} Guide",
                f"The Complete {phrase.title()} Framework",
                f"How to Build {phrase.title()} for Better Results"
            ])
        
        # Pattern 2: Question-based titles
        titles.extend([
            f"What is {key_phrases[0].title()} and Why It Matters",
            f"How to Create {key_phrases[0].title()} That Converts",
            f"The Ultimate {key_phrases[0].title()} Strategy"
        ])
        
        # Pattern 3: Benefit-focused titles
        titles.extend([
            f"Build Better Messages with {key_phrases[0].title()}",
            f"Increase Conversions with {key_phrases[0].title()}",
            f"Master {key_phrases[0].title()} for Marketing Success"
        ])
        
        return titles[:15]  # Return top 15
        
    def generate_headings_structure(self):
        """Generate H1, H2, H3 structure using semantic gaps"""
        
        # Get high-usage gaps (used by 50%+ competitors)
        high_usage_gaps = [gap for gap in self.semantic_gaps if gap['competitor_usage_pct'] > 50]
        medium_usage_gaps = [gap for gap in self.semantic_gaps if 25 <= gap['competitor_usage_pct'] <= 50]
        
        structure = {
            "h1": f"High Quality Message Building: Complete {high_usage_gaps[0]['phrase'].title()} Guide",
            "h2_headings": [],
            "h3_headings": []
        }
        
        # H2 headings based on high-usage gaps
        for gap in high_usage_gaps[:5]:
            structure["h2_headings"].extend([
                f"What is {gap['phrase'].title()}?",
                f"How to Build {gap['phrase'].title()}",
                f"{gap['phrase'].title()} Best Practices",
                f"Common {gap['phrase'].title()} Mistakes to Avoid"
            ])
        
        # H3 headings based on medium-usage gaps
        for gap in medium_usage_gaps[:8]:
            structure["h3_headings"].extend([
                f"Understanding {gap['phrase'].title()}",
                f"Implementing {gap['phrase'].title()}",
                f"Measuring {gap['phrase'].title()} Success"
            ])
        
        return structure
        
    def generate_meta_description(self):
        """Generate meta description using semantic gaps"""
        
        # Get top 3 semantic gaps
        top_gaps = sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[:3]
        
        # Create variations
        descriptions = []
        
        for i, gap in enumerate(top_gaps):
            descriptions.append(
                f"Learn how to build high quality {gap['phrase']} with our comprehensive guide. "
                f"Discover proven strategies and frameworks for effective message building that drives results."
            )
            
            descriptions.append(
                f"Master the art of {gap['phrase']} with expert tips and best practices. "
                f"Create compelling messages that convert and build lasting customer relationships."
            )
            
            descriptions.append(
                f"Complete guide to {gap['phrase']}: strategies, frameworks, and examples "
                f"for building effective communication that resonates with your audience."
            )
        
        return descriptions[:5]  # Return top 5
        
    def generate_content_sections(self):
        """Generate actual content sections using semantic gaps"""
        
        # Get semantic gaps grouped by usage
        high_usage_gaps = [gap for gap in self.semantic_gaps if gap['competitor_usage_pct'] > 50]
        medium_usage_gaps = [gap for gap in self.semantic_gaps if 25 <= gap['competitor_usage_pct'] <= 50]
        
        sections = []
        
        # Section 1: Introduction using high-usage phrases
        intro_content = f"""## Introduction

Building high quality message building requires understanding the fundamentals of {high_usage_gaps[0]['phrase']} and how it impacts your marketing success. 

Your {high_usage_gaps[0]['phrase']} is crucial for effective communication. Learn how to develop a comprehensive {high_usage_gaps[0]['phrase']} that aligns with your brand values and resonates with your target audience.

In this guide, we'll explore:
- What {high_usage_gaps[0]['phrase']} means for your business
- How to create {high_usage_gaps[0]['phrase']} that converts
- Best practices for {high_usage_gaps[0]['phrase']} implementation
- Common mistakes to avoid in {high_usage_gaps[0]['phrase']}

Let's dive into the world of {high_usage_gaps[0]['phrase']} and discover how it can transform your marketing results."""
        
        sections.append(intro_content)
        
        # Section 2: Framework section using high-usage gaps
        framework_content = f"""## What is {high_usage_gaps[0]['phrase'].title()}?

{high_usage_gaps[0]['phrase'].title()} is the foundation of effective communication. It's not just about what you say, but how you say it and when you say it.

### Key Components of {high_usage_gaps[0]['phrase'].title()}:

1. **Strategic Foundation**: Your {high_usage_gaps[0]['phrase']} must align with your business goals
2. **Audience Understanding**: Know who you're speaking to and what they need
3. **Message Consistency**: Ensure your {high_usage_gaps[0]['phrase']} is consistent across all channels
4. **Value Proposition**: Clearly communicate what makes you different

### Why {high_usage_gaps[0]['phrase'].title()} Matters:

Building a successful {high_usage_gaps[0]['phrase']} requires understanding your audience, defining your value proposition, and creating consistent messaging across all channels. The key to effective {high_usage_gaps[0]['phrase']} lies in creating clear, compelling content that drives action and builds trust with your customers."""
        
        sections.append(framework_content)
        
        # Section 3: Implementation using medium-usage gaps
        implementation_content = f"""## How to Implement {high_usage_gaps[0]['phrase'].title()}

### Step 1: Define Your {medium_usage_gaps[0]['phrase'].title()}

Start by clearly defining your {medium_usage_gaps[0]['phrase']}. This involves:
- Identifying your core message
- Understanding your audience's pain points
- Creating a unique value proposition
- Developing key talking points

### Step 2: Create Your {medium_usage_gaps[1]['phrase'].title()} Strategy

Your {medium_usage_gaps[1]['phrase']} strategy should include:
- Channel-specific messaging
- Content calendar planning
- Brand voice guidelines
- Performance metrics

### Step 3: Test and Optimize

Regular testing and optimization are crucial for {high_usage_gaps[0]['phrase']} success:
- A/B test different messages
- Monitor engagement metrics
- Gather customer feedback
- Iterate based on results"""
        
        sections.append(implementation_content)
        
        # Section 4: Best Practices
        best_practices_content = f"""## {high_usage_gaps[0]['phrase'].title()} Best Practices

### 1. Focus on Your Audience

Your {high_usage_gaps[0]['phrase']} should always be audience-centric:
- Research your target market thoroughly
- Understand their challenges and goals
- Speak their language
- Address their specific needs

### 2. Maintain Consistency

Consistency is key to {high_usage_gaps[0]['phrase']} success:
- Use consistent terminology across all channels
- Maintain the same brand voice
- Align messaging with brand values
- Ensure visual consistency

### 3. Measure and Optimize

Track your {high_usage_gaps[0]['phrase']} performance:
- Monitor engagement rates
- Track conversion metrics
- Analyze customer feedback
- Continuously improve based on data"""
        
        sections.append(best_practices_content)
        
        return sections
        
    def generate_call_to_action(self):
        """Generate CTAs using semantic gaps"""
        
        top_gaps = sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[:3]
        
        ctas = []
        
        for gap in top_gaps:
            ctas.extend([
                f"Ready to improve your {gap['phrase']}? Contact us today for a free consultation.",
                f"Learn more about {gap['phrase']} and how it can transform your marketing results.",
                f"Get started with {gap['phrase']} today and see the difference it makes.",
                f"Discover the power of {gap['phrase']} for your business success.",
                f"Transform your marketing with effective {gap['phrase']} strategies."
            ])
        
        return ctas[:10]
        
    def generate_complete_content(self):
        """Generate complete, ready-to-use content"""
        
        # Generate all components
        titles = self.generate_title_variations()
        structure = self.generate_headings_structure()
        meta_descriptions = self.generate_meta_description()
        sections = self.generate_content_sections()
        ctas = self.generate_call_to_action()
        
        # Create complete content
        complete_content = f"""# {structure['h1']}

## Meta Description Options:
{chr(10).join([f"- {desc}" for desc in meta_descriptions])}

---

{chr(10).join(sections)}

## Call to Action

{random.choice(ctas)}

---

## Additional Title Options:
{chr(10).join([f"- {title}" for title in titles[5:]])}

---

## Heading Structure:
### H2 Headings:
{chr(10).join([f"- {h2}" for h2 in structure['h2_headings'][:8]])}

### H3 Headings:
{chr(10).join([f"- {h3}" for h3 in structure['h3_headings'][:12]])}

---

*Content generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Based on analysis of {len(self.semantic_gaps)} semantic gaps and {len(self.competitive_analysis.get('competitors', []))} competitors*
"""
        
        return complete_content
        
    def generate_keyword_variations(self):
        """Generate keyword variations for internal linking"""
        
        top_gaps = sorted(self.semantic_gaps, key=lambda x: x['estimated_impact'], reverse=True)[:20]
        
        keywords = {
            "primary_keywords": [],
            "secondary_keywords": [],
            "long_tail_keywords": [],
            "internal_linking_phrases": []
        }
        
        for gap in top_gaps:
            phrase = gap['phrase']
            
            # Primary keywords (high impact, high usage)
            if gap['competitor_usage_pct'] > 50:
                keywords["primary_keywords"].append(phrase)
            
            # Secondary keywords (medium impact, medium usage)
            elif gap['competitor_usage_pct'] > 25:
                keywords["secondary_keywords"].append(phrase)
            
            # Long-tail variations
            keywords["long_tail_keywords"].extend([
                f"how to {phrase}",
                f"best {phrase} practices",
                f"{phrase} strategy",
                f"{phrase} framework",
                f"effective {phrase}"
            ])
            
            # Internal linking phrases
            keywords["internal_linking_phrases"].extend([
                f"learn more about {phrase}",
                f"our {phrase} guide",
                f"comprehensive {phrase} resource",
                f"{phrase} best practices"
            ])
        
        return keywords
        
    def generate_all_content(self):
        """Generate all content components"""
        
        print("Generating complete content package...")
        
        # Generate main content
        complete_content = self.generate_complete_content()
        
        # Generate keyword variations
        keywords = self.generate_keyword_variations()
        
        # Save complete content
        with open(self.output_dir / 'COMPLETE_CONTENT.md', 'w', encoding='utf-8') as f:
            f.write(complete_content)
        
        # Save keyword variations
        with open(self.output_dir / 'KEYWORD_VARIATIONS.json', 'w', encoding='utf-8') as f:
            json.dump(keywords, f, indent=2, ensure_ascii=False)
        
        # Save individual components
        components = {
            "titles": self.generate_title_variations(),
            "meta_descriptions": self.generate_meta_description(),
            "headings_structure": self.generate_headings_structure(),
            "call_to_actions": self.generate_call_to_action()
        }
        
        with open(self.output_dir / 'CONTENT_COMPONENTS.json', 'w', encoding='utf-8') as f:
            json.dump(components, f, indent=2, ensure_ascii=False)
        
        print(f"Content generation complete: {self.output_dir}")
        print("\nGenerated files:")
        print("   COMPLETE_CONTENT.md - Ready-to-use content")
        print("   KEYWORD_VARIATIONS.json - SEO keywords and phrases")
        print("   CONTENT_COMPONENTS.json - Individual content pieces")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate actual content from analysis')
    parser.add_argument('--project-dir', default='./output/500rockets', 
                       help='Path to project directory')
    
    args = parser.parse_args()
    
    generator = ContentGenerator(args.project_dir)
    generator.generate_all_content()
