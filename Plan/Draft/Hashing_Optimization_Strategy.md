# Hashing & Optimization Strategy

## The Problem: Computational Efficiency

**Scenario**: You want to test 1,000 word-level changes to optimize a page.

**Naive approach**:
```python
for change in 1000_word_changes:
    modified_page = apply_change(page, change)
    
    # This is EXPENSIVE - recalculates EVERYTHING
    new_score = calculate_all_scores(
        modified_page,
        competitors,  # Need to re-embed everything
        embedder      # 15+ embeddings per test
    )
    
    if new_score > current_score:
        keep_change(change)
```

**Cost**: 1,000 changes × 15 embeddings × $0.0001 = **$1.50 per page**  
**Time**: 1,000 changes × 0.5 seconds = **8+ minutes per page**

**The Solution**: Smart hashing and incremental computation.

---

## Core Concept: The Hash Hierarchy

Think of the page as a **nested hash structure** where:
- **Micro-hashes**: Individual components (title, H1, each H2 section)
- **Meso-hashes**: Component groups (all H2s, metadata bundle)
- **Macro-hashes**: Score categories (structural, coverage, alignment)
- **Mega-hash**: Overall composite score

```
┌─────────────────────────────────────────────────────────────┐
│ MEGA-HASH: Overall Composite Score (0.786)                  │
│ Hash: sha256(alignment + coverage + structural + ...)       │
└─────────────────────────────────────────────────────────────┘
                            ▲
            ┌───────────────┼───────────────┐
            │               │               │
┌───────────┴──────┐  ┌────┴────┐  ┌──────┴─────────┐
│ MACRO-HASH:      │  │ MACRO:  │  │ MACRO:         │
│ Alignment (0.78) │  │ Coverage│  │ Structural     │
│                  │  │ (0.72)  │  │ (0.80)         │
└──────────────────┘  └─────────┘  └────────────────┘
         ▲                  ▲              ▲
         │                  │              │
    ┌────┴────┐        ┌────┴────┐   ┌────┴────┐
    │ MESO:   │        │ MESO:   │   │ MESO:   │
    │ Page    │        │ Topics  │   │ Metadata│
    │ Embed   │        │ Covered │   │ Align   │
    └─────────┘        └─────────┘   └─────────┘
         ▲                  ▲              ▲
         │                  │              │
    ┌────┴────┐        ┌────┴────┐   ┌────┴────┐
    │ MICRO:  │        │ MICRO:  │   │ MICRO:  │
    │ Section │        │ Section │   │ Title   │
    │ Embeds  │        │ Matches │   │ H1      │
    │ [...]   │        │ [...]   │   │ Desc    │
    └─────────┘        └─────────┘   └─────────┘
         ▲                  ▲              ▲
         │                  │              │
    ┌────┴────┐        ┌────┴────┐   ┌────┴────┐
    │ NANO:   │        │ NANO:   │   │ NANO:   │
    │ Words   │        │ Keywords│   │ Text    │
    │ [w1,w2] │        │ [.....] │   │ Strings │
    └─────────┘        └─────────┘   └─────────┘
```

**Key Insight**: If you change 1 word in section 3, you only need to recalculate:
- NANO: That section's word list
- MICRO: That section's embedding
- MESO: Page embedding (average of all section embeddings)
- MACRO: Alignment score (uses page embedding)
- MEGA: Overall composite (uses alignment)

**Don't recalculate**: Coverage, structural coherence for other sections, competitor embeddings, etc.

---

## The Hashing Plan

### 1. State Representation (Content Hashing)

**Goal**: Efficiently detect what changed.

