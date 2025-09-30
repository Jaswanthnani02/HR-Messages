import streamlit as st
import json
import os
import io
import re
from typing import Dict, Any, List
import sqlite3
import hashlib
import uuid
from datetime import datetime
import requests

# Configuration
CONFIG = {
    "DB_PATH": "resume_vectors.db",
    "GROQ_API_URL": "https://api.groq.com/openai/v1/chat/completions",
    "MODEL": "llama-3.1-70b-versatile",
    "MAX_TOKENS": 1500,
    "TEMPERATURE": 0.7,
}

class SimpleResumeParser:
    """Simple resume parser with robust error handling."""
    
    def __init__(self):
        self.keywords = {
            'technical': ['python', 'javascript', 'react', 'sql', 'aws', 'docker', 'java', 'c++', 'html', 'css'],
            'soft': ['leadership', 'communication', 'teamwork', 'problem-solving', 'management']
        }
    
    def parse_resume(self, resume_text: str) -> Dict[str, Any]:
        """Parse resume text into structured data with error handling."""
        try:
            contact_info = self._extract_contact_info(resume_text)
            experience = self._extract_experience(resume_text)
            skills = self._extract_skills(resume_text)
            
            return {
                'contact_info': contact_info,
                'experience': experience,
                'skills': skills,
                'raw_text': resume_text[:5000]  # Limit size
            }
        except Exception as e:
            st.error(f"Error parsing resume: {str(e)}")
            return {
                'contact_info': {'name': '', 'email': '', 'phone': ''},
                'experience': [],
                'skills': {'technical': [], 'soft': []},
                'raw_text': resume_text[:5000]
            }
    
    def _extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information safely."""
        try:
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            phone_pattern = r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
            
            emails = re.findall(email_pattern, text)
            phones = re.findall(phone_pattern, text)
            
            name = ""
            for line in text.split('\n')[:5]:
                line = line.strip()
                if line and len(line.split()) >= 2 and len(line.split()) <= 4:
                    name = line
                    break
            
            return {
                'name': name,
                'email': emails[0] if emails else '',
                'phone': ''.join(phones[0]) if phones else ''
            }
        except Exception:
            return {'name': '', 'email': '', 'phone': ''}
    
    def _extract_experience(self, text: str) -> List[Dict[str, str]]:
        """Extract work experience safely."""
        try:
            experience = []
            lines = [ln.strip() for ln in text.split('\n') if ln.strip()]
            for i, line in enumerate(lines):
                if any(w in line.lower() for w in ['engineer', 'developer', 'manager', 'analyst', 'developer']):
                    title = line
                    company = lines[i+1] if i+1 < len(lines) else ''
                    desc = lines[i+2] if i+2 < len(lines) else ''
                    experience.append({'title': title, 'company': company, 'description': desc})
            return experience[:3]
        except Exception:
            return []
    
    def _extract_skills(self, text: str) -> Dict[str, List[str]]:
        """Extract skills safely."""
        try:
            text_lower = text.lower()
            return {
                'technical': [skill for skill in self.keywords['technical'] if skill in text_lower],
                'soft': [skill for skill in self.keywords['soft'] if skill in text_lower]
            }
        except Exception:
            return {'technical': [], 'soft': []}

class SimpleDBManager:
    """Simple database manager with error handling."""
    
    def __init__(self):
        self.db_path = CONFIG["DB_PATH"]
        self._init_database()
    
    def _init_database(self):
        """Initialize database safely."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS resumes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    email TEXT,
                    resume_data TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()
        except Exception as e:
            st.error(f"Database initialization error: {str(e)}")
    
    def store_resume(self, resume_data: Dict[str, Any]):
        """Store resume data safely."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO resumes (name, email, resume_data)
                VALUES (?, ?, ?)
            ''', (
                resume_data.get('contact_info', {}).get('name', ''),
                resume_data.get('contact_info', {}).get('email', ''),
                json.dumps(resume_data)
            ))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Database storage error: {str(e)}")
            return False
    
    def get_all_resumes(self) -> List[Dict[str, Any]]:
        """Get all resumes safely."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('SELECT id, name, email, resume_data, created_at FROM resumes ORDER BY created_at DESC')
            rows = cursor.fetchall()
            results = []
            for row in rows:
                try:
                    resume_json = json.loads(row[3]) if row[3] else {}
                except:
                    resume_json = {}
                results.append({
                    'id': row[0],
                    'name': row[1],
                    'email': row[2],
                    'resume_data': resume_json,
                    'created_at': row[4]
                })
            conn.close()
            return results
        except Exception as e:
            st.error(f"Database retrieval error: {str(e)}")
            return []

