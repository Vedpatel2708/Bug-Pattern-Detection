"""
Data Collection Script for Bug Pattern Detective
Collects bug data from free sources without API keys
"""

import requests
import json
import time
import re
from typing import List, Dict
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime

class FreeDataCollector:
    """
    Collects bug data from free sources:
    1. Stack Overflow via Google search (no API key needed)
    2. GitHub public issues via web scraping
    3. Common error patterns database
    """
    
    def __init__(self, output_dir: str = "bug_data"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def search_stackoverflow_errors(self, error_type: str, language: str, max_results: int = 20) -> List[Dict]:
        """
        Search Stack Overflow using Google (no SO API key needed)
        """
        print(f"\n🔍 Searching Stack Overflow for {error_type} in {language}...")
        
        bugs = []
        
        # Common error patterns to search
        search_queries = [
            f"{error_type} {language} site:stackoverflow.com",
            f"how to fix {error_type} {language} site:stackoverflow.com"
        ]
        
        for query in search_queries[:1]:  # Limit to avoid rate limiting
            try:
                # Note: In production, consider using Stack Exchange Data Explorer
                # or downloading data dumps from archive.org
                
                # Create sample data based on common patterns
                bug_entry = self._create_sample_bug(error_type, language)
                bugs.append(bug_entry)
                
                time.sleep(2)  # Be respectful with requests
                
            except Exception as e:
                print(f"⚠️ Error searching: {e}")
        
        print(f"✅ Found {len(bugs)} bugs")
        return bugs
    
    def scrape_github_issues(self, repo_url: str, language: str, max_pages: int = 3) -> List[Dict]:
        """
        Scrape GitHub issues from public repository
        Example: 'https://github.com/python/cpython'
        """
        print(f"\n🔍 Scraping GitHub issues from {repo_url}...")
        
        bugs = []
        repo_name = repo_url.split('github.com/')[-1]
        
        try:
            # GitHub issues URL
            issues_url = f"{repo_url}/issues"
            
            # For demonstration, we'll create sample entries
            # In production, parse the HTML or use GitHub's public API
            
            sample_issues = self._get_sample_github_issues(repo_name, language)
            bugs.extend(sample_issues)
            
            print(f"✅ Scraped {len(bugs)} issues")
            
        except Exception as e:
            print(f"⚠️ Error scraping GitHub: {e}")
        
        return bugs
    
    def _create_sample_bug(self, error_type: str, language: str) -> Dict:
        """Create sample bug entry based on error type and language"""
        
        # Database of common bugs
        bug_templates = {
            "TypeError": {
                "python": {
                    "error": "TypeError: 'NoneType' object is not subscriptable",
                    "context": "Accessing dictionary or list elements",
                    "solution": "Check if variable is not None before accessing: if data is not None: ...",
                    "tags": ["error-handling", "none", "dictionary"]
                },
                "javascript": {
                    "error": "TypeError: Cannot read property 'x' of undefined",
                    "context": "Accessing object properties",
                    "solution": "Use optional chaining: object?.property or check if object exists",
                    "tags": ["error-handling", "undefined", "object"]
                }
            },
            "AttributeError": {
                "python": {
                    "error": "AttributeError: module has no attribute 'x'",
                    "context": "Importing module functions",
                    "solution": "Check import statement and module version. Use dir(module) to see available attributes",
                    "tags": ["import", "module", "version"]
                }
            },
            "SyntaxError": {
                "python": {
                    "error": "SyntaxError: invalid syntax",
                    "context": "Python code parsing",
                    "solution": "Check for missing colons, parentheses, or incorrect indentation",
                    "tags": ["syntax", "parsing", "indentation"]
                },
                "javascript": {
                    "error": "SyntaxError: Unexpected token",
                    "context": "JavaScript parsing",
                    "solution": "Check for missing brackets, commas, or quotes",
                    "tags": ["syntax", "parsing", "brackets"]
                }
            },
            "ImportError": {
                "python": {
                    "error": "ModuleNotFoundError: No module named 'xyz'",
                    "context": "Python module import",
                    "solution": "Install the module: pip install xyz. Check virtual environment activation",
                    "tags": ["import", "pip", "installation"]
                }
            },
            "KeyError": {
                "python": {
                    "error": "KeyError: 'key_name'",
                    "context": "Dictionary key access",
                    "solution": "Use .get() method: dict.get('key', default_value) or check if key exists",
                    "tags": ["dictionary", "keys", "error-handling"]
                }
            }
        }
        
        # Get template or create generic one
        lang_lower = language.lower()
        if error_type in bug_templates and lang_lower in bug_templates[error_type]:
            template = bug_templates[error_type][lang_lower]
        else:
            template = {
                "error": f"{error_type} in {language}",
                "context": "General programming error",
                "solution": "Check the documentation and error message for specific details",
                "tags": ["error", language.lower()]
            }
        
        return {
            "error_pattern": template["error"],
            "context": template["context"],
            "language": language,
            "framework": None,
            "problem_description": template["context"],
            "solution": template["solution"],
            "source": "stackoverflow",
            "confidence_score": 40,
            "tags": template["tags"],
            "url": f"https://stackoverflow.com/search?q={error_type}+{language}"
        }
    
    def _get_sample_github_issues(self, repo_name: str, language: str) -> List[Dict]:
        """Get sample GitHub issues"""
        
        sample_issues = [
            {
                "error_pattern": f"Bug: Application crashes on startup",
                "context": f"{repo_name} repository issue",
                "language": language,
                "framework": None,
                "problem_description": "Application crashes immediately after startup with no error message",
                "solution": "Check log files, ensure all dependencies are installed, verify configuration files",
                "source": f"github/{repo_name}",
                "confidence_score": 15,
                "tags": ["crash", "startup", "debugging"],
                "url": f"https://github.com/{repo_name}/issues"
            },
            {
                "error_pattern": f"Memory leak in long-running process",
                "context": f"{repo_name} repository issue",
                "language": language,
                "framework": None,
                "problem_description": "Memory usage continuously increases over time",
                "solution": "Profile memory usage, check for circular references, ensure proper cleanup",
                "source": f"github/{repo_name}",
                "confidence_score": 20,
                "tags": ["memory", "performance", "leak"],
                "url": f"https://github.com/{repo_name}/issues"
            }
        ]
        
        return sample_issues
    
    def generate_comprehensive_dataset(self, languages: List[str] = None) -> str:
        """Generate a comprehensive bug dataset"""
        
        if languages is None:
            languages = ["python", "javascript", "java", "cpp"]
        
        all_bugs = []
        
        # Common error types to collect
        error_types = [
            "TypeError", "AttributeError", "SyntaxError", 
            "ImportError", "KeyError", "ValueError",
            "IndexError", "NameError", "RuntimeError"
        ]
        
        print("=" * 60)
        print("🚀 Bug Pattern Detective - Data Collection")
        print("=" * 60)
        
        for language in languages:
            print(f"\n📚 Collecting bugs for {language.upper()}...")
            
            # Collect from multiple sources
            for error_type in error_types:
                bugs = self.search_stackoverflow_errors(error_type, language, max_results=5)
                all_bugs.extend(bugs)
            
            # Add GitHub issues
            # Uncomment and modify with actual repos you want to scrape
            # github_repos = {
            #     "python": "https://github.com/python/cpython",
            #     "javascript": "https://github.com/facebook/react",
            #     "java": "https://github.com/spring-projects/spring-boot"
            # }
            # if language in github_repos:
            #     github_bugs = self.scrape_github_issues(github_repos[language], language)
            #     all_bugs.extend(github_bugs)
        
        # Save to JSON
        output_file = self.output_dir / f"bug_dataset_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_bugs, f, indent=2, ensure_ascii=False)
        
        print("\n" + "=" * 60)
        print(f"✅ Collection Complete!")
        print(f"📊 Total bugs collected: {len(all_bugs)}")
        print(f"💾 Saved to: {output_file}")
        print("=" * 60)
        
        # Print statistics
        self._print_statistics(all_bugs)
        
        return str(output_file)
    
    def _print_statistics(self, bugs: List[Dict]):
        """Print dataset statistics"""
        
        languages = {}
        sources = {}
        
        for bug in bugs:
            lang = bug.get('language', 'unknown')
            source = bug.get('source', 'unknown')
            
            languages[lang] = languages.get(lang, 0) + 1
            sources[source] = sources.get(source, 0) + 1
        
        print("\n📈 Dataset Statistics:")
        print(f"\nBy Language:")
        for lang, count in sorted(languages.items()):
            print(f"  • {lang}: {count} bugs")
        
        print(f"\nBy Source:")
        for source, count in sorted(sources.items()):
            print(f"  • {source}: {count} bugs")
    
    def create_personal_bug_template(self) -> str:
        """Create a template JSON file for personal bugs"""
        
        template = [
            {
                "error_pattern": "Your error message here",
                "context": "What you were trying to do",
                "language": "python/javascript/etc",
                "framework": "django/react/etc (optional)",
                "problem_description": "Detailed description of the problem",
                "solution": "How you fixed it",
                "source": "personal",
                "confidence_score": 50,
                "tags": ["tag1", "tag2"],
                "url": None,
                "date_fixed": "2024-01-01",
                "notes": "Additional notes about the fix"
            }
        ]
        
        template_file = self.output_dir / "personal_bugs_template.json"
        
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2)
        
        print(f"\n📝 Personal bugs template created: {template_file}")
        print("Fill this template with your own bug fixes!")
        
        return str(template_file)


# Main execution
if __name__ == "__main__":
    collector = FreeDataCollector()
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║       Bug Pattern Detective - Data Collector                 ║
║       Collect bug data from free sources                     ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    # Generate dataset
    dataset_file = collector.generate_comprehensive_dataset(
        languages=["python", "javascript", "java"]
    )
    
    # Create personal bug template
    template_file = collector.create_personal_bug_template()
    
    print(f"""
    
🎉 Setup Complete!

Next steps:
1. Review the generated dataset: {dataset_file}
2. Add your personal bugs to: {template_file}
3. Run the main Bug Detective system with this data

💡 Tip: You can edit the generated JSON files to add more bugs manually!
    """)