```python
from hashlib import sha256
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class PageHash:
    """Complete hash representation of page state"""
    
    # NANO level: Raw text hashes
    title_hash: str
    meta_desc_hash: str
    h1_hash: str
    h2_hashes: Dict[int, str]  # {index: hash}
    section_hashes: Dict[int, str]  # {index: hash}
    
    # MICRO level: Component hashes
    metadata_bundle_hash: str  # title + meta_desc + h1
    structure_bundle_hash: str  # h2s + h3s order
    content_bundle_hash: str   # all sections
    
    # MESO level: Embedding hashes (expensive to compute)
    title_embedding_hash: Optional[str] = None
    h1_embedding_hash: Optional[str] = None
    section_embedding_hashes: Dict[int, str] = None
    page_embedding_hash: Optional[str] = None
    
    # MACRO level: Score hashes
    alignment_score_hash: Optional[str] = None
    coverage_score_hash: Optional[str] = None
    structural_score_hash: Optional[str] = None
    
    # MEGA level: Overall hash
    composite_score_hash: Optional[str] = None
    
    def __init__(self, page: PageContent):
        """Initialize hashes from page content"""
        # NANO level (fast - just SHA256 of text)
        self.title_hash = self._hash(page.title)
        self.meta_desc_hash = self._hash(page.meta_description)
        self.h1_hash = self._hash('|'.join(page.h1))
        self.h2_hashes = {i: self._hash(h2) for i, h2 in enumerate(page.h2)}
        self.section_hashes = {i: self._hash(p) for i, p in enumerate(page.paragraphs)}
        
        # MICRO level (derived from NANO)
        self.metadata_bundle_hash = self._hash(
            self.title_hash + self.meta_desc_hash + self.h1_hash
        )
        self.structure_bundle_hash = self._hash(
            '|'.join(self.h2_hashes.values())
        )
        self.content_bundle_hash = self._hash(
            '|'.join(self.section_hashes.values())
        )
    
    @staticmethod
    def _hash(text: str) -> str:
        """Fast hash of text content"""
        return sha256(text.encode()).hexdigest()[:16]  # Short hash
    
    def detect_changes(self, new_page: PageContent) -> ChangeSet:
        """
        Detect exactly what changed between current and new page.
        
        Returns ChangeSet with flags for what needs recalculation.
        """
        new_hash = PageHash(new_page)
        changes = ChangeSet()
        
        # Check NANO level changes
        if self.title_hash != new_hash.title_hash:
            changes.title_changed = True
            changes.metadata_changed = True
        
        if self.meta_desc_hash != new_hash.meta_desc_hash:
            changes.meta_desc_changed = True
            changes.metadata_changed = True
        
        if self.h1_hash != new_hash.h1_hash:
            changes.h1_changed = True
            changes.metadata_changed = True
        
        # Check H2 changes
        for idx, h2_hash in self.h2_hashes.items():
            if new_hash.h2_hashes.get(idx) != h2_hash:
                changes.h2_changed_indices.append(idx)
                changes.structure_changed = True
        
        # Check section changes
        for idx, section_hash in self.section_hashes.items():
            if new_hash.section_hashes.get(idx) != section_hash:
                changes.section_changed_indices.append(idx)
                changes.content_changed = True
        
        # Determine what needs recalculation
        changes.needs_embedding_recalc = (
            changes.metadata_changed or 
            len(changes.section_changed_indices) > 0
        )
        
        changes.needs_structural_recalc = changes.structure_changed
        changes.needs_coverage_recalc = changes.content_changed
        changes.needs_alignment_recalc = changes.content_changed
        
        return changes

@dataclass
class ChangeSet:
    """What changed and what needs recalculation"""
    
    # NANO level changes
    title_changed: bool = False
    meta_desc_changed: bool = False
    h1_changed: bool = False
    h2_changed_indices: List[int] = None
    section_changed_indices: List[int] = None
    
    # MICRO level impacts
    metadata_changed: bool = False
    structure_changed: bool = False
    content_changed: bool = False
    
    # MACRO level recalc needs
    needs_embedding_recalc: bool = False
    needs_structural_recalc: bool = False
    needs_coverage_recalc: bool = False
    needs_alignment_recalc: bool = False
    
    def __post_init__(self):
        if self.h2_changed_indices is None:
            self.h2_changed_indices = []
        if self.section_changed_indices is None:
            self.section_changed_indices = []
```

---

### 2. Score Dependency Graph

**Goal**: Know what scores depend on what data.

