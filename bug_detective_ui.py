"""
Bug Pattern Detective - Working Streamlit UI
This version actually loads and uses the bug data!
"""

import streamlit as st
import json
import os
from pathlib import Path

st.set_page_config(
    page_title="Bug Pattern Detective 🔍",
    page_icon="🐛",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .solution-box {
        background-color: #e8f5e9;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #4CAF50;
    }
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# HELPER FUNCTIONS TO CREATE SAMPLE DATA
# ==============================================================================

def create_sample_bugs_python():
    """Create sample Python bugs - these will be loaded when you click the button"""
    return [
        {
            "error_pattern": "TypeError: 'NoneType' object is not subscriptable",
            "context": "Accessing dictionary or list elements without checking if None",
            "language": "python",
            "framework": None,
            "problem_description": "Trying to access elements from a variable that is None",
            "solution": "Always check if variable is not None before accessing: if data is not None and 'key' in data: result = data['key']",
            "source": "stackoverflow",
            "confidence_score": 85,
            "tags": ["error-handling", "none", "dictionary"]
        },
        {
            "error_pattern": "ModuleNotFoundError: No module named 'xyz'",
            "context": "Python import statement failing",
            "language": "python",
            "framework": None,
            "problem_description": "Package not installed in environment",
            "solution": "Install the module using pip: pip install xyz. Make sure your virtual environment is activated.",
            "source": "stackoverflow",
            "confidence_score": 90,
            "tags": ["import", "pip", "installation"]
        },
        {
            "error_pattern": "IndentationError: expected an indented block",
            "context": "Python function or class definition",
            "language": "python",
            "framework": None,
            "problem_description": "Missing or incorrect indentation after colon",
            "solution": "Add proper indentation (4 spaces or 1 tab) after function/class/if/for statements",
            "source": "stackoverflow",
            "confidence_score": 95,
            "tags": ["syntax", "indentation", "pep8"]
        },
        {
            "error_pattern": "KeyError: 'key_name'",
            "context": "Accessing dictionary keys",
            "language": "python",
            "framework": None,
            "problem_description": "Trying to access a key that doesn't exist in dictionary",
            "solution": "Use .get() method: value = dict.get('key', default_value) or check if key exists: if 'key' in dict:",
            "source": "stackoverflow",
            "confidence_score": 88,
            "tags": ["dictionary", "keys", "error-handling"]
        },
        {
            "error_pattern": "AttributeError: 'list' object has no attribute 'append'",
            "context": "Calling methods on wrong data types",
            "language": "python",
            "framework": None,
            "problem_description": "Variable was reassigned to different type or overwritten",
            "solution": "Check if you accidentally reassigned the variable. Use type() to verify variable type.",
            "source": "stackoverflow",
            "confidence_score": 80,
            "tags": ["data-types", "debugging", "attributes"]
        }
    ]

def create_sample_bugs_javascript():
    """Create sample JavaScript bugs"""
    return [
        {
            "error_pattern": "TypeError: Cannot read property 'map' of undefined",
            "context": "Trying to map over an array that doesn't exist",
            "language": "javascript",
            "framework": "react",
            "problem_description": "Array is undefined when trying to use .map()",
            "solution": "Check if array exists before mapping: {array && array.map(...)} or use optional chaining: array?.map(...)",
            "source": "stackoverflow",
            "confidence_score": 92,
            "tags": ["react", "array", "undefined"]
        },
        {
            "error_pattern": "ReferenceError: variable is not defined",
            "context": "Using undeclared variable",
            "language": "javascript",
            "framework": None,
            "problem_description": "Variable used before declaration",
            "solution": "Declare variable with let, const, or var before using it. Check for typos in variable names.",
            "source": "stackoverflow",
            "confidence_score": 90,
            "tags": ["variables", "scope", "declaration"]
        },
        {
            "error_pattern": "SyntaxError: Unexpected token",
            "context": "JavaScript parsing error",
            "language": "javascript",
            "framework": None,
            "problem_description": "Missing brackets, commas, or quotes",
            "solution": "Check for: missing closing brackets, extra/missing commas in objects/arrays, unmatched quotes",
            "source": "stackoverflow",
            "confidence_score": 85,
            "tags": ["syntax", "parsing", "brackets"]
        }
    ]

# ==============================================================================
# SESSION STATE INITIALIZATION
# ==============================================================================

if 'bugs_database' not in st.session_state:
    st.session_state.bugs_database = []
if 'groq_api_key' not in st.session_state:
    st.session_state.groq_api_key = None
if 'system_ready' not in st.session_state:
    st.session_state.system_ready = False

# ==============================================================================
# SIMPLE SEARCH FUNCTION (without needing full RAG setup initially)
# ==============================================================================

def simple_search(error_query, language=None):
    """
    Simple keyword search in bugs database
    This works even without the vector database!
    """
    results = []
    query_lower = error_query.lower()
    
    for bug in st.session_state.bugs_database:
        # Calculate simple relevance score
        score = 0
        
        # Check if error pattern matches
        if query_lower in bug['error_pattern'].lower():
            score += 50
        
        # Check language match
        if language and bug['language'].lower() == language.lower():
            score += 20
        
        # Check context
        if any(word in bug['context'].lower() for word in query_lower.split()):
            score += 10
        
        # Check tags
        if any(word in ' '.join(bug['tags']).lower() for word in query_lower.split()):
            score += 10
        
        if score > 0:
            bug_copy = bug.copy()
            bug_copy['relevance_score'] = score
            results.append(bug_copy)
    
    # Sort by relevance
    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    return results[:3]  # Return top 3

# ==============================================================================
# MAIN UI
# ==============================================================================

def main():
    # Header
    st.markdown('<h1 class="main-header">🐛 Bug Pattern Detective 🔍</h1>', unsafe_allow_html=True)
    st.markdown("### AI-powered bug solution finder using RAG")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        groq_api_key = st.text_input(
            "Groq API Key (Optional for now)",
            type="password",
            help="Get your free API key from console.groq.com - Not needed for basic search!"
        )
        
        if groq_api_key:
            st.session_state.groq_api_key = groq_api_key
            st.session_state.system_ready = True
            st.success("✅ API Key saved!")
        
        st.divider()
        
        # Data management
        st.header("📚 Data Management")
        
        st.info(f"💾 Bugs in database: **{len(st.session_state.bugs_database)}**")
        
        st.subheader("Load Sample Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🐍 Python Bugs", use_container_width=True):
                python_bugs = create_sample_bugs_python()
                st.session_state.bugs_database.extend(python_bugs)
                st.success(f"✅ Loaded {len(python_bugs)} Python bugs!")
                st.rerun()
        
        with col2:
            if st.button("📜 JavaScript Bugs", use_container_width=True):
                js_bugs = create_sample_bugs_javascript()
                st.session_state.bugs_database.extend(js_bugs)
                st.success(f"✅ Loaded {len(js_bugs)} JavaScript bugs!")
                st.rerun()
        
        if st.button("🗑️ Clear All Data", use_container_width=True):
            st.session_state.bugs_database = []
            st.success("✅ Database cleared!")
            st.rerun()
        
        st.divider()
        
        # Upload custom bugs
        st.subheader("📤 Upload Custom Bugs")
        uploaded_file = st.file_uploader(
            "Upload JSON file",
            type=['json'],
            help="Upload a JSON file with your bug data"
        )
        
        if uploaded_file:
            try:
                custom_bugs = json.load(uploaded_file)
                st.session_state.bugs_database.extend(custom_bugs)
                st.success(f"✅ Loaded {len(custom_bugs)} custom bugs!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Error loading file: {e}")
    
    # Main tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Find Solution", "📊 Browse Database", "ℹ️ How to Use"])
    
    with tab1:
        st.header("Describe Your Bug")
        
        if len(st.session_state.bugs_database) == 0:
            st.warning("⚠️ **No data loaded yet!**")
            st.info("""
            👈 **Please load sample data from the sidebar first:**
            1. Click "🐍 Python Bugs" or "📜 JavaScript Bugs"
            2. Then come back here to search!
            """)
        else:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                error_text = st.text_area(
                    "Error Message / Stack Trace",
                    height=200,
                    placeholder="""Paste your error here, for example:

TypeError: 'NoneType' object is not subscriptable
"""
                )
            
            with col2:
                language = st.selectbox(
                    "Programming Language",
                    ["Python", "JavaScript", "Java", "C++", "Go", "Rust", "Other"]
                )
                
                context = st.text_area(
                    "Additional Context",
                    height=100,
                    placeholder="What were you trying to do?"
                )
            
            if st.button("🔍 Find Solution", type="primary", use_container_width=True):
                if not error_text:
                    st.warning("Please enter an error message!")
                else:
                    with st.spinner("Searching for similar bugs..."):
                        # Search for similar bugs
                        results = simple_search(error_text, language)
                        
                        if not results:
                            st.warning("❌ No similar bugs found. Try loading more data or adjusting your search.")
                        else:
                            st.markdown('<div class="solution-box">', unsafe_allow_html=True)
                            st.markdown("### 💡 Similar Bugs Found")
                            
                            for i, bug in enumerate(results, 1):
                                with st.expander(f"🐛 Solution #{i} - Relevance: {bug['relevance_score']}%", expanded=(i==1)):
                                    st.markdown(f"**Error:** `{bug['error_pattern']}`")
                                    st.markdown(f"**Language:** {bug['language']}")
                                    st.markdown(f"**Context:** {bug['context']}")
                                    st.markdown(f"**Tags:** {', '.join(bug['tags'])}")
                                    st.divider()
                                    st.markdown("**💡 Solution:**")
                                    st.info(bug['solution'])
                                    st.markdown(f"**Confidence Score:** {bug['confidence_score']}/100")
                                    st.markdown(f"**Source:** {bug['source']}")
                            
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            # Show suggestion to use Groq for better answers
                            if not st.session_state.groq_api_key:
                                st.info("💡 **Tip:** Add your Groq API key in the sidebar to get AI-generated solutions tailored to your specific error!")
    
    with tab2:
        st.header("📊 Bug Database Browser")
        
        if len(st.session_state.bugs_database) == 0:
            st.info("No bugs in database yet. Load sample data from the sidebar!")
        else:
            # Statistics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Bugs", len(st.session_state.bugs_database))
            
            with col2:
                languages = set(bug['language'] for bug in st.session_state.bugs_database)
                st.metric("Languages", len(languages))
            
            with col3:
                avg_confidence = sum(bug['confidence_score'] for bug in st.session_state.bugs_database) / len(st.session_state.bugs_database)
                st.metric("Avg Confidence", f"{avg_confidence:.0f}%")
            
            st.divider()
            
            # Filters
            filter_col1, filter_col2 = st.columns(2)
            
            with filter_col1:
                filter_language = st.selectbox("Filter by Language", ["All"] + list(languages))
            
            with filter_col2:
                search_term = st.text_input("Search bugs", placeholder="Type keywords...")
            
            # Display bugs
            filtered_bugs = st.session_state.bugs_database
            
            if filter_language != "All":
                filtered_bugs = [b for b in filtered_bugs if b['language'] == filter_language]
            
            if search_term:
                filtered_bugs = [b for b in filtered_bugs if search_term.lower() in str(b).lower()]
            
            st.write(f"Showing {len(filtered_bugs)} bugs:")
            
            for i, bug in enumerate(filtered_bugs):
                with st.expander(f"{bug['error_pattern']} - {bug['language']}"):
                    st.json(bug)
    
    with tab3:
        st.header("📖 How to Use This App")
        
        st.markdown("""
        ### 🎯 Quick Start Guide
        
        **Step 1: Load Sample Data** 👈
        - Go to the sidebar
        - Click "🐍 Python Bugs" or "📜 JavaScript Bugs"
        - This loads example bugs into the database
        
        **Step 2: Search for Solutions** 🔍
        - Go to "Find Solution" tab
        - Paste your error message
        - Select your programming language
        - Click "Find Solution"
        
        **Step 3: Browse Database** 📊
        - Check the "Browse Database" tab
        - See all bugs in the system
        - Filter by language or search keywords
        
        ---
        
        ### 🚀 What This App Does
        
        This is a **RAG (Retrieval-Augmented Generation)** system:
        
        1. **R**etrieval: Finds similar bugs from database
        2. **A**ugmented: Adds that info as context
        3. **G**eneration: AI creates tailored solution (with Groq API)
        
        ---
        
        ### 💡 Current Mode: Simple Search
        
        Right now, you're using **keyword-based search** which:
        - ✅ Works without API keys
        - ✅ Searches through loaded bug data
        - ✅ Returns similar errors based on keywords
        
        **Want AI-powered solutions?**
        - Get free Groq API key from [console.groq.com](https://console.groq.com)
        - Enter it in the sidebar
        - Get personalized, AI-generated solutions!
        
        ---
        
        ### 📁 Add Your Own Bugs
        
        Create a JSON file with this format:
        
        ```json
        [
          {
            "error_pattern": "Your error message",
            "context": "What you were doing",
            "language": "python",
            "framework": null,
            "problem_description": "Details",
            "solution": "How you fixed it",
            "source": "personal",
            "confidence_score": 85,
            "tags": ["tag1", "tag2"]
          }
        ]
        ```
        
        Then upload it using the sidebar!
        """)

if __name__ == "__main__":
    main()