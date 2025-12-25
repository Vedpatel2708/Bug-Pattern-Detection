# 🐛 Bug Pattern Detective

**AI-powered bug solution finder using RAG (Retrieval-Augmented Generation)**

A practical RAG project that helps developers find solutions to programming errors by learning from Stack Overflow, GitHub issues, and personal bug fix history.

---

## ✨ Features

- 🔍 **Semantic Search**: Find similar bugs using vector embeddings
- 🤖 **AI Solutions**: Get tailored solutions using Groq LLM (free!)
- 📚 **Multiple Sources**: Stack Overflow, GitHub, personal history
- 🆓 **100% Free**: No paid APIs required
- 💻 **Runs Locally**: All data stored on your machine
- 🎨 **User-Friendly UI**: Clean Streamlit interface

---

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
cd bug-pattern-detective

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Get Groq API Key (Free!)

1. Visit [console.groq.com](https://console.groq.com)
2. Sign up for free account
3. Create an API key
4. Copy the key (you'll need it in step 4)

### 3. Collect Bug Data

```bash
# Run data collector to generate sample dataset
python data_collector.py
```

This will create:
- `bug_data/bug_dataset_YYYYMMDD_HHMMSS.json` - Sample bugs from common patterns
- `bug_data/personal_bugs_template.json` - Template for your own bugs

### 4. Run the Application

```bash
# Start Streamlit UI
streamlit run bug_detective_ui.py
```

### 5. Use the System

1. Enter your Groq API key in the sidebar
2. Click "Initialize System"
3. Load sample data or upload your own
4. Paste your error message
5. Get AI-generated solutions! 🎉

---

## 📁 Project Structure

```
bug-pattern-detective/
├── bug_detective.py          # Main RAG system implementation
├── data_collector.py          # Data collection scripts
├── bug_detective_ui.py        # Streamlit web interface
├── requirements.txt           # Python dependencies
├── README.md                  # This file
└── bug_data/                  # Generated datasets (created after first run)
    ├── bug_dataset_*.json     # Collected bug data
    └── personal_bugs_template.json
```

---

## 💡 How It Works

### RAG Pipeline

```
User Error → Embedding → Vector Search → Retrieve Similar Bugs → LLM Context → AI Solution
```

1. **Data Collection**: Gather bugs from Stack Overflow, GitHub, personal fixes
2. **Embedding**: Convert bugs to vectors using sentence-transformers
3. **Indexing**: Store in ChromaDB vector database
4. **Query**: User submits error message
5. **Retrieval**: Find top-k similar bugs using cosine similarity
6. **Generation**: Groq LLM generates solution using retrieved context

### Tech Stack

| Component | Technology | Why? |
|-----------|-----------|------|
| **Vector DB** | ChromaDB | Free, local, easy to use |
| **Embeddings** | sentence-transformers | Free, runs locally, good quality |
| **LLM** | Groq API | Free tier, super fast inference |
| **Backend** | Python + FastAPI | Standard for ML/AI projects |
| **UI** | Streamlit | Quick prototyping, clean interface |

---

## 🎯 Usage Examples

### Example 1: Python TypeError

**Input:**
```
Traceback (most recent call last):
  File "app.py", line 15, in <module>
    result = data['users'][0]['name']
TypeError: 'NoneType' object is not subscriptable
```

**Output:**
- Identifies the issue (NoneType error)
- Finds 3 similar bugs from database
- Generates step-by-step solution
- Provides code examples
- Shows prevention tips

### Example 2: JavaScript Undefined Error

**Input:**
```
TypeError: Cannot read property 'map' of undefined
  at Component.render (App.js:25)
```

**Output:**
- Explains undefined vs null in JavaScript
- Shows safe array access patterns
- Demonstrates optional chaining
- Provides React-specific solutions

---

## 📊 Adding Your Own Bugs

### Option 1: Use the Template

Edit `bug_data/personal_bugs_template.json`:

```json
[
  {
    "error_pattern": "ConnectionRefusedError: [Errno 111]",
    "context": "Django connecting to PostgreSQL",
    "language": "python",
    "framework": "django",
    "problem_description": "Django couldn't connect to database on Docker",
    "solution": "Changed localhost to db service name in settings.py",
    "source": "personal",
    "confidence_score": 80,
    "tags": ["docker", "database", "django"],
    "date_fixed": "2024-01-15",
    "notes": "Remember to use Docker service names, not localhost!"
  }
]
```

### Option 2: Programmatic Addition

```python
from bug_detective import BugEntry, BugPatternDetective

detective = BugPatternDetective(groq_api_key="your-key")

new_bug = BugEntry(
    error_pattern="Your error here",
    context="What you were doing",
    language="python",
    framework="django",
    problem_description="Detailed description",
    solution="How you fixed it",
    source="personal",
    confidence_score=50,
    tags=["tag1", "tag2"]
)

detective.index_bugs([new_bug])
```

---

## 🔧 Advanced Configuration

### Customize Embedding Model

In `bug_detective.py`, change:
```python
self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
```

Options:
- `all-MiniLM-L6-v2` (default) - Fast, good quality
- `all-mpnet-base-v2` - Better quality, slower
- `multi-qa-mpnet-base-dot-v1` - Optimized for Q&A

### Customize Groq Model

```python
self.model = "llama-3.3-70b-versatile"  # Default
# self.model = "mixtral-8x7b-32768"      # Alternative
```

### Adjust Search Parameters

```python
# In generate_solution() method
similar_bugs = self.search_similar_bugs(
    error_query, 
    language, 
    top_k=5  # Change this to retrieve more/fewer bugs
)
```

---

## 🌟 Future Enhancements

- [ ] VS Code extension
- [ ] Browser extension for Stack Overflow
- [ ] CLI tool for terminal integration
- [ ] Error pattern clustering visualization
- [ ] Solution effectiveness tracking (thumbs up/down)
- [ ] Multi-modal support (screenshots of errors)
- [ ] Team collaboration features
- [ ] Integration with issue trackers (JIRA, GitHub)
- [ ] Automatic git commit message analysis

---

## 🤝 Contributing Ideas

Want to improve this project? Here are some ideas:

1. **Data Sources**: Add scrapers for more platforms (Reddit, forums)
2. **Language Support**: Add more programming languages
3. **UI Improvements**: Better visualization, dark mode
4. **Performance**: Optimize vector search, add caching
5. **Features**: Export solutions as markdown, PDF generation

---

## 🐛 Troubleshooting

### Issue: "ModuleNotFoundError"
**Solution**: Make sure you activated the virtual environment and installed all requirements

### Issue: "Groq API Error"
**Solution**: Check your API key is correct and you have free credits remaining

### Issue: "No similar bugs found"
**Solution**: Index more data using the data collector or add your own bugs

### Issue: "ChromaDB error"
**Solution**: Delete the `chroma_db` folder and re-initialize

---

## 📝 License

This is an educational project. Feel free to use, modify, and share!

---

## 🎓 Learning Resources

**RAG Concepts:**
- [Anthropic's RAG Documentation](https://docs.anthropic.com)
- Vector databases and embeddings
- Semantic search principles

**Tools Used:**
- [ChromaDB Docs](https://docs.trychroma.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [Groq API Docs](https://console.groq.com/docs)
- [Streamlit Docs](https://docs.streamlit.io/)

---

## 💬 Questions?

This is a learning project to understand RAG systems. Experiment, break things, and learn!

**Key Learning Points:**
✅ Vector embeddings and semantic search
✅ RAG architecture and implementation
✅ Working with LLM APIs
✅ Building practical AI applications
✅ Data collection and preprocessing

---

**Happy Debugging! 🐛🔍✨**