```python
class ScoreDependencyGraph:
    """
    Maps dependencies between scores.
    
    If X changes, what needs to be recalculated?
    """
    
    DEPENDENCIES = {
        # NANO → MICRO
        'title_text': ['title_embedding', 'metadata_alignment'],
        'meta_desc_text': ['meta_desc_embedding', 'metadata_alignment'],
        'h1_text': ['h1_embedding', 'metadata_alignment', 'hierarchical_decomp'],
        'h2_text[i]': ['h2_embeddings[i]', 'hierarchical_decomp', 'structure_balance'],
        'section_text[i]': ['section_embeddings[i]', 'page_embedding', 'thematic_unity'],
        
        # MICRO → MESO
        'section_embeddings[i]': ['page_embedding', 'thematic_unity'],
        'page_embedding': ['alignment_score'],
        'h2_embeddings': ['hierarchical_decomp'],
        
        # MESO → MACRO
        'alignment_score': ['overall_composite'],
        'coverage_score': ['overall_composite'],
        'structural_coherence': ['overall_composite'],
        'keyword_presence': ['overall_composite'],
        'query_intent': ['overall_composite'],
        
        # MACRO → MEGA
        'overall_composite': []  # Top level
    }
    
    def get_recalc_list(self, changed_components: List[str]) -> List[str]:
        """
        Given what changed, return everything that needs recalculation.
        
        Uses dependency graph to find all downstream impacts.
        """
        needs_recalc = set()
        queue = list(changed_components)
        
        while queue:
            component = queue.pop(0)
            
            if component in needs_recalc:
                continue
                
            needs_recalc.add(component)
            
            # Add all dependents
            for dep_component, dependencies in self.DEPENDENCIES.items():
                if component in dependencies:
                    queue.append(dep_component)
        
        return list(needs_recalc)
    
    def minimal_recalc_plan(self, changes: ChangeSet) -> RecalcPlan:
        """
        Create minimal recalculation plan based on changes.
        
        Returns exactly what needs to be recomputed, in dependency order.
        """
        plan = RecalcPlan()
        
        # Map changes to components
        changed = []
        if changes.title_changed:
            changed.append('title_text')
        if changes.meta_desc_changed:
            changed.append('meta_desc_text')
        if changes.h1_changed:
            changed.append('h1_text')
        for idx in changes.h2_changed_indices:
            changed.append(f'h2_text[{idx}]')
        for idx in changes.section_changed_indices:
            changed.append(f'section_text[{idx}]')
        
        # Get full recalc list
        plan.components_to_recalc = self.get_recalc_list(changed)
        
        # Sort by dependency order (NANO → MICRO → MESO → MACRO → MEGA)
        plan.components_to_recalc.sort(key=self._dependency_order)
        
        # Estimate cost
        plan.embeddings_needed = len([c for c in plan.components_to_recalc if 'embedding' in c])
        plan.estimated_time_seconds = plan.embeddings_needed * 0.05  # 50ms per embedding
        plan.estimated_cost_usd = plan.embeddings_needed * 0.0001  # OpenAI cost
        
        return plan

@dataclass
class RecalcPlan:
    """Plan for what to recalculate"""
    components_to_recalc: List[str] = None
    embeddings_needed: int = 0
    estimated_time_seconds: float = 0.0
    estimated_cost_usd: float = 0.0
    
    def __post_init__(self):
        if self.components_to_recalc is None:
            self.components_to_recalc = []
```

---

### 3. Cached Score Manager

**Goal**: Store computed scores and embeddings, reuse when possible.

