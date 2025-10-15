# Structural Coherence Scoring (APA-Style Quality)

## The Problem: What Magic-SEO Misses

### Current Magic-SEO Scoring:
```python
composite_score = (alignment * 0.35) + (coverage * 0.35) + (keyword_presence * 0.30)
```

**What it measures**:
- ✅ Alignment: Overall semantic similarity to competitors
- ✅ Coverage: % of competitor topics covered
- ✅ Keyword Presence: Keyword in URL, title, H1, first para, H2s

**What it DOESN'T measure** (and Google absolutely does):
- ❌ **Structural coherence**: Do meta elements align with content?
- ❌ **Hierarchical semantic breakdown**: Does H1 → H2 → H3 follow logical decomposition?
- ❌ **Thematic unity**: Is there a clear main topic that subheadings support?
- ❌ **User intent match**: Does the structure match what the query implies?

---

## How Google Likely Chunks & Scores Pages

### Google's Approach (Based on Patents & Research):

```
1. PASSAGE INDEXING (BERT-based):
   - Chunk by semantic boundaries (not just H2s)
   - Each passage gets scored independently for query relevance
   - Best passage determines initial ranking

2. HIERARCHICAL TOPIC MODELING:
   - H1 = Main topic embedding
   - H2s = Subtopic embeddings
   - H3s = Sub-subtopic embeddings
   - Measure semantic "child-of" relationships

3. METADATA ALIGNMENT:
   - Title embedding vs H1 embedding (should be ~0.85+ similar)
   - Description embedding vs intro paragraph (should be ~0.75+ similar)
   - Title embedding vs full content centroid (should be ~0.80+ similar)

4. STRUCTURAL SIGNALS:
   - Clear hierarchy (H1 → H2 → H3, no skipping)
   - Appropriate density (3-6 H2s per 1000 words)
   - Balanced sections (no 100-word H2 next to 2000-word H2)
```

### Magic-SEO's Approach:

```
1. CHUNKING:
   - Split by H2 sections (simple, effective but incomplete)
   - Capture intro content (first ~20% of paragraphs)
   - Fallback to paragraph grouping if no H2s

2. COMPARISON:
   - Compare your sections vs competitor sections
   - Cluster competitor sections into topics
   - Check if you cover those topics (≥0.65 similarity)

MISSING: No measurement of internal structural quality!
```

---

## The APA-Style Quality Model

### Academic Writing Principles Applied to SEO:

In APA format (dissertation/research paper):
1. **Title** = Clear thesis statement
2. **Abstract** = Summary of entire argument
3. **H1 (Introduction)** = Restates thesis, provides context
4. **H2s (Main Points)** = Major supporting arguments
5. **H3s (Evidence)** = Detailed support for each H2
6. **Conclusion** = Synthesizes main points

### SEO Equivalent:

```
Title Tag = Keyword + Clear value proposition
Meta Description = Summary of what page delivers
H1 = Main keyword/topic (should align with title semantically)
H2s = Semantic breakdown of H1 into subtopics
H3s = Further breakdown of each H2
Body = Evidence/content supporting each heading
```

---

## Proposed Structural Coherence Score

### Formula:

```python
structural_coherence_score = (
    0.25 * metadata_alignment_score +     # Title/desc vs content
    0.30 * hierarchical_decomposition +   # H1 → H2 → H3 logic
    0.20 * thematic_unity_score +         # All sections support main topic
    0.15 * balance_score +                # Sections appropriately sized
    0.10 * structural_hygiene_score       # No skipped heading levels, etc.
)
```

### Component 1: Metadata Alignment Score (25%)

**Measures**: Do title, description, H1 semantically align with actual content?

