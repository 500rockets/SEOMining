"""
Content Chunking Utilities
Handles intelligent splitting of long content for embedding generation
"""
import re
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class Chunk:
    """Represents a content chunk with metadata"""
    text: str
    start_idx: int
    end_idx: int
    chunk_type: str  # 'heading', 'paragraph', 'list', etc.
    metadata: Optional[Dict] = None


class ContentChunker:
    """
    Intelligent content chunker for semantic analysis
    Splits content while preserving semantic boundaries
    """
    
    def __init__(
        self,
        chunk_size: int = 512,
        overlap: int = 50,
        min_chunk_size: int = 50,
        respect_boundaries: bool = True
    ):
        """
        Initialize chunker
        
        Args:
            chunk_size: Target size for each chunk (in characters)
            overlap: Overlap between chunks for context preservation
            min_chunk_size: Minimum chunk size to keep
            respect_boundaries: Try to split on sentence/paragraph boundaries
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_chunk_size = min_chunk_size
        self.respect_boundaries = respect_boundaries
    
    def chunk_text(self, text: str) -> List[Chunk]:
        """
        Split text into semantic chunks
        
        Args:
            text: Input text to chunk
            
        Returns:
            List of Chunk objects
        """
        if len(text) < self.min_chunk_size:
            return [Chunk(
                text=text,
                start_idx=0,
                end_idx=len(text),
                chunk_type='short'
            )]
        
        if self.respect_boundaries:
            return self._chunk_with_boundaries(text)
        else:
            return self._chunk_fixed_size(text)
    
    def _chunk_fixed_size(self, text: str) -> List[Chunk]:
        """Split text into fixed-size chunks with overlap"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            
            chunk_text = text[start:end].strip()
            if len(chunk_text) >= self.min_chunk_size:
                chunks.append(Chunk(
                    text=chunk_text,
                    start_idx=start,
                    end_idx=end,
                    chunk_type='fixed'
                ))
            
            start += self.chunk_size - self.overlap
        
        return chunks
    
    def _chunk_with_boundaries(self, text: str) -> List[Chunk]:
        """
        Split text respecting semantic boundaries (sentences, paragraphs)
        """
        # First, try to split on paragraphs
        paragraphs = self._split_paragraphs(text)
        
        chunks = []
        current_chunk = ""
        current_start = 0
        
        for para in paragraphs:
            # If adding this paragraph exceeds chunk size
            if len(current_chunk) + len(para) > self.chunk_size:
                # Save current chunk if it's not empty
                if current_chunk.strip():
                    chunks.append(Chunk(
                        text=current_chunk.strip(),
                        start_idx=current_start,
                        end_idx=current_start + len(current_chunk),
                        chunk_type='paragraph'
                    ))
                
                # If paragraph itself is too long, split by sentences
                if len(para) > self.chunk_size:
                    sentence_chunks = self._split_long_paragraph(para, current_start + len(current_chunk))
                    chunks.extend(sentence_chunks)
                    current_chunk = ""
                    current_start = chunks[-1].end_idx if chunks else 0
                else:
                    current_chunk = para
                    current_start = current_start + len(current_chunk)
            else:
                current_chunk += "\n\n" + para if current_chunk else para
        
        # Add remaining chunk
        if current_chunk.strip():
            chunks.append(Chunk(
                text=current_chunk.strip(),
                start_idx=current_start,
                end_idx=current_start + len(current_chunk),
                chunk_type='paragraph'
            ))
        
        return chunks
    
    def _split_paragraphs(self, text: str) -> List[str]:
        """Split text into paragraphs"""
        # Split on double newlines or multiple spaces/tabs
        paragraphs = re.split(r'\n\s*\n|\r\n\s*\r\n', text)
        return [p.strip() for p in paragraphs if p.strip()]
    
    def _split_long_paragraph(self, paragraph: str, start_offset: int) -> List[Chunk]:
        """Split a long paragraph into sentence-based chunks"""
        # Split on sentence boundaries
        sentences = re.split(r'(?<=[.!?])\s+', paragraph)
        
        chunks = []
        current_chunk = ""
        current_start = start_offset
        
        for sentence in sentences:
            if len(current_chunk) + len(sentence) > self.chunk_size:
                if current_chunk.strip():
                    chunks.append(Chunk(
                        text=current_chunk.strip(),
                        start_idx=current_start,
                        end_idx=current_start + len(current_chunk),
                        chunk_type='sentence'
                    ))
                current_chunk = sentence
                current_start = current_start + len(current_chunk)
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        if current_chunk.strip():
            chunks.append(Chunk(
                text=current_chunk.strip(),
                start_idx=current_start,
                end_idx=current_start + len(current_chunk),
                chunk_type='sentence'
            ))
        
        return chunks
    
    def chunk_with_metadata(
        self,
        text: str,
        document_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Chunk text and include metadata
        
        Args:
            text: Input text
            document_metadata: Metadata to attach to all chunks
            
        Returns:
            List of dicts with 'text' and 'metadata'
        """
        chunks = self.chunk_text(text)
        
        results = []
        for i, chunk in enumerate(chunks):
            metadata = {
                'chunk_index': i,
                'total_chunks': len(chunks),
                'start_idx': chunk.start_idx,
                'end_idx': chunk.end_idx,
                'chunk_type': chunk.chunk_type,
                'char_count': len(chunk.text)
            }
            
            # Merge with document metadata
            if document_metadata:
                metadata.update(document_metadata)
            
            results.append({
                'text': chunk.text,
                'metadata': metadata
            })
        
        return results


class HierarchicalChunker:
    """
    Hierarchical content chunker that preserves document structure
    Useful for HTML/Markdown with headings
    """
    
    def __init__(
        self,
        max_chunk_size: int = 1024,
        min_chunk_size: int = 50
    ):
        self.max_chunk_size = max_chunk_size
        self.min_chunk_size = min_chunk_size
    
    def chunk_html(self, html: str) -> List[Dict]:
        """
        Chunk HTML content preserving hierarchical structure
        
        Args:
            html: HTML content
            
        Returns:
            List of chunks with hierarchical metadata
        """
        try:
            from bs4 import BeautifulSoup
        except ImportError:
            logger.error("beautifulsoup_not_installed")
            raise ImportError("beautifulsoup4 is required for HTML chunking")
        
        soup = BeautifulSoup(html, 'html.parser')
        chunks = []
        
        # Extract main content (remove script, style, etc.)
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        
        # Process by sections (based on headings)
        current_section = {
            'heading': None,
            'level': 0,
            'content': []
        }
        
        for element in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li']):
            if element.name.startswith('h'):
                # New section
                if current_section['content']:
                    chunks.extend(self._process_section(current_section))
                
                current_section = {
                    'heading': element.get_text().strip(),
                    'level': int(element.name[1]),
                    'content': []
                }
            else:
                text = element.get_text().strip()
                if text:
                    current_section['content'].append(text)
        
        # Process last section
        if current_section['content']:
            chunks.extend(self._process_section(current_section))
        
        return chunks
    
    def _process_section(self, section: Dict) -> List[Dict]:
        """Process a section into chunks"""
        content = '\n'.join(section['content'])
        
        # If section is small enough, return as single chunk
        if len(content) <= self.max_chunk_size:
            return [{
                'text': content,
                'metadata': {
                    'heading': section['heading'],
                    'level': section['level'],
                    'chunk_type': 'section'
                }
            }]
        
        # Otherwise, split into smaller chunks
        chunker = ContentChunker(
            chunk_size=self.max_chunk_size,
            overlap=50,
            min_chunk_size=self.min_chunk_size
        )
        
        chunks = chunker.chunk_with_metadata(
            content,
            document_metadata={
                'heading': section['heading'],
                'level': section['level']
            }
        )
        
        return chunks


def chunk_for_embeddings(
    text: str,
    chunk_size: int = 512,
    overlap: int = 50,
    preserve_structure: bool = True
) -> List[str]:
    """
    Convenience function to chunk text for embedding generation
    
    Args:
        text: Input text
        chunk_size: Target chunk size
        overlap: Overlap between chunks
        preserve_structure: Respect paragraph/sentence boundaries
        
    Returns:
        List of text chunks
    """
    chunker = ContentChunker(
        chunk_size=chunk_size,
        overlap=overlap,
        respect_boundaries=preserve_structure
    )
    
    chunks = chunker.chunk_text(text)
    return [chunk.text for chunk in chunks]


def estimate_tokens(text: str) -> int:
    """
    Rough estimate of token count (for planning chunk sizes)
    Assumes ~4 characters per token on average
    """
    return len(text) // 4