```python
from typing import Any, Optional
import pickle

class CachedScoreManager:
    """
    Manages cached scores and embeddings.
    
    Key insight: Embeddings are expensive. Cache aggressively.
    """
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache for current optimization session
        self.session_cache = {
            'embeddings': {},
            'scores': {},
            'page_hashes': {}
        }
    
    def get_or_compute_embedding(
        self,
        text: str,
        text_hash: str,
        embedder: EmbeddingService
    ) -> np.ndarray:
        """
        Get embedding from cache or compute if not cached.
        
        Returns embedding vector.
        """
        
        # Check in-memory session cache first
        if text_hash in self.session_cache['embeddings']:
            return self.session_cache['embeddings'][text_hash]
        
        # Check disk cache
        cache_file = self.cache_dir / f"emb_{text_hash}.pkl"
        if cache_file.exists():
            with open(cache_file, 'rb') as f:
                embedding = pickle.load(f)
                self.session_cache['embeddings'][text_hash] = embedding
                return embedding
        
        # Compute (expensive!)
        embedding = embedder.embed(text)
        
        # Cache in memory
        self.session_cache['embeddings'][text_hash] = embedding
        
        # Cache on disk
        with open(cache_file, 'wb') as f:
            pickle.dump(embedding, f)
        
        return embedding
    
    def get_cached_score(
        self,
        score_type: str,
        input_hash: str
    ) -> Optional[float]:
        """
        Get cached score if inputs haven't changed.
        
        Returns None if cache miss.
        """
        cache_key = f"{score_type}_{input_hash}"
        
        # Check in-memory
        if cache_key in self.session_cache['scores']:
            return self.session_cache['scores'][cache_key]
        
        # Check disk
        cache_file = self.cache_dir / f"score_{cache_key}.json"
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                score = json.load(f)['score']
                self.session_cache['scores'][cache_key] = score
                return score
        
        return None
    
    def cache_score(
        self,
        score_type: str,
        input_hash: str,
        score: float
    ):
        """Cache a computed score"""
        cache_key = f"{score_type}_{input_hash}"
        
        # Memory cache
        self.session_cache['scores'][cache_key] = score
        
        # Disk cache
        cache_file = self.cache_dir / f"score_{cache_key}.json"
        with open(cache_file, 'w') as f:
            json.dump({
                'score': score,
                'timestamp': datetime.now().isoformat(),
                'input_hash': input_hash
            }, f)
    
    def batch_get_embeddings(
        self,
        texts: List[str],
        embedder: EmbeddingService
    ) -> List[np.ndarray]:
        """
        Get embeddings for multiple texts, batching API calls.
        
        Returns list of embeddings (some from cache, rest computed).
        """
        
        # Hash all texts
        text_hashes = [sha256(t.encode()).hexdigest()[:16] for t in texts]
        
        # Check cache
        embeddings = []
        texts_to_compute = []
        indices_to_compute = []
        
        for i, (text, text_hash) in enumerate(zip(texts, text_hashes)):
            if text_hash in self.session_cache['embeddings']:
                embeddings.append(self.session_cache['embeddings'][text_hash])
            else:
                embeddings.append(None)  # Placeholder
                texts_to_compute.append(text)
                indices_to_compute.append(i)
        
        # Batch compute missing embeddings
        if texts_to_compute:
            computed = embedder.batch_embed(texts_to_compute)
            
            # Fill in placeholders and cache
            for idx, embedding in zip(indices_to_compute, computed):
                embeddings[idx] = embedding
                text_hash = text_hashes[idx]
                self.session_cache['embeddings'][text_hash] = embedding
                
                # Disk cache
                cache_file = self.cache_dir / f"emb_{text_hash}.pkl"
                with open(cache_file, 'wb') as f:
                    pickle.dump(embedding, f)
        
        return embeddings
```

---

### 4. Incremental Score Calculator

**Goal**: Recalculate only what changed.

