"""Database models for SEO Mining.

Adapted from Magic-SEO but extended with:
- Structural coherence scores (8+ dimensions)
- Optimization metadata (iterations, cache hits, etc.)
- Competitor benchmarking data
"""

import enum
import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, Float, DateTime, Enum,
    ForeignKey, Text, Boolean, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.database import Base


class JobStatus(str, enum.Enum):
    """Status of analysis or optimization job"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisJob(Base):
    """
    Represents a page analysis job.
    
    Tracks the overall job status and metadata.
    Pattern adapted from Magic-SEO's BulkAnalysisJob.
    """
    __tablename__ = "analysis_jobs"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Job Info
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    target_url = Column(String, nullable=False)
    target_keyword = Column(String, nullable=False)
    
    # Progress Tracking
    total_steps = Column(Integer, default=0)
    completed_steps = Column(Integer, default=0)
    
    # Results
    output_path = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Relationships
    results = relationship("AnalysisResult", back_populates="job", cascade="all, delete-orphan")
    
    @property
    def progress_percent(self) -> int:
        """Calculate progress percentage"""
        if self.total_steps == 0:
            return 0
        return int((self.completed_steps / self.total_steps) * 100)


class AnalysisResult(Base):
    """
    Stores comprehensive analysis results for a page.
    
    Includes:
    - All semantic scores (alignment, coverage, keyword presence)
    - All structural coherence scores (8+ dimensions)
    - Optimization metadata
    - Competitor benchmarking data
    
    Extended from Magic-SEO's BulkAnalysisResult with our unique scoring.
    """
    __tablename__ = "analysis_results"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Foreign Key
    job_id = Column(UUID(as_uuid=True), ForeignKey("analysis_jobs.id"), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Page Info
    url = Column(String, nullable=False)
    keyword = Column(String, nullable=False)
    status = Column(Enum(JobStatus), default=JobStatus.PENDING, nullable=False)
    
    # Processing Metadata
    processing_time_seconds = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # ============================================================
    # SEMANTIC SCORES (from Magic-SEO, kept)
    # ============================================================
    
    alignment_score = Column(Float, nullable=True)  # 0-1: semantic alignment with competitors
    coverage_score = Column(Float, nullable=True)   # 0-1: topic coverage vs competitors
    keyword_presence_score = Column(Float, nullable=True)  # 0-1: keyword in key locations
    
    # ============================================================
    # STRUCTURAL COHERENCE SCORES (our unique addition)
    # ============================================================
    
    metadata_alignment_score = Column(Float, nullable=True)  # 0-1: title/meta/H1 semantic alignment
    hierarchical_decomposition_score = Column(Float, nullable=True)  # 0-1: H1→H2→H3 hierarchy quality
    thematic_unity_score = Column(Float, nullable=True)  # 0-1: section-to-section coherence
    balance_score = Column(Float, nullable=True)  # 0-1: content distribution balance
    query_intent_score = Column(Float, nullable=True)  # 0-1: page vs query intent match
    
    # Aggregate structural score
    structural_coherence_score = Column(Float, nullable=True)  # 0-1: average of structural components
    
    # ============================================================
    # COMPOSITE SCORE (weighted average of all)
    # ============================================================
    
    composite_score = Column(Float, nullable=True)  # 0-1: overall page quality
    seo_score = Column(Integer, nullable=True)  # 0-100: composite × 100 for display
    
    # ============================================================
    # COMPETITOR BENCHMARKING (our addition)
    # ============================================================
    
    competitor_avg_score = Column(Float, nullable=True)  # Average competitor composite score
    competitor_best_score = Column(Float, nullable=True)  # Best competitor score
    competitor_worst_score = Column(Float, nullable=True)  # Worst competitor score
    competitor_top25_threshold = Column(Float, nullable=True)  # 75th percentile score
    your_percentile = Column(Integer, nullable=True)  # Your ranking percentile (0-100)
    competitor_count = Column(Integer, nullable=True)  # Number of competitors analyzed
    
    # ============================================================
    # OPTIMIZATION METADATA (our addition)
    # ============================================================
    
    optimization_iterations = Column(Integer, nullable=True, default=0)  # Number of optimization iterations run
    cache_hit_rate = Column(Float, nullable=True)  # % of embeddings served from cache
    total_variations_tested = Column(Integer, nullable=True)  # Total candidate variations tested
    improvements_found = Column(Integer, nullable=True)  # Number of score improvements found
    
    # ============================================================
    # GAP ANALYSIS (from Magic-SEO, kept)
    # ============================================================
    
    gap_1 = Column(String, nullable=True)  # Top missing topic
    gap_2 = Column(String, nullable=True)  # 2nd missing topic
    gap_3 = Column(String, nullable=True)  # 3rd missing topic
    
    # Detailed gaps stored as JSON
    detailed_gaps = Column(JSON, nullable=True)  # Full gap analysis with scores and recommendations
    
    # ============================================================
    # RANKING DATA (from Magic-SEO, kept)
    # ============================================================
    
    current_rank = Column(Integer, nullable=True)  # Current SERP position
    ranking_potential = Column(String, nullable=True)  # Estimated ranking potential after optimization
    
    # ============================================================
    # RAW DATA STORAGE
    # ============================================================
    
    page_content_path = Column(String, nullable=True)  # Path to stored HTML
    embeddings_path = Column(String, nullable=True)  # Path to stored embeddings cache
    
    # Relationships
    job = relationship("AnalysisJob", back_populates="results")
    
    def to_dict(self) -> dict:
        """Convert result to dictionary for API responses"""
        return {
            "id": str(self.id),
            "job_id": str(self.job_id),
            "url": self.url,
            "keyword": self.keyword,
            "status": self.status.value,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "processing_time_seconds": self.processing_time_seconds,
            
            # Semantic scores
            "alignment_score": self.alignment_score,
            "coverage_score": self.coverage_score,
            "keyword_presence_score": self.keyword_presence_score,
            
            # Structural coherence scores
            "metadata_alignment_score": self.metadata_alignment_score,
            "hierarchical_decomposition_score": self.hierarchical_decomposition_score,
            "thematic_unity_score": self.thematic_unity_score,
            "balance_score": self.balance_score,
            "query_intent_score": self.query_intent_score,
            "structural_coherence_score": self.structural_coherence_score,
            
            # Composite
            "composite_score": self.composite_score,
            "seo_score": self.seo_score,
            
            # Competitor benchmarking
            "competitor_avg_score": self.competitor_avg_score,
            "competitor_best_score": self.competitor_best_score,
            "your_percentile": self.your_percentile,
            
            # Optimization metadata
            "optimization_iterations": self.optimization_iterations,
            "cache_hit_rate": self.cache_hit_rate,
            "improvements_found": self.improvements_found,
            
            # Gaps
            "top_gaps": [self.gap_1, self.gap_2, self.gap_3],
            
            # Ranking
            "current_rank": self.current_rank,
            "ranking_potential": self.ranking_potential,
            
            "error_message": self.error_message,
        }


class CompetitorPage(Base):
    """
    Stores competitor page data for caching and analysis.
    
    Allows reusing competitor data across multiple analyses.
    """
    __tablename__ = "competitor_pages"
    
    # Primary Key
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Page Info
    url = Column(String, nullable=False, unique=True, index=True)
    keyword = Column(String, nullable=False, index=True)
    fetched_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # SERP Info
    serp_position = Column(Integer, nullable=True)
    
    # Scores (calculated once, reused)
    alignment_score = Column(Float, nullable=True)
    coverage_score = Column(Float, nullable=True)
    structural_coherence_score = Column(Float, nullable=True)
    composite_score = Column(Float, nullable=True)
    
    # Storage paths
    content_path = Column(String, nullable=True)
    embeddings_path = Column(String, nullable=True)
    
    # Freshness tracking
    is_stale = Column(Boolean, default=False)  # Mark as stale after X days

