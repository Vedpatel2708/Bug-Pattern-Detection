"""
Bug Pattern Detective - RAG System for Bug Solutions
Main pipeline implementation with Groq API and free tools
"""

import os
import json
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

# Core dependencies (install via: pip install chromadb sentence-transformers groq requests beautifulsoup4)
import chromadb
from sentence_transformers import SentenceTransformer
from groq import Groq
import requests
from bs4 import BeautifulSoup

@dataclass
class BugEntry:
    """Structure for bug data"""
    error_pattern: str
    context: str
    language: str
    framework: Optional[str]
    problem_description: str
    solution: str
    source: str
    confidence_score: int
    tags: List[str]
    url: Optional[str] = None
    
    def to_dict(self):
        return {
            'error_pattern': self.error_pattern,
            'context': self.context,
            'language': self.language,
            'framework': self.framework,
            'problem_description': self.problem_description,
            'solution': self.solution,
            'source': self.source,
            'confidence_score': self.confidence_score,
            'tags': self.tags,
            'url': self.url
        }

class DataCollector:
    """Collects bug data from various free sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'BugDetective/1.0 (Educational Project)'
        })
    
    def scrape_github_issues(self, repo: str, language: str, max_issues: int = 50) -> List[BugEntry]:
        """
        Scrape GitHub issues from public repos (no API key needed for public data)
        Example repo: 'facebook/react', 'python/cpython'
        """
        entries = []
        url = f"https://github.com/{repo}/issues"
        
        try:
            # Note: For production, use GitHub API with personal token (free)
            # This is a simplified scraper for demonstration
            print(f"Scraping {repo} issues... (simplified version)")
            
            # In real implementation, you'd parse the HTML or use GitHub API
            # For now, we'll show the structure
            sample_entry = BugEntry(
                error_pattern="AttributeError: 'NoneType' object has no attribute 'get'",
                context="Accessing nested dictionary values",
                language=language,
                framework=None,
                problem_description="Getting AttributeError when trying to access nested dict",
                solution="Use .get() method with default values or check for None first",
                source=f"github/{repo}",
                confidence_score=10,
                tags=["error-handling", "dictionary"],
                url=url
            )
            entries.append(sample_entry)
            
        except Exception as e:
            print(f"Error scraping GitHub: {e}")
        
        return entries
    
    def parse_stackoverflow_dump(self, dump_path: str, language: str, max_entries: int = 100) -> List[BugEntry]:
        """
        Parse Stack Overflow data dump (download from archive.org/details/stackexchange)
        The dumps are in XML format
        """
        entries = []
        
        # For demonstration, creating sample entries
        # In real implementation, you'd parse the XML files: Posts.xml, Comments.xml
        print(f"Parsing Stack Overflow dump for {language}...")
        
        sample_bugs = [
            {
                "error": "TypeError: Cannot read property 'map' of undefined",
                "context": "React component trying to map over undefined array",
                "solution": "Check if array exists before mapping: {array && array.map(...)}",
                "tags": ["javascript", "react", "array"],
                "score": 45
            },
            {
                "error": "IndentationError: expected an indented block",
                "context": "Python function definition",
                "solution": "Add proper indentation (4 spaces) after function declaration",
                "tags": ["python", "syntax"],
                "score": 30
            },
            {
                "error": "ModuleNotFoundError: No module named 'xyz'",
                "context": "Python import statement",
                "solution": "Install the module using: pip install xyz",
                "tags": ["python", "import", "pip"],
                "score": 50
            }
        ]
        
        for bug in sample_bugs:
            entry = BugEntry(
                error_pattern=bug["error"],
                context=bug["context"],
                language=language,
                framework=None,
                problem_description=bug["context"],
                solution=bug["solution"],
                source="stackoverflow",
                confidence_score=bug["score"],
                tags=bug["tags"]
            )
            entries.append(entry)
        
        return entries
    
    def load_personal_bugs(self, json_file: str) -> List[BugEntry]:
        """Load your personal bug fixes from JSON file"""
        entries = []
        
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                for item in data:
                    entry = BugEntry(**item)
                    entries.append(entry)
        except FileNotFoundError:
            print(f"Personal bugs file not found: {json_file}")
        except Exception as e:
            print(f"Error loading personal bugs: {e}")
        
        return entries


class BugPatternDetective:
    """Main RAG system for bug pattern detection"""
    
    def __init__(self, groq_api_key: str, collection_name: str = "bug_patterns"):
        # Initialize embedding model (runs locally, free)
        print("Loading embedding model...")
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Initialize ChromaDB (local, free)
        print("Initializing ChromaDB...")
        self.chroma_client = chromadb.Client()
        self.collection = self.chroma_client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize Groq client
        self.groq_client = Groq(api_key=groq_api_key)
        self.model = "llama-3.3-70b-versatile"  # Fast and free on Groq
        
        print("Bug Pattern Detective initialized!")
    
    def extract_error_pattern(self, error_text: str) -> str:
        """Extract the core error pattern from full stack trace"""
        # Simple regex to find common error patterns
        patterns = [
            r'(\w+Error: .+)',
            r'(\w+Exception: .+)',
            r'(Error: .+)',
            r'(Exception: .+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, error_text)
            if match:
                return match.group(1).split('\n')[0]  # First line only
        
        return error_text[:200]  # Fallback: first 200 chars
    
    def index_bugs(self, bug_entries: List[BugEntry]):
        """Index bug entries into vector database"""
        print(f"Indexing {len(bug_entries)} bug entries...")
        
        for idx, bug in enumerate(bug_entries):
            # Create searchable text combining all relevant fields
            searchable_text = f"""
            Error: {bug.error_pattern}
            Context: {bug.context}
            Language: {bug.language}
            Problem: {bug.problem_description}
            Tags: {', '.join(bug.tags)}
            """
            
            # Generate embedding
            embedding = self.embedding_model.encode(searchable_text).tolist()
            
            # Store in ChromaDB
            self.collection.add(
                embeddings=[embedding],
                documents=[searchable_text],
                metadatas=[bug.to_dict()],
                ids=[f"bug_{idx}_{bug.source}"]
            )
        
        print(f"Indexed {len(bug_entries)} bugs successfully!")
    
    def search_similar_bugs(self, error_query: str, language: str = None, top_k: int = 5) -> List[Dict]:
        """Search for similar bugs in the vector database"""
        # Extract core error pattern
        error_pattern = self.extract_error_pattern(error_query)
        
        # Build search query
        search_text = f"Error: {error_pattern}"
        if language:
            search_text += f" Language: {language}"
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode(search_text).tolist()
        
        # Search in ChromaDB
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        # Format results
        similar_bugs = []
        if results['metadatas']:
            for metadata, distance in zip(results['metadatas'][0], results['distances'][0]):
                bug_info = metadata.copy()
                bug_info['similarity_score'] = 1 - distance  # Convert distance to similarity
                similar_bugs.append(bug_info)
        
        return similar_bugs
    
    def generate_solution(self, error_query: str, language: str = None, context: str = None) -> str:
        """Generate solution using Groq LLM with RAG context"""
        # Retrieve similar bugs
        similar_bugs = self.search_similar_bugs(error_query, language, top_k=3)
        
        # Build context from retrieved bugs
        rag_context = "Here are similar bugs and their solutions:\n\n"
        for i, bug in enumerate(similar_bugs, 1):
            rag_context += f"""