```python
class IncrementalScoreCalculator:
    """
    Calculate scores incrementally based on what changed.
    
    This is the heart of efficient optimization.
    """
    
    def __init__(
        self,
        cache_manager: CachedScoreManager,
        embedder: EmbeddingService,
        competitor_data: dict
    ):
        self.cache = cache_manager
        self.embedder = embedder
        self.competitors = competitor_data
        self.dependency_graph = ScoreDependencyGraph()
    
    def calculate_score_incremental(
        self,
        page: PageContent,
        page_hash: PageHash,
        previous_page: Optional[PageContent] = None,
        previous_hash: Optional[PageHash] = None
    ) -> IncrementalScoreResult:
        """
        Calculate score, reusing cached values where possible.
        
        If previous_page provided, detect changes and recalc only what's needed.
        If not provided, calculate everything (first run).
        """
        
        result = IncrementalScoreResult()
        
        # Detect changes
        if previous_page and previous_hash:
            changes = previous_hash.detect_changes(page)
            recalc_plan = self.dependency_graph.minimal_recalc_plan(changes)
            result.recalc_plan = recalc_plan
        else:
            # First run - calculate everything
            changes = None
            recalc_plan = self._full_recalc_plan()
        
        # Track what we're reusing vs recalculating
        result.embeddings_cached = 0
        result.embeddings_computed = 0
        result.scores_cached = 0
        result.scores_computed = 0
        
        # Calculate embeddings (with caching)
        embeddings = self._get_embeddings_incremental(
            page,
            page_hash,
            recalc_plan,
            result
        )
        
        # Calculate scores (with caching)
        scores = self._calculate_scores_incremental(
            page,
            embeddings,
            recalc_plan,
            result
        )
        
        result.scores = scores
        result.total_time_seconds = result.compute_time()
        
        return result
    
    def _get_embeddings_incremental(
        self,
        page: PageContent,
        page_hash: PageHash,
        recalc_plan: RecalcPlan,
        result: IncrementalScoreResult
    ) -> Dict[str, np.ndarray]:
        """Get all necessary embeddings, using cache where possible"""
        
        embeddings = {}
        
        # Title embedding
        if 'title_embedding' in recalc_plan.components_to_recalc:
            embeddings['title'] = self.cache.get_or_compute_embedding(
                page.title,
                page_hash.title_hash,
                self.embedder
            )
            result.embeddings_computed += 1
        else:
            embeddings['title'] = self.cache.get_cached_embedding(page_hash.title_hash)
            result.embeddings_cached += 1
        
        # Similar for other components...
        
        # Section embeddings (batch compute new ones)
        sections_to_compute = []
        section_indices = []
        
        for i, section in enumerate(page.paragraphs):
            section_hash = page_hash.section_hashes[i]
            
            if f'section_embeddings[{i}]' in recalc_plan.components_to_recalc:
                sections_to_compute.append(section)
                section_indices.append(i)
            else:
                embeddings[f'section_{i}'] = self.cache.get_cached_embedding(section_hash)
                result.embeddings_cached += 1
        
        # Batch compute new section embeddings
        if sections_to_compute:
            computed = self.embedder.batch_embed(sections_to_compute)
            for idx, embedding in zip(section_indices, computed):
                embeddings[f'section_{idx}'] = embedding
                self.cache.cache_embedding(page_hash.section_hashes[idx], embedding)
                result.embeddings_computed += 1
        
        # Page embedding (average of section embeddings)
        if 'page_embedding' in recalc_plan.components_to_recalc:
            section_embs = [embeddings[f'section_{i}'] for i in range(len(page.paragraphs))]
            embeddings['page'] = np.mean(section_embs, axis=0)
            result.embeddings_computed += 1
        else:
            embeddings['page'] = self.cache.get_cached_embedding(page_hash.content_bundle_hash)
            result.embeddings_cached += 1
        
        return embeddings
    
    def _calculate_scores_incremental(
        self,
        page: PageContent,
        embeddings: Dict[str, np.ndarray],
        recalc_plan: RecalcPlan,
        result: IncrementalScoreResult
    ) -> AnalysisScores:
        """Calculate scores, using cache where possible"""
        
        scores = AnalysisScores()
        
        # Alignment score
        if 'alignment_score' in recalc_plan.components_to_recalc:
            scores.alignment_score = self._calculate_alignment(
                embeddings['page'],
                self.competitors['embeddings']
            )
            result.scores_computed += 1
        else:
            scores.alignment_score = self.cache.get_cached_score(
                'alignment',
                embeddings['page_hash']
            )
            result.scores_cached += 1
        
        # Coverage score
        if 'coverage_score' in recalc_plan.components_to_recalc:
            scores.coverage_score = self._calculate_coverage(
                page,
                embeddings,
                self.competitors['clusters']
            )
            result.scores_computed += 1
        else:
            scores.coverage_score = self.cache.get_cached_score(
                'coverage',
                page_hash.content_bundle_hash
            )
            result.scores_cached += 1
        
        # Structural coherence
        if 'structural_coherence' in recalc_plan.components_to_recalc:
            scores.structural_coherence = self._calculate_structural(
                page,
                embeddings
            )
            result.scores_computed += 1
        else:
            scores.structural_coherence = self.cache.get_cached_score(
                'structural',
                page_hash.structure_bundle_hash + page_hash.metadata_bundle_hash
            )
            result.scores_cached += 1
        
        # Keyword presence (cheap - always recalc)
        scores.keyword_presence = self._calculate_keyword_presence(page)
        
        # Query intent (cheap - always recalc)
        scores.query_intent = self._calculate_query_intent(page)
        
        # Overall composite
        scores.composite_score = (
            0.25 * scores.alignment_score +
            0.25 * scores.coverage_score +
            0.20 * scores.structural_coherence +
            0.15 * scores.keyword_presence +
            0.15 * scores.query_intent
        )
        
        return scores

@dataclass
class IncrementalScoreResult:
    """Result of incremental score calculation"""
    scores: Optional[AnalysisScores] = None
    recalc_plan: Optional[RecalcPlan] = None
    embeddings_cached: int = 0
    embeddings_computed: int = 0
    scores_cached: int = 0
    scores_computed: int = 0
    total_time_seconds: float = 0.0
    
    def compute_time(self) -> float:
        """Estimate total computation time"""
        return (
            self.embeddings_computed * 0.05 +  # 50ms per embedding
            self.scores_computed * 0.01          # 10ms per score calc
        )
    
    def efficiency_ratio(self) -> float:
        """What % of work was cached?"""
        total = (
            self.embeddings_cached + self.embeddings_computed +
            self.scores_cached + self.scores_computed
        )
        if total == 0:
            return 0.0
        cached = self.embeddings_cached + self.scores_cached
        return cached / total
```

