import streamlit as st
import json
import os
import io
import re
from typing import Dict, Any, List
import sqlite3
import hashlib
import pickle
from functools import lru_cache
import uuid
from datetime import datetime
import requests

# Conditional imports with lazy loading
try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    import chromadb
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMER_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMER_AVAILABLE = False

# Configuration
CONFIG = {
    "DB_PATH": "resume_vectors.db",
    "GROQ_API_URL": "https://api.groq.com/openai/v1/chat/completions",
    "MODEL": "llama-3.1-70b-versatile",
    "MAX_TOKENS": 1500,
    "TEMPERATURE": 0.7,
    "CACHE_TTL": 60 * 60 * 24,  # 24 hours
}

class AdvancedLLMHandler:
    """Handles interactions with the Groq LLM API with robust fallbacks."""
    
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
    
    def generate_response(self, prompt: str, max_tokens: int = CONFIG["MAX_TOKENS"]) -> str:
        """Generate a response using the Groq LLM API."""
        if not self.api_key:
            return self._generate_fallback(prompt)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": CONFIG["MODEL"],
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": CONFIG["TEMPERATURE"]
            }
            response = requests.post(CONFIG["GROQ_API_URL"], headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except Exception as e:
            st.error(f"LLM API error: {str(e)}. Using fallback.")
            return self._generate_fallback(prompt)
    
    def _generate_fallback(self, prompt: str) -> str:
        """Generate fallback responses for specific tasks."""
        prompt_lower = prompt.lower()
        if "extract" in prompt_lower and "resume" in prompt_lower:
            return json.dumps({
                "contact_info": {"name": "", "email": "", "phone": ""},
                "skills": {"technical": [], "soft": []},
                "experience": [],
                "raw_text": ""
            })
        elif "analyze" in prompt_lower and "match" in prompt_lower:
            return json.dumps({
                "match_score": 85,
                "key_alignments": ["Python experience", "Full-stack capabilities"],
                "missing_skills": ["Cloud deployment"],
                "strengths": ["Technical expertise", "Leadership"],
                "recommended_focus": "Emphasize Python and leadership skills",
                "keyword_suggestions": ["Python", "Leadership", "Agile"]
            })
        elif "generate" in prompt_lower and "message" in prompt_lower:
            return self._create_personalized_message(prompt)
        return "Unable to process request in demo mode."
    
    def _create_personalized_message(self, prompt: str) -> str:
        """Create a personalized HR outreach message."""
        company, contact, skills, role = "Your Company", "Hiring Manager", ["Python", "JavaScript"], "Software Engineer"
        for line in prompt.split('\n'):
            if "Company:" in line:
                company = line.split("Company:")[-1].strip()
            elif "Contact:" in line:
                contact = line.split("Contact:")[-1].strip()
            elif "Top Skills:" in line:
                skills = [s.strip() for s in line.split("Top Skills:")[-1].strip().split(',')]
            elif "Recent Role:" in line:
                role = line.split("Recent Role:")[-1].strip()
        
        return f"""Subject: Application for {role} - [Your Name]

Dear {contact},

I am excited to apply for the {role} position at {company}. With expertise in {', '.join(skills[:3])}, I am eager to contribute to your team.

My experience in {skills[0]} and {skills[1]} aligns with your needs. I have delivered scalable solutions and led projects that enhanced performance. {company}'s innovation inspires me, and I am confident my skills will add value.

I am available to discuss how I can contribute to {company}. Thank you for considering my application.

Best regards,
[Your Name]
[Your Email]
[Your Phone]"""

class AdvancedResumeParser:
    """Parses resumes to extract structured data."""
    
    def __init__(self):
        self.keywords = {
            'technical': ['python', 'javascript', 'react', 'sql', 'aws', 'docker'],
            'soft': ['leadership', 'communication', 'teamwork', 'problem-solving']
        }
    
    @st.cache_data(ttl=CONFIG["CACHE_TTL"])
    def parse_resume(_self, resume_text: str) -> Dict[str, Any]:
        """Parse resume text into structured data."""
        contact_info = _self._extract_contact_info(resume_text)
        experience = _self._extract_experience(resume_text)
        skills = _self._extract_skills(resume_text)
        
        return {
            'contact_info': contact_info,
            'experience': experience,
            'skills': skills,
            'raw_text': resume_text[:10000]  # Limit size for storage
        }
    
    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information using regex."""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
        
        emails = re.findall(email_pattern, text)
        phones = re.findall(phone_pattern, text)
        
        name = ""
        for line in text.split('\n')[:5]:
            line = line.strip()
            if line and len(line.split()) >= 2 and len(line.split()) <= 4 and not re.search(r'[@\d\(\)]', line):
                name = line
                break
        
        return {
            'name': name,
            'email': emails[0] if emails else '',
            'phone': ''.join(phones[0]) if phones else ''
        }
    
    def _extract_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience from resume text."""
        experience = []
        lines = [ln.strip() for ln in text.split('\n') if ln.strip()]
        for i, line in enumerate(lines):
            if any(w in line.lower() for w in ['engineer', 'developer', 'manager', 'analyst']):
                title = line
                company = lines[i+1] if i+1 < len(lines) else ''
                desc = lines[i+2] if i+2 < len(lines) else ''
                experience.append({'title': title, 'company': company, 'description': desc})
        return experience[:3]
    
    def _extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract technical and soft skills."""
        text_lower = text.lower()
        return {
            'technical': [skill for skill in self.keywords['technical'] if skill in text_lower],
            'soft': [skill for skill in self.keywords['soft'] if skill in text_lower]
        }

class VectorDBManager:
    """Manages resume storage and retrieval with SQLite and optional ChromaDB."""
    
    def __init__(self):
        self.db_path = CONFIG["DB_PATH"]
        self._init_database()
        self.chroma_client = None
        self.chroma_collection = None
        self.embed_model = None
        if CHROMA_AVAILABLE and SENTENCE_TRANSFORMER_AVAILABLE:
            self._init_resources()
    
    @st.cache_resource
    def _load_resources(_self):
        """Load optional resources (ChromaDB and SentenceTransformer)."""
        client, collection = None, None
        embed_model = None
        if CHROMA_AVAILABLE:
            client = chromadb.Client()
            try:
                collection = client.get_collection(name='resumes')
            except:
                collection = client.create_collection(name='resumes')
        if SENTENCE_TRANSFORMER_AVAILABLE:
            embed_model = SentenceTransformer('all-MiniLM-L6-v2')
        return client, collection, embed_model
    
    def _init_resources(self):
        """Initialize ChromaDB and embedding model."""
        self.chroma_client, self.chroma_collection, self.embed_model = self._load_resources()
    
    def _init_database(self):
        """Initialize SQLite database with indexing."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                email TEXT,
                resume_data TEXT,
                skills TEXT,
                experience TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_resume_data ON resumes (resume_data)')
        conn.commit()
        conn.close()
    
    def store_resume(self, resume_data: Dict[str, Any]):
        """Store resume data in SQLite and optionally ChromaDB."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO resumes (name, email, resume_data, skills, experience)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            resume_data['contact_info'].get('name', ''),
            resume_data['contact_info'].get('email', ''),
            json.dumps(resume_data),
            json.dumps(resume_data.get('skills', {})),
            json.dumps(resume_data.get('experience', []))
        ))
        row_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        if self.chroma_collection and self.embed_model:
            try:
                doc_id = str(uuid.uuid4())
                raw_text = resume_data.get('raw_text', '')
                embedding = self.embed_model.encode(raw_text).tolist()
                self.chroma_collection.add(
                    ids=[doc_id],
                    documents=[raw_text],
                    metadatas=[{
                        'sqlite_id': row_id,
                        'name': resume_data['contact_info'].get('name', ''),
                        'email': resume_data['contact_info'].get('email', '')
                    }],
                    embeddings=[embedding]
                )
            except Exception as e:
                st.warning(f"ChromaDB storage failed: {str(e)}")

    def get_all_resumes(self) -> List[Dict[str, Any]]:
        """Retrieve all stored resumes from SQLite."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, email, resume_data, skills, experience, created_at FROM resumes ORDER BY created_at DESC')
        rows = cursor.fetchall()
        results = []
        for row in rows:
            try:
                resume_json = json.loads(row[3]) if row[3] else {}
            except Exception:
                resume_json = {}
            results.append({
                'id': row[0],
                'name': row[1],
                'email': row[2],
                'resume_data': resume_json,
                'skills': json.loads(row[4]) if row[4] else {},
                'experience': json.loads(row[5]) if row[5] else [],
                'created_at': row[6]
            })
        conn.close()
        return results
    
    def semantic_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform semantic search with ChromaDB or fallback to SQLite keyword search."""
        if self.chroma_collection and self.embed_model:
            try:
                q_emb = self.embed_model.encode(query).tolist()
                query_res = self.chroma_collection.query(query_embeddings=[q_emb], n_results=top_k)
                return [{
                    'doc_id': doc_id,
                    'sqlite_id': meta.get('sqlite_id'),
                    'name': meta.get('name'),
                    'email': meta.get('email'),
                    'snippet': doc[:400],
                    'score': dist
                } for doc_id, meta, doc, dist in zip(
                    query_res.get('ids', [[]])[0],
                    query_res.get('metadatas', [[]])[0],
                    query_res.get('documents', [[]])[0],
                    query_res.get('distances', [[]])[0]
                )]
            except Exception:
                st.warning("Semantic search failed. Falling back to keyword search.")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        pattern = f"%{query}%"
        cursor.execute('SELECT id, name, email, resume_data FROM resumes WHERE resume_data LIKE ? ORDER BY created_at DESC LIMIT ?', (pattern, top_k))
        rows = cursor.fetchall()
        results = [{
            'doc_id': None,
            'sqlite_id': row[0],
            'name': row[1],
            'email': row[2],
            'snippet': json.loads(row[3]).get('raw_text', '')[:400],
            'score': None
        } for row in rows]
        conn.close()
        return results

class KeywordSuggestionEngine:
    """Generates keyword suggestions for job applications."""
    
    def __init__(self):
        self.industry_keywords = {
            'tech': ['innovation', 'scalable', 'agile', 'cloud', 'devops'],
            'finance': ['compliance', 'risk management', 'analytics'],
            'healthcare': ['patient care', 'clinical', 'pharmaceutical'],
            'ecommerce': ['customer experience', 'retail', 'supply chain']
        }
    
    def suggest_keywords(self, job_description: str, resume_skills: List[str]) -> List[str]:
        """Suggest keywords based on job description and resume skills."""
        job_lower = job_description.lower()
        suggestions = []
        for industry, keywords in self.industry_keywords.items():
            if any(keyword in job_lower for keyword in keywords):
                suggestions.extend(keywords)
        
        skill_keywords = {
            'python': ['data analysis', 'machine learning', 'backend development'],
            'javascript': ['frontend development', 'web applications', 'react'],
            'sql': ['database management', 'analytics']
        }
        for skill in resume_skills:
            if skill.lower() in skill_keywords:
                suggestions.extend(skill_keywords[skill.lower()])
        
        return list(set(suggestions))[:10]

def main():
    st.set_page_config(
        page_title="Advanced HR Outreach Generator", 
        page_icon="🚀", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for better styling
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #c3e6cb;
    }
    .warning-message {
        background: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        border: 1px solid #ffeaa7;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="main-header">
        <h1>🚀 Advanced HR Outreach Generator</h1>
        <p>Upload resumes, analyze job matches, and generate personalized outreach messages with AI</p>
    </div>
    """, unsafe_allow_html=True)
    
    parser = AdvancedResumeParser()
    llm = AdvancedLLMHandler()
    db_manager = VectorDBManager()
    keyword_engine = KeywordSuggestionEngine()
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # API Key Configuration
        api_key = st.text_input("GROQ API Key", type="password", help="Enter your Groq API key for enhanced AI features")
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
            st.markdown('<div class="success-message">✅ API key configured successfully</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-message">ℹ️ Running in demo mode - some features may be limited</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # Database Statistics
        st.header("📊 Database Statistics")
        try:
            resumes = db_manager.get_all_resumes()
            st.metric("Total Resumes", len(resumes))
            if resumes:
                recent_count = len([r for r in resumes if r['created_at'] and '2024' in r['created_at']])
                st.metric("Recent Uploads", recent_count)
                
                if st.button("🔄 Refresh Database"):
                    st.rerun()
        except Exception as e:
            st.error(f"Database error: {str(e)}")
        
        st.divider()
        
        # Quick Actions
        st.header("🚀 Quick Actions")
        if st.button("📋 View All Resumes"):
            resumes = db_manager.get_all_resumes()
            if resumes:
                for i, resume in enumerate(resumes[:5]):
                    with st.expander(f"Resume {i+1}: {resume['name'] or 'Unknown'}"):
                        st.write(f"**Email:** {resume['email']}")
                        st.write(f"**Uploaded:** {resume['created_at']}")
                        if resume['skills']:
                            st.write(f"**Skills:** {', '.join(resume['skills'].get('technical', [])[:3])}")
            else:
                st.info("No resumes found. Upload some resumes to get started!")
        
        if st.button("🗑️ Clear Database"):
            if st.button("⚠️ Confirm Clear", key="confirm_clear"):
                try:
                    conn = sqlite3.connect(CONFIG["DB_PATH"])
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM resumes")
                    conn.commit()
                    conn.close()
                    st.success("Database cleared successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error clearing database: {str(e)}")
    
    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Upload Resume", "🔍 Analyze Match", "💬 Generate Message", "🔎 Search Resumes"])
    
    with tab1:
        st.header("📄 Upload & Parse Resume")
        resume_file = st.file_uploader("Upload resume (TXT or PDF)", type=['txt', 'pdf'])
        
        if resume_file:
            try:
                resume_text = ""
                if resume_file.type == "text/plain":
                    resume_text = str(resume_file.read(), "utf-8")
                elif resume_file.type == "application/pdf" and PDF_AVAILABLE:
                    with pdfplumber.open(io.BytesIO(resume_file.read())) as pdf:
                        resume_text = "\n".join(page.extract_text() or "" for page in pdf.pages)
                else:
                    st.error("PDF parsing requires pdfplumber.")
                    return
                
                with st.spinner("Parsing resume..."):
                    parsed_resume = parser.parse_resume(resume_text)
                    db_manager.store_resume(parsed_resume)
                    st.session_state['parsed_resume'] = parsed_resume
                
                st.success("✅ Resume parsed and stored!")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("📋 Contact Information")
                    contact = parsed_resume['contact_info']
                    st.write(f"**Name:** {contact.get('name', 'Not found')}")
                    st.write(f"**Email:** {contact.get('email', 'Not found')}")
                    st.write(f"**Phone:** {contact.get('phone', 'Not found')}")
                    
                    st.subheader("🛠️ Skills")
                    st.write("**Technical:**", ", ".join(parsed_resume['skills']['technical'] or ["None"]))
                    st.write("**Soft:**", ", ".join(parsed_resume['skills']['soft'] or ["None"]))
                
                with col2:
                    st.subheader("💼 Experience")
                    for exp in parsed_resume['experience'][:3]:
                        st.write(f"**{exp['title']}** at {exp['company']}")
                        st.write(exp['description'])
                        st.write("---")
            except Exception as e:
                st.error(f"Error processing resume: {str(e)}")
    
    with tab2:
        st.header("🔍 Job Match Analysis")
        if 'parsed_resume' not in st.session_state:
            st.warning("Please upload a resume first.")
        else:
            job_description = st.text_area("Job Description", height=200)
            company_name = st.text_input("Company Name")
            hr_name = st.text_input("HR Contact Name (optional)")
            
            if st.button("🔍 Analyze Match"):
                if not job_description:
                    st.error("Please provide a job description.")
                else:
                    with st.spinner("Analyzing..."):
                        analysis_prompt = f"""
                        Analyze resume-job match:
                        Resume: {json.dumps(st.session_state['parsed_resume'], indent=2)}
                        Job: {job_description}
                        Return JSON with match_score, key_alignments, missing_skills, strengths, recommended_focus, keyword_suggestions.
                        """
                        analysis = llm.generate_response(analysis_prompt)
                        try:
                            analysis_data = json.loads(analysis)
                        except:
                            analysis_data = {
                                "match_score": 75,
                                "key_alignments": ["Technical skills"],
                                "missing_skills": ["Cloud experience"],
                                "strengths": ["Strong background"],
                                "recommended_focus": "Highlight technical skills",
                                "keyword_suggestions": ["Python", "Leadership"]
                            }
                        
                        st.session_state['analysis'] = analysis_data
                        st.session_state['company_name'] = company_name
                        st.session_state['hr_name'] = hr_name
                        st.session_state['job_description'] = job_description
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Match Score", f"{analysis_data['match_score']}%")
                        with col2:
                            st.metric("Key Alignments", len(analysis_data['key_alignments']))
                        with col3:
                            st.metric("Strengths", len(analysis_data['strengths']))
                        
                        st.subheader("📊 Analysis Details")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write("**✅ Key Alignments:**", ", ".join(analysis_data['key_alignments']))
                            st.write("**💪 Strengths:**", ", ".join(analysis_data['strengths']))
                        with col2:
                            st.write("**⚠️ Missing Skills:**", ", ".join(analysis_data['missing_skills']))
                            st.write("**🎯 Recommended Focus:**", analysis_data['recommended_focus'])
                        
                        st.subheader("🔑 Keyword Suggestions")
                        keywords = keyword_engine.suggest_keywords(job_description, st.session_state['parsed_resume']['skills']['technical'])
                        st.write(", ".join(keywords))
    
    with tab3:
        st.header("💬 Generate Outreach Message")
        if 'analysis' not in st.session_state:
            st.warning("Please analyze a job match first.")
        else:
            col1, col2 = st.columns(2)
            with col1:
                message_tone = st.selectbox("Tone", ["Professional", "Enthusiastic", "Confident", "Friendly"])
                message_length = st.selectbox("Length", ["Short (150-200 words)", "Medium (200-300 words)", "Long (300-400 words)"])
            with col2:
                include_portfolio = st.checkbox("Include portfolio", value=True)
                include_availability = st.checkbox("Include availability", value=True)
            
            custom_keywords = st.text_input("Custom Keywords (comma-separated)")
            
            if st.button("🚀 Generate Message"):
                with st.spinner("Generating message..."):
                    resume_data = st.session_state['parsed_resume']
                    analysis_data = st.session_state['analysis']
                    top_skills = resume_data['skills']['technical'][:3]
                    recent_job = resume_data['experience'][0] if resume_data['experience'] else {}
                    company_name = st.session_state.get('company_name', 'Your Company')
                    hr_name = st.session_state.get('hr_name', 'Hiring Manager')
                    
                    message_prompt = f"""
                    Create a {message_tone.lower()} HR email for:
                    - Candidate: {resume_data['contact_info']['name']}
                    - Skills: {', '.join(top_skills)}
                    - Role: {recent_job.get('title', 'Software Engineer')}
                    - Company: {company_name}
                    - Contact: {hr_name}
                    - Length: {message_length}
                    Include portfolio: {include_portfolio}
                    Include availability: {include_availability}
                    Keywords: {custom_keywords or ', '.join(analysis_data['keyword_suggestions'][:3])}
                    """
                    message = llm.generate_response(message_prompt)
                    
                    st.subheader("📧 Generated Message")
                    edited_message = st.text_area("Edit Message", value=message, height=400)
                    st.download_button("📥 Download as TXT", edited_message, f"outreach_{company_name}.txt")
    
    with tab4:
        st.header("🔎 Search Stored Resumes")
        search_query = st.text_input("Search Query (skills, role, company)")
        top_k = st.slider("Top Results", 1, 10, 5)
        
        if st.button("Search"):
            if search_query:
                with st.spinner("Searching..."):
                    results = db_manager.semantic_search(search_query, top_k)
                    if results:
                        for r in results:
                            st.subheader(r['name'] or f"Resume {r['sqlite_id']}")
                            st.write(f"**Email:** {r['email']}")
                            st.write(f"**Snippet:** {r['snippet']}")
                            if r['score']:
                                st.write(f"**Score:** {r['score']}")
                            st.write("---")
                    else:
                        st.info("No results found.")
            else:
                st.error("Please enter a search query.")

if __name__ == "__main__":
    main()