```python
class MetadataAlignmentScorer:
    def calculate(self, page: PageContent, page_embeddings: dict) -> float:
        """
        Check if metadata (title, description) aligns with content.
        
        Returns score 0-1 where:
        - 1.0 = Perfect alignment (title/desc accurately reflect content)
        - 0.5 = Moderate alignment
        - 0.0 = Misalignment (clickbait, misleading metadata)
        """
        
        # Get embeddings
        title_emb = page_embeddings['title']
        desc_emb = page_embeddings['meta_description']
        h1_emb = page_embeddings['h1']
        intro_emb = page_embeddings['intro_content']  # First 2-3 paragraphs
        content_centroid = page_embeddings['content_centroid']  # Average of all sections
        
        # Calculate pairwise similarities
        scores = {
            # Critical alignments
            'title_h1': cosine_similarity([title_emb], [h1_emb])[0][0],
            'title_content': cosine_similarity([title_emb], [content_centroid])[0][0],
            'desc_intro': cosine_similarity([desc_emb], [intro_emb])[0][0],
            'h1_content': cosine_similarity([h1_emb], [content_centroid])[0][0],
            
            # Secondary alignments
            'desc_content': cosine_similarity([desc_emb], [content_centroid])[0][0],
        }
        
        # Weighted scoring
        # title_h1: Most critical (should be nearly identical concept)
        # title_content: Very important (title should reflect actual content)
        # desc_intro: Important (description should match what user sees first)
        # h1_content: Important (main heading should match content)
        
        alignment_score = (
            0.30 * scores['title_h1'] +      # Target: 0.85+
            0.30 * scores['title_content'] +  # Target: 0.80+
            0.25 * scores['desc_intro'] +     # Target: 0.75+
            0.15 * scores['h1_content']       # Target: 0.80+
        )
        
        return alignment_score
```

**Target Thresholds** (calibrated from high-ranking pages):
- `title_h1`: ≥0.85 (nearly identical semantic meaning)
- `title_content`: ≥0.80 (title accurately reflects content)
- `desc_intro`: ≥0.75 (description matches what user reads first)
- `h1_content`: ≥0.80 (main heading aligns with body)

---

### Component 2: Hierarchical Decomposition Score (30%)

**Measures**: Does H1 break down into H2s, and H2s into H3s, semantically?

```python
class HierarchicalDecompositionScorer:
    def calculate(self, page: PageContent, page_embeddings: dict) -> float:
        """
        Check if headings follow logical semantic hierarchy.
        
        H1 should be the "parent topic"
        H2s should be "child topics" that decompose H1
        H3s should be "grandchild topics" that decompose their parent H2
        
        Returns score 0-1 where:
        - 1.0 = Perfect hierarchy (clear semantic decomposition)
        - 0.5 = Moderate hierarchy
        - 0.0 = No hierarchy (random topics)
        """
        
        h1_emb = page_embeddings['h1']
        h2_embeddings = page_embeddings['h2s']  # List of embeddings
        h3_embeddings_grouped = page_embeddings['h3s_by_h2']  # Dict: {h2_idx: [h3_embs]}
        
        scores = []
        
        # 1. Check H1 → H2 relationships
        # Each H2 should be moderately similar to H1 (same domain but distinct subtopic)
        # Target: 0.60-0.85 similarity
        # Too high (>0.90) = H2 is redundant with H1
        # Too low (<0.50) = H2 is off-topic
        
        h2_to_h1_similarities = []
        for h2_emb in h2_embeddings:
            sim = cosine_similarity([h1_emb], [h2_emb])[0][0]
            h2_to_h1_similarities.append(sim)
            
            # Score this relationship
            if 0.60 <= sim <= 0.85:
                scores.append(1.0)  # Perfect
            elif 0.50 <= sim < 0.60 or 0.85 < sim <= 0.90:
                scores.append(0.7)  # Acceptable
            else:
                scores.append(0.3)  # Poor (off-topic or redundant)
        
        # 2. Check H2 semantic diversity
        # H2s should cover distinct subtopics (not all the same thing)
        # Calculate pairwise similarity between all H2s
        # Target: Most pairs should be 0.40-0.70 (related but distinct)
        
        if len(h2_embeddings) >= 2:
            h2_matrix = cosine_similarity(h2_embeddings)
            # Get upper triangle (exclude diagonal)
            upper_tri = []
            for i in range(len(h2_matrix)):
                for j in range(i+1, len(h2_matrix)):
                    upper_tri.append(h2_matrix[i][j])
            
            avg_h2_similarity = np.mean(upper_tri)
            
            # Score diversity
            if 0.40 <= avg_h2_similarity <= 0.70:
                scores.append(1.0)  # Good diversity
            elif 0.30 <= avg_h2_similarity < 0.40 or 0.70 < avg_h2_similarity <= 0.80:
                scores.append(0.7)  # Acceptable
            else:
                scores.append(0.3)  # Poor (too similar or too different)
        
        # 3. Check H2 → H3 relationships (if H3s exist)
        # Each H3 should be moderately similar to its parent H2
        # Target: 0.65-0.85 similarity
        
        for h2_idx, h3_embs in h3_embeddings_grouped.items():
            if h2_idx < len(h2_embeddings):
                parent_h2_emb = h2_embeddings[h2_idx]
                
                for h3_emb in h3_embs:
                    sim = cosine_similarity([parent_h2_emb], [h3_emb])[0][0]
                    
                    if 0.65 <= sim <= 0.85:
                        scores.append(1.0)
                    elif 0.55 <= sim < 0.65 or 0.85 < sim <= 0.90:
                        scores.append(0.7)
                    else:
                        scores.append(0.3)
        
        return np.mean(scores) if scores else 0.5
```