---

### 5. Optimization Loop with Hashing

**Goal**: Test 1000s of changes efficiently.

```python
class HashingOptimizer:
    """
    Optimize page using hashing for efficient testing.
    
    Can test 1000s of word changes in minutes instead of hours.
    """
    
    def __init__(
        self,
        calculator: IncrementalScoreCalculator,
        cache_manager: CachedScoreManager
    ):
        self.calculator = calculator
        self.cache = cache_manager
    
    def optimize(
        self,
        page: PageContent,
        target_score: float = 0.85,
        max_iterations: int = 1000,
        min_improvement: float = 0.001
    ) -> OptimizationResult:
        """
        Optimize page to target score.
        
        Uses hashing to test changes efficiently.
        """
        
        result = OptimizationResult()
        result.start_time = time.time()
        
        # Initial scoring (full calculation)
        current_page = page
        current_hash = PageHash(page)
        
        initial_result = self.calculator.calculate_score_incremental(
            page,
            current_hash
        )
        current_score = initial_result.scores.composite_score
        result.initial_score = current_score
        
        logger.info(f"Starting optimization from score: {current_score:.3f}")
        
        # Optimization loop
        for iteration in range(max_iterations):
            # Generate candidate changes
            candidates = self._generate_candidate_changes(current_page)
            
            if not candidates:
                logger.info("No more candidate changes")
                break
            
            # Test each candidate (EFFICIENTLY with hashing!)
            best_candidate = None
            best_improvement = 0
            
            for candidate in candidates:
                # Apply change
                modified_page = self._apply_change(current_page, candidate)
                modified_hash = PageHash(modified_page)
                
                # Incremental scoring (FAST - reuses cached embeddings)
                candidate_result = self.calculator.calculate_score_incremental(
                    modified_page,
                    modified_hash,
                    previous_page=current_page,
                    previous_hash=current_hash
                )
                
                candidate_score = candidate_result.scores.composite_score
                improvement = candidate_score - current_score
                
                # Track efficiency
                result.total_embeddings_cached += candidate_result.embeddings_cached
                result.total_embeddings_computed += candidate_result.embeddings_computed
                
                if improvement > best_improvement:
                    best_improvement = improvement
                    best_candidate = (candidate, modified_page, modified_hash, candidate_score)
                
                logger.debug(
                    f"  Candidate: {candidate.description}, "
                    f"improvement: {improvement:+.4f}, "
                    f"cached: {candidate_result.embeddings_cached}/"
                    f"{candidate_result.embeddings_cached + candidate_result.embeddings_computed}"
                )
            
            # Keep best change if it meets threshold
            if best_candidate and best_improvement >= min_improvement:
                candidate, modified_page, modified_hash, new_score = best_candidate
                
                current_page = modified_page
                current_hash = modified_hash
                current_score = new_score
                
                result.changes_made.append({
                    'iteration': iteration,
                    'change': candidate,
                    'improvement': best_improvement,
                    'new_score': new_score
                })
                
                logger.info(
                    f"Iteration {iteration}: Applied {candidate.description}, "
                    f"improvement: {best_improvement:+.4f}, "
                    f"new score: {new_score:.3f}"
                )
                
                # Check if target reached
                if new_score >= target_score:
                    logger.info(f"Target score {target_score:.3f} reached!")
                    break
            else:
                logger.info(
                    f"Iteration {iteration}: No improvement ≥ {min_improvement:.4f}, stopping"
                )
                break
        
        result.end_time = time.time()
        result.final_score = current_score
        result.final_page = current_page
        result.total_improvement = current_score - result.initial_score
        result.iterations_run = len(result.changes_made)
        
        # Calculate efficiency
        total_embedding_ops = (
            result.total_embeddings_cached + result.total_embeddings_computed
        )
        result.cache_efficiency = (
            result.total_embeddings_cached / total_embedding_ops
            if total_embedding_ops > 0 else 0
        )
        
        logger.info(
            f"Optimization complete: {result.initial_score:.3f} → {result.final_score:.3f} "
            f"(+{result.total_improvement:.3f}) in {result.iterations_run} iterations"
        )
        logger.info(
            f"Cache efficiency: {result.cache_efficiency:.1%} "
            f"({result.total_embeddings_cached}/{total_embedding_ops} embeddings cached)"
        )
        
        return result

@dataclass
class OptimizationResult:
    """Result of optimization process"""
    initial_score: float = 0.0
    final_score: float = 0.0
    total_improvement: float = 0.0
    iterations_run: int = 0
    changes_made: List[dict] = None
    final_page: Optional[PageContent] = None
    
    total_embeddings_cached: int = 0
    total_embeddings_computed: int = 0
    cache_efficiency: float = 0.0
    
    start_time: float = 0.0
    end_time: float = 0.0
    
    def __post_init__(self):
        if self.changes_made is None:
            self.changes_made = []
    
    @property
    def total_time_seconds(self) -> float:
        return self.end_time - self.start_time
```