def main():
    st.set_page_config(
        page_title="HR Messages - Simple Version", 
        page_icon="🚀", 
        layout="wide"
    )
    
    st.title("🚀 HR Messages - Simple Version")
    st.markdown("**Upload resumes and generate personalized outreach messages.**")
    
    parser = SimpleResumeParser()
    db_manager = SimpleDBManager()
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Database")
        resumes = db_manager.get_all_resumes()
        st.metric("Total Resumes", len(resumes))
        
        if st.button("🔄 Refresh"):
            st.rerun()
    
    # Main content
    tab1, tab2 = st.tabs(["📄 Upload Resume", "📋 View Resumes"])
    
    with tab1:
        st.header("📄 Upload Resume")
        resume_file = st.file_uploader("Upload resume (TXT or PDF)", type=['txt', 'pdf'])
        
        if resume_file:
            try:
                # Reset file pointer
                resume_file.seek(0)
                resume_text = ""
                
                # Process file
                if resume_file.type == "text/plain":
                    try:
                        resume_text = str(resume_file.read(), "utf-8")
                    except UnicodeDecodeError:
                        resume_file.seek(0)
                        resume_text = str(resume_file.read(), "latin-1")
                elif resume_file.type == "application/pdf":
                    st.info("PDF parsing not available in simple version. Please use TXT files.")
                    return
                else:
                    st.error(f"Unsupported file type: {resume_file.type}")
                    return
                
                # Validate content
                if not resume_text or len(resume_text.strip()) < 10:
                    st.error("File appears to be empty or contains no readable text.")
                    return
                
                # Parse resume
                with st.spinner("Parsing resume..."):
                    parsed_resume = parser.parse_resume(resume_text)
                    
                    # Store in database
                    if db_manager.store_resume(parsed_resume):
                        st.session_state['parsed_resume'] = parsed_resume
                        st.success("✅ Resume parsed and stored!")
                    else:
                        st.error("Failed to store resume in database.")
                        return
                
                # Display results
                col1, col2 = st.columns(2)
                with col1:
                    st.subheader("📋 Contact Information")
                    contact = parsed_resume.get('contact_info', {})
                    st.write(f"**Name:** {contact.get('name', 'Not found')}")
                    st.write(f"**Email:** {contact.get('email', 'Not found')}")
                    st.write(f"**Phone:** {contact.get('phone', 'Not found')}")
                
                with col2:
                    st.subheader("🛠️ Skills")
                    skills = parsed_resume.get('skills', {})
                    technical = skills.get('technical', [])
                    soft = skills.get('soft', [])
                    st.write("**Technical:**", ", ".join(technical) if technical else "None")
                    st.write("**Soft:**", ", ".join(soft) if soft else "None")
                    
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    with tab2:
        st.header("📋 Stored Resumes")
        resumes = db_manager.get_all_resumes()
        
        if resumes:
            for resume in resumes:
                with st.expander(f"Resume: {resume['name'] or 'Unknown'}"):
                    st.write(f"**Email:** {resume['email']}")
                    st.write(f"**Uploaded:** {resume['created_at']}")
                    if resume['resume_data']:
                        skills = resume['resume_data'].get('skills', {})
                        if skills:
                            st.write(f"**Skills:** {', '.join(skills.get('technical', [])[:3])}")
        else:
            st.info("No resumes found. Upload some resumes to get started!")

if __name__ == "__main__":
    main()