Bug {i} (Confidence: {bug['confidence_score']}, Similarity: {bug['similarity_score']:.2f}):
Error: {bug['error_pattern']}
Context: {bug['context']}
Solution: {bug['solution']}
Source: {bug['source']}
---
"""
        
        # Build prompt for Groq
        prompt = f"""You are a debugging expert. Based on similar bugs found in the database, help solve this error.

USER'S ERROR:
{error_query}

LANGUAGE: {language or 'Not specified'}
ADDITIONAL CONTEXT: {context or 'None provided'}

{rag_context}

Based on the similar bugs above, provide:
1. Likely cause of the error
2. Step-by-step solution
3. Code example if applicable
4. Prevention tips

Keep your response clear and practical."""

        try:
            # Call Groq API
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert debugging assistant. Provide clear, actionable solutions based on the provided context."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                model=self.model,
                temperature=0.3,
                max_tokens=1000
            )
            
            solution = chat_completion.choices[0].message.content
            
            # Append sources
            solution += "\n\n📚 **Similar Cases Found:**\n"
            for bug in similar_bugs:
                solution += f"- {bug['error_pattern']} (Score: {bug['confidence_score']})\n"
            
            return solution
            
        except Exception as e:
            return f"Error generating solution: {str(e)}"


# Example usage
if __name__ == "__main__":
    # Initialize system
    GROQ_API_KEY = "your-groq-api-key-here"  # Get free key from console.groq.com
    
    detective = BugPatternDetective(groq_api_key=GROQ_API_KEY)
    
    # Collect data
    collector = DataCollector()
    
    # Load sample data from Stack Overflow dump
    bugs = collector.parse_stackoverflow_dump("", "python", max_entries=50)
    
    # You can also add GitHub issues
    # bugs.extend(collector.scrape_github_issues("python/cpython", "python", max_issues=20))
    
    # Index all bugs
    detective.index_bugs(bugs)
    
    # Example: Search for solution
    error = """
    Traceback (most recent call last):
      File "app.py", line 15, in <module>
        result = data['users'][0]['name']
    TypeError: 'NoneType' object is not subscriptable
    """
    
    solution = detective.generate_solution(
        error_query=error,
        language="python",
        context="Trying to access user data from API response"
    )
    
    print("\n" + "="*50)
    print("SOLUTION:")
    print("="*50)
    print(solution)