---

## Performance Comparison

### Without Hashing (Naive Approach):

```
Test 1000 word changes:
├─ 1000 changes × 15 embeddings = 15,000 embeddings
├─ Time: 15,000 × 0.05s = 750 seconds (12.5 minutes)
├─ Cost: 15,000 × $0.0001 = $1.50
└─ Efficiency: 0% cached

Result: SLOW and EXPENSIVE
```

### With Hashing (Our Approach):

```
Test 1000 word changes:
├─ Initial: 15 embeddings (full calculation)
├─ Per change: ~1 embedding (only changed section)
├─ Total: 15 + (1000 × 1) = 1,015 embeddings
├─ But with caching: ~15 + 50 = 65 embeddings
│  (Most candidates reuse same word additions)
├─ Time: 65 × 0.05s = 3.25 seconds
├─ Cost: 65 × $0.0001 = $0.0065
└─ Efficiency: 93.6% cached

Result: 230× FASTER, 230× CHEAPER! 🚀
```

---

## Implementation Summary

### Key Components:

1. **PageHash**: Fast content hashing for change detection
2. **ChangeSet**: Precisely what changed
3. **ScoreDependencyGraph**: What needs recalculation
4. **CachedScoreManager**: Store/retrieve computed values
5. **IncrementalScoreCalculator**: Recalc only what's needed
6. **HashingOptimizer**: Test changes efficiently

### The "Hashing" Hierarchy:

```
NANO → words/text strings (SHA256 hash)
  ↓
MICRO → components (title, H2s, sections)
  ↓
MESO → bundles (metadata, structure, content)
  ↓
MACRO → scores (alignment, coverage, structural)
  ↓
MEGA → overall composite score
```

### Optimization Strategy:

1. Hash initial page state (NANO level)
2. Generate candidate changes
3. For each candidate:
   - Apply change
   - Hash new state
   - Detect what changed (ChangeSet)
   - Recalc only impacted scores (incremental)
   - Cache new embeddings/scores
4. Keep best change if improvement ≥ threshold
5. Repeat until convergence

### Efficiency Gains:

- **Without hashing**: O(n × m) where n = changes, m = total embeddings
- **With hashing**: O(n × k) where k = changed embeddings (typically k << m)
- **Typical speedup**: 50-200×
- **Typical cost reduction**: 50-200×

---

## Next Steps

1. Implement PageHash and ChangeSet (foundational)
2. Build ScoreDependencyGraph (map dependencies)
3. Create CachedScoreManager (caching layer)
4. Build IncrementalScoreCalculator (the core)
5. Implement HashingOptimizer (optimization loop)
6. Test on real pages and measure efficiency

**This hashing strategy is what makes word-level optimization practical!** 🎯