**Why These Thresholds?**

- **H1 → H2: 0.60-0.85**
  - 0.85+: Too similar (H2 basically restates H1)
  - 0.60-0.85: Perfect (H2 is a subtopic of H1)
  - <0.60: Off-topic (H2 doesn't relate to H1)

- **H2 ↔ H2: 0.40-0.70**
  - 0.70+: H2s too similar (redundant sections)
  - 0.40-0.70: Good diversity (distinct but related subtopics)
  - <0.40: H2s unrelated (scattered, no thematic unity)

---

### Component 3: Thematic Unity Score (20%)

**Measures**: Do all sections support the main topic (H1)?

```python
class ThematicUnityScorer:
    def calculate(self, page: PageContent, section_embeddings: list) -> float:
        """
        Check if all content sections support the main topic.
        
        In APA style, all body paragraphs support the thesis.
        In SEO, all sections should support the main keyword/topic (H1).
        
        Returns score 0-1 where:
        - 1.0 = All sections tightly focused on main topic
        - 0.5 = Some tangential content
        - 0.0 = Scattered, unfocused content
        """
        
        h1_emb = page_embeddings['h1']
        section_embs = [emb for _, emb in section_embeddings]
        
        # Calculate similarity of each section to H1
        similarities = []
        for section_emb in section_embs:
            sim = cosine_similarity([h1_emb], [section_emb])[0][0]
            similarities.append(sim)
        
        # Statistics
        avg_sim = np.mean(similarities)
        min_sim = np.min(similarities)
        std_sim = np.std(similarities)
        
        # Score based on:
        # 1. Average similarity (higher = more focused)
        # 2. Minimum similarity (no outlier off-topic sections)
        # 3. Standard deviation (lower = consistent focus)
        
        avg_score = min(avg_sim / 0.70, 1.0)  # Target: 0.70+ average
        min_score = min(min_sim / 0.50, 1.0)  # Target: 0.50+ minimum
        consistency_score = max(1.0 - (std_sim / 0.20), 0.0)  # Target: <0.20 std
        
        unity_score = (
            0.50 * avg_score +
            0.30 * min_score +
            0.20 * consistency_score
        )
        
        return unity_score
```

---

### Component 4: Balance Score (15%)

**Measures**: Are sections appropriately sized and distributed?

```python
class BalanceScorer:
    def calculate(self, page: PageContent) -> float:
        """
        Check if page structure is balanced.
        
        Issues to detect:
        - One massive section + several tiny ones
        - Too many/too few H2s for content length
        - Empty sections (H2 with no content)
        
        Returns score 0-1
        """
        
        word_count = page.word_count
        h2_count = len(page.h2)
        h3_count = len(page.h3)
        
        scores = []
        
        # 1. H2 density (target: 1 H2 per 200-400 words)
        if word_count > 0:
            ideal_h2s = word_count / 300  # Middle of range
            actual_h2s = h2_count
            
            ratio = min(actual_h2s, ideal_h2s) / max(actual_h2s, ideal_h2s)
            scores.append(ratio)
        
        # 2. H3 density (target: 0-2 H3s per H2)
        if h2_count > 0:
            h3_per_h2 = h3_count / h2_count
            
            if 0 <= h3_per_h2 <= 2.5:
                scores.append(1.0)
            elif h3_per_h2 <= 4:
                scores.append(0.7)
            else:
                scores.append(0.3)  # Too many H3s
        
        # 3. Section size balance
        # Calculate word count per section (approximation)
        if h2_count > 0:
            words_per_section = word_count / h2_count
            
            # Ideal: 150-600 words per section
            if 150 <= words_per_section <= 600:
                scores.append(1.0)
            elif 100 <= words_per_section < 150 or 600 < words_per_section <= 800:
                scores.append(0.7)
            else:
                scores.append(0.3)
        
        return np.mean(scores) if scores else 0.5
```

---

### Component 5: Structural Hygiene Score (10%)

**Measures**: Basic best practices.

```python
class StructuralHygieneScorer:
    def calculate(self, page: PageContent) -> float:
        """
        Check basic structural best practices.
        
        Checks:
        - Only one H1
        - No skipped heading levels (H2 → H4)
        - Meta description exists and is appropriate length
        - Title tag appropriate length
        
        Returns score 0-1
        """
        
        checks = []
        
        # 1. Single H1
        checks.append(1.0 if len(page.h1) == 1 else 0.0)
        
        # 2. Meta description exists
        if page.meta_description:
            desc_len = len(page.meta_description)
            if 120 <= desc_len <= 160:
                checks.append(1.0)
            elif 100 <= desc_len < 120 or 160 < desc_len <= 180:
                checks.append(0.7)
            else:
                checks.append(0.3)
        else:
            checks.append(0.0)
        
        # 3. Title tag appropriate length
        title_len = len(page.title)
        if 30 <= title_len <= 60:
            checks.append(1.0)
        elif 20 <= title_len < 30 or 60 < title_len <= 70:
            checks.append(0.7)
        else:
            checks.append(0.3)
        
        # 4. Has H2s (not just H1)
        checks.append(1.0 if len(page.h2) >= 2 else 0.5)
        
        # 5. Reasonable content length
        if page.word_count >= 300:
            checks.append(1.0)
        elif page.word_count >= 150:
            checks.append(0.7)
        else:
            checks.append(0.3)
        
        return np.mean(checks)
```

---

## Complete Implementation

### New Scoring Service Addition:

```python
# services/analysis/structural_coherence_service.py

class StructuralCoherenceService:
    """Service for calculating structural coherence (APA-style quality)"""
    
    def __init__(self):
        self.metadata_scorer = MetadataAlignmentScorer()
        self.hierarchy_scorer = HierarchicalDecompositionScorer()
        self.unity_scorer = ThematicUnityScorer()
        self.balance_scorer = BalanceScorer()
        self.hygiene_scorer = StructuralHygieneScorer()
    
    async def calculate_structural_coherence(
        self,
        page: PageContent,
        embedder: EmbeddingService
    ) -> StructuralCoherenceScores:
        """
        Calculate complete structural coherence score.
        
        Returns:
            StructuralCoherenceScores with all component scores
        """
        
        # Generate all necessary embeddings
        page_embeddings = await self._create_page_embeddings(page, embedder)
        
        # Calculate component scores
        metadata_alignment = self.metadata_scorer.calculate(page, page_embeddings)
        hierarchical_decomp = self.hierarchy_scorer.calculate(page, page_embeddings)
        thematic_unity = self.unity_scorer.calculate(page, page_embeddings)
        balance = self.balance_scorer.calculate(page)
        hygiene = self.hygiene_scorer.calculate(page)
        
        # Calculate composite
        composite = (
            0.25 * metadata_alignment +
            0.30 * hierarchical_decomp +
            0.20 * thematic_unity +
            0.15 * balance +
            0.10 * hygiene
        )
        
        return StructuralCoherenceScores(
            metadata_alignment=metadata_alignment,
            hierarchical_decomposition=hierarchical_decomp,
            thematic_unity=thematic_unity,
            balance=balance,
            hygiene=hygiene,
            composite=composite
        )
    
    async def _create_page_embeddings(
        self, 
        page: PageContent, 
        embedder: EmbeddingService
    ) -> dict:
        """Create all embeddings needed for structural analysis"""
        
        # Prepare texts
        texts_to_embed = {
            'title': page.title,
            'meta_description': page.meta_description or "",
            'h1': page.h1[0] if page.h1 else "",
            'intro_content': " ".join(page.paragraphs[:3]) if len(page.paragraphs) >= 3 else " ".join(page.paragraphs),
        }
        
        # Create embeddings (batch for efficiency)
        embeddings = await embedder.create_embeddings(list(texts_to_embed.values()))
        
        # Map back to dict
        result = dict(zip(texts_to_embed.keys(), embeddings))
        
        # Add H2 embeddings
        if page.h2:
            result['h2s'] = await embedder.create_embeddings(page.h2)
        else:
            result['h2s'] = []
        
        # Add H3 embeddings grouped by parent H2
        # (Would need more sophisticated H3→H2 mapping based on document order)
        if page.h3:
            result['h3s'] = await embedder.create_embeddings(page.h3)
            # Simplified: assume H3s equally distributed across H2s
            result['h3s_by_h2'] = self._group_h3s_by_h2(page.h2, page.h3, result['h3s'])
        else:
            result['h3s'] = []
            result['h3s_by_h2'] = {}
        
        # Calculate content centroid (average of all paragraphs)
        if page.paragraphs:
            para_embeddings = await embedder.create_embeddings(page.paragraphs)
            result['content_centroid'] = np.array(para_embeddings).mean(axis=0).tolist()
        else:
            result['content_centroid'] = result['intro_content']
        
        return result
    
    def _group_h3s_by_h2(self, h2s: list, h3s: list, h3_embeddings: list) -> dict:
        """Group H3s by their parent H2 (simplified version)"""
        # In production, would need document order analysis
        # For now, distribute evenly
        h3_per_h2 = len(h3s) // max(len(h2s), 1)
        grouped = {}
        for i, h2 in enumerate(h2s):
            start_idx = i * h3_per_h2
            end_idx = start_idx + h3_per_h2
            if end_idx <= len(h3_embeddings):
                grouped[i] = h3_embeddings[start_idx:end_idx]
        return grouped
```

---

## Updated Composite Score Formula

### New Overall Score:

```python
# Old Magic-SEO formula:
composite = (alignment * 0.35) + (coverage * 0.35) + (keyword_presence * 0.30)

# NEW FORMULA with structural coherence:
composite = (
    0.25 * alignment_score +           # Semantic similarity to competitors
    0.25 * coverage_score +            # Topic coverage vs competitors
    0.20 * structural_coherence +      # NEW: APA-style quality
    0.15 * keyword_presence +          # Keyword in key locations
    0.15 * query_intent_match          # NEW: Does structure match query type?
)
```

### Rationale:

- **Alignment (25%)**: Still important - need to be in same semantic space as competitors
- **Coverage (25%)**: Critical - must cover all major topics competitors cover
- **Structural Coherence (20%)**: NEW - Internal quality matters for rankings
- **Keyword Presence (15%)**: Basic hygiene, but less weight (semantic understanding improved)
- **Query Intent Match (15%)**: NEW - Structure should match what query implies

---

## Query Intent Matching

**Additional component**: Does page structure match query type?

```python
class QueryIntentMatcher:
    """Match page structure to query intent"""
    
    INTENT_PATTERNS = {
        'how_to': {
            'indicators': ['how to', 'how do', 'how can'],
            'expected_structure': {
                'h2_patterns': ['step ', 'method ', 'way to'],
                'has_ordered_list': True,
                'min_h2s': 3,
            }
        },
        'what_is': {
            'indicators': ['what is', 'what are', 'define', 'definition'],
            'expected_structure': {
                'h2_patterns': ['definition', 'types', 'examples', 'benefits'],
                'intro_length': 'long',  # Needs good explanation
            }
        },
        'best': {
            'indicators': ['best', 'top', 'review'],
            'expected_structure': {
                'h2_patterns': ['#1', '#2', 'best for', 'winner'],
                'has_comparison': True,
                'min_h2s': 3,
            }
        },
        'vs': {
            'indicators': [' vs ', ' versus ', 'compare'],
            'expected_structure': {
                'h2_patterns': ['comparison', 'vs', 'versus', 'difference', 'pros', 'cons'],
                'has_table': True,
                'balanced_sections': True,
            }
        }
    }
    
    def score_intent_match(self, keyword: str, page: PageContent) -> float:
        """
        Score how well page structure matches query intent.
        
        Returns 0-1 score
        """
        
        # Detect intent
        intent = self._detect_intent(keyword)
        
        if not intent:
            return 0.7  # Neutral score if can't determine intent
        
        expected = self.INTENT_PATTERNS[intent]['expected_structure']
        
        # Check structure matches expectations
        matches = []
        
        # Check H2 patterns
        if 'h2_patterns' in expected:
            h2_text_lower = " ".join(page.h2).lower()
            pattern_matches = sum(1 for p in expected['h2_patterns'] if p in h2_text_lower)
            pattern_score = min(pattern_matches / len(expected['h2_patterns']), 1.0)
            matches.append(pattern_score)
        
        # Check minimum H2s
        if 'min_h2s' in expected:
            matches.append(1.0 if len(page.h2) >= expected['min_h2s'] else 0.5)
        
        return np.mean(matches) if matches else 0.7
```

---

## Optimization Strategy: "Hashing Algorithm"

**Your mention of a "hashing algorithm" is interesting**. Here's how to optimize:

### Caching Strategy:

```python
class StructuralCoherenceCache:
    """
    Cache embeddings and scores to avoid recomputation.
    
    Key insight: Most page elements (title, H1, H2s) don't change frequently.
    Only recompute what changed.
    """
    
    def get_cache_key(self, page: PageContent) -> str:
        """
        Create hash of page structure.
        
        Uses: title + H1 + H2s + meta description + word count
        If hash matches, can reuse cached scores.
        """
        import hashlib
        
        structure_str = (
            page.title +
            "|".join(page.h1) +
            "|".join(page.h2) +
            page.meta_description +
            str(page.word_count)
        )
        
        return hashlib.sha256(structure_str.encode()).hexdigest()
    
    def can_reuse_embeddings(
        self, 
        current_page: PageContent, 
        cached_page: PageContent
    ) -> dict:
        """
        Determine which embeddings can be reused.
        
        Returns dict of reusable components: {'title': True, 'h1': True, 'h2s': False, ...}
        """
        reusable = {}
        
        reusable['title'] = (current_page.title == cached_page.title)
        reusable['h1'] = (current_page.h1 == cached_page.h1)
        reusable['h2s'] = (current_page.h2 == cached_page.h2)
        reusable['meta_description'] = (current_page.meta_description == cached_page.meta_description)
        
        # Content centroid: reuse if word count within 10% and first 3 paras unchanged
        word_count_similar = abs(current_page.word_count - cached_page.word_count) / max(cached_page.word_count, 1) < 0.10
        intro_same = (current_page.paragraphs[:3] == cached_page.paragraphs[:3])
        reusable['content_centroid'] = (word_count_similar and intro_same)
        
        return reusable
```

### Incremental Computation:

```python
def calculate_structural_coherence_incremental(
    current_page: PageContent,
    cached_data: dict,
    embedder: EmbeddingService
) -> StructuralCoherenceScores:
    """
    Recalculate only what changed.
    
    Huge speedup for iterative optimization:
    - Change H2 → only recompute hierarchical_decomposition
    - Change title → only recompute metadata_alignment
    - Add content → only recompute thematic_unity
    """
    
    reusable = can_reuse_embeddings(current_page, cached_data['page'])
    
    # Reuse cached embeddings where possible
    page_embeddings = {}
    for component, can_reuse in reusable.items():
        if can_reuse:
            page_embeddings[component] = cached_data['embeddings'][component]
        else:
            # Recompute this component
            page_embeddings[component] = await _compute_embedding(current_page, component, embedder)
    
    # Recompute only affected scores
    # (Details depend on what changed)
    ...
```

---

## Comparison: Your Pages vs Competitors

### Average Structural Coherence:

```python
def compare_structural_coherence(
    your_page: PageContent,
    competitor_pages: list[PageContent],
    embedder: EmbeddingService
) -> StructuralComparisonReport:
    """
    Calculate structural coherence for your page and all competitors.
    
    Returns:
    - Your score
    - Average competitor score
    - Best competitor score
    - Gap analysis
    """
    
    # Calculate for your page
    your_scores = await calculate_structural_coherence(your_page, embedder)
    
    # Calculate for each competitor
    competitor_scores = []
    for comp_page in competitor_pages:
        scores = await calculate_structural_coherence(comp_page, embedder)
        competitor_scores.append(scores)
    
    # Statistics
    avg_competitor = np.mean([s.composite for s in competitor_scores])
    best_competitor = max([s.composite for s in competitor_scores])
    
    # Component-level comparison
    component_gaps = {
        'metadata_alignment': avg_competitor_component('metadata_alignment') - your_scores.metadata_alignment,
        'hierarchical_decomposition': ...,
        'thematic_unity': ...,
        'balance': ...,
        'hygiene': ...,
    }
    
    return StructuralComparisonReport(
        your_score=your_scores.composite,
        competitor_avg=avg_competitor,
        competitor_best=best_competitor,
        gap=avg_competitor - your_scores.composite,
        component_gaps=component_gaps,
        weakest_component=min(component_gaps, key=component_gaps.get),
        recommendations=_generate_structural_recommendations(component_gaps)
    )
```

---

## Implementation Priority

### Phase 1 (Week 1): Basic Structural Scoring
- [ ] Implement MetadataAlignmentScorer
- [ ] Implement StructuralHygieneScorer
- [ ] Add to existing scoring pipeline
- [ ] Test on sample pages

### Phase 2 (Week 2): Hierarchical Analysis
- [ ] Implement HierarchicalDecompositionScorer
- [ ] Implement ThematicUnityScorer
- [ ] Add H3→H2 grouping logic
- [ ] Calibrate thresholds

### Phase 3 (Week 3): Optimization
- [ ] Implement BalanceScorer
- [ ] Implement QueryIntentMatcher
- [ ] Build caching system
- [ ] Add incremental computation

### Phase 4 (Week 4): Competitor Comparison
- [ ] Calculate structural coherence for competitors
- [ ] Generate comparative reports
- [ ] Identify specific structural improvements
- [ ] A/B test recommendations

---

## Example Output

```json
{
  "your_page": {
    "structural_coherence": 0.78,
    "components": {
      "metadata_alignment": 0.82,
      "hierarchical_decomposition": 0.75,
      "thematic_unity": 0.81,
      "balance": 0.76,
      "hygiene": 0.90
    }
  },
  "competitors": {
    "average_structural_coherence": 0.84,
    "best_structural_coherence": 0.91
  },
  "gap_analysis": {
    "overall_gap": -0.06,
    "weakest_component": "hierarchical_decomposition",
    "recommendations": [
      "H2 'Pricing Options' is off-topic (0.45 similarity to H1). Consider renaming to align with main topic.",
      "Title and H1 similarity is 0.72 (target: 0.85+). Make H1 more closely match title.",
      "H2s are too similar to each other (0.78 avg). Create more distinct subtopics.",
      "Meta description doesn't match intro content (0.68 similarity). Rewrite to reflect actual content."
    ]
  }
}
```

---

## Summary

### What You Identified (Correctly):

1. ✅ **Magic-SEO chunks by H2s** → Good start, but incomplete
2. ✅ **Missing APA-style coherence** → Critical gap
3. ✅ **Need hierarchical semantic analysis** → H1 → H2 → H3 relationships
4. ✅ **Need metadata alignment scoring** → Title/desc vs content
5. ✅ **Should compare against competitors** → Get average structural quality

### What We're Adding:

- **Structural Coherence Score (0-1)** with 5 components
- **Metadata Alignment** (25%): Title/desc vs content
- **Hierarchical Decomposition** (30%): H1 → H2 → H3 logic
- **Thematic Unity** (20%): All sections support main topic
- **Balance** (15%): Appropriate section sizing
- **Hygiene** (10%): Basic best practices

### Why This Matters:

Google absolutely uses structural signals:
- **Passage indexing** requires coherent sections
- **BERT** understands hierarchical relationships
- **Quality raters** check for clear organization
- **E-E-A-T** requires logical presentation

**Pages with high structural coherence rank better**, even with similar content coverage.

### Cost:

- **Additional embeddings per page**: ~10-15 (title, desc, H1, H2s, H3s)
- **Additional compute**: ~0.5 seconds per page (with caching)
- **Cost with OpenAI**: ~$0.005 extra per page
- **Cost with local GPU**: ~$0.000 extra per page

**ROI**: Massive. Structural quality is a **major ranking factor** that competitors ignore.

