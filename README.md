# 🚀 HR Messages - Advanced HR Outreach Generator

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.37+-red.svg)](https://streamlit.io)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An intelligent Streamlit application that helps HR professionals and job seekers by analyzing resumes, matching them with job descriptions, and generating personalized outreach messages using AI.

## ✨ Features

### 📄 **Resume Processing**
- **Smart Parsing**: Upload and parse PDF/TXT resumes with intelligent data extraction
- **Contact Extraction**: Automatically extracts name, email, phone from resumes
- **Skills Detection**: Identifies technical and soft skills (30+ technical, 15+ soft skills)
- **Experience Analysis**: Extracts work experience, job titles, and company information

### 🔍 **Job Match Analysis**
- **AI-Powered Matching**: Analyze how well a resume matches a job description
- **Match Scoring**: Get detailed match scores and alignment analysis
- **Keyword Suggestions**: Receive intelligent keyword recommendations
- **Strengths & Weaknesses**: Identify candidate strengths and areas for improvement

### 💬 **Personalized Message Generation**
- **Custom Messages**: Generate personalized HR outreach messages
- **Multiple Tones**: Professional, Enthusiastic, Confident, Friendly
- **Length Options**: Short, Medium, Long message formats
- **Real Data Integration**: Uses actual resume data (name, email, phone)
- **Download Options**: Export messages as TXT or DOC files

### 🔎 **Advanced Search**
- **Semantic Search**: AI-powered resume search using vector embeddings
- **Keyword Search**: Fallback keyword-based search
- **Database Management**: View, manage, and search stored resumes
- **Duplicate Detection**: Prevents duplicate resume uploads

## 🏗️ **Architecture**

### **Production-Ready Design**
- **Modular Architecture**: Clean separation of concerns
- **Database Management**: SQLite with connection pooling
- **Error Handling**: Comprehensive error management and logging
- **Security**: File validation, input sanitization, SQL injection prevention
- **Performance**: Optimized queries, caching, memory management

### **Components**
- **DatabaseManager**: Production-ready database operations
- **ResumeParser**: Enhanced resume parsing with validation
- **LLMHandler**: AI integration with fallback responses
- **Security**: File validation and input sanitization

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.8+
- Streamlit
- Optional: Groq API key for enhanced AI features

### **Installation**

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd hr-messages
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   streamlit run app_improved.py
   ```

5. **Access the application**
   ```
   http://localhost:8501
   ```

## 🔧 **Configuration**

### **Environment Variables**
Create a `.env` file with:
```bash
GROQ_API_KEY=your_groq_api_key_here  # Optional, for enhanced AI
DB_PATH=resume_vectors.db            # Database file path
LOG_LEVEL=INFO                       # Logging level
MAX_FILE_SIZE=10485760              # 10MB file size limit
```

### **Optional Dependencies**
The app works with or without these optional dependencies:
- **ChromaDB**: For advanced semantic search
- **SentenceTransformers**: For embedding generation
- **pdfplumber**: For PDF resume parsing

## 📱 **Usage**

### **1. Upload Resume**
- Upload PDF or TXT resume files
- Automatic parsing extracts contact info, skills, and experience
- Data is stored in the local database with duplicate detection

### **2. Analyze Job Match**
- Paste job description
- Enter company and HR contact details
- Get match score and detailed analysis
- Receive keyword suggestions

### **3. Generate Custom Messages**
- Choose message tone and length
- Customize with additional keywords
- Generate personalized messages using your actual resume data
- Download as TXT or DOC files

### **4. Search Resumes**
- Use semantic search to find relevant candidates
- Search by skills, roles, or company names
- View detailed candidate information

## 🛡️ **Security Features**

- **File Upload Protection**: Size limits, type validation, content scanning
- **SQL Injection Prevention**: Parameterized queries throughout
- **Input Sanitization**: All user inputs properly validated
- **Error Information Protection**: No internal details exposed
- **Duplicate Detection**: SHA-256 hash-based duplicate prevention

## 📊 **Database Schema**

```sql
CREATE TABLE resumes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    resume_data TEXT NOT NULL,
    skills TEXT,
    experience TEXT,
    file_hash TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🚀 **Deployment**

### **Local Development**
```bash
streamlit run app_improved.py
```

### **Docker Deployment**
```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.production.yml up -d
```

### **Production Deployment**
```bash
# Use the deployment script
python deploy_improved.py
```

## 📈 **Performance Features**

- **Database Optimization**: Proper indexing and query optimization
- **Memory Management**: File size limits and efficient processing
- **Caching**: Intelligent caching with Streamlit
- **Connection Pooling**: Efficient database connections
- **Error Recovery**: Graceful degradation when components fail

## 🔍 **Monitoring & Debugging**

### **Health Checks**
- Database connectivity and performance
- File system operations
- API connectivity
- Resource usage monitoring

### **Logging**
- Comprehensive logging system
- Different log levels (INFO, WARNING, ERROR)
- File and console logging
- Debug information for troubleshooting

## 📋 **API Integration**

### **Groq LLM Integration**
- **Enhanced AI Features**: When API key is provided
- **Fallback Responses**: Demo mode when API unavailable
- **Error Handling**: Robust API error management
- **Rate Limiting**: Proper API usage management

## 🧪 **Testing**

### **Test Files**
- `test_resume.txt`: Sample resume for testing
- `monitor.py`: Health check and maintenance script

### **Manual Testing**
1. Upload sample resume
2. Test job match analysis
3. Generate custom messages
4. Test search functionality
5. Verify database operations

## 📚 **Documentation**

- **SENIOR_CODE_REVIEW.md**: Comprehensive code review analysis
- **FINAL_SUMMARY.md**: Complete improvement summary
- **DEPLOYMENT.md**: Detailed deployment guide
- **OPTIMIZATION_SUMMARY.md**: Performance optimization details

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 **License**

This project is open source and available under the [MIT License](LICENSE).

## 🆘 **Support**

### **Common Issues**
1. **Port already in use**: Use `--server.port 8502`
2. **Missing dependencies**: Run `pip install -r requirements.txt`
3. **Database locked**: Restart the application
4. **API key issues**: Check environment variable configuration

### **Getting Help**
- Check the documentation files
- Review error logs
- Open an issue on GitHub
- Check the debug features in the application

## 🎯 **Roadmap**

- [ ] **Multi-language Support**: Resume parsing in multiple languages
- [ ] **Advanced Analytics**: Detailed matching statistics
- [ ] **Integration APIs**: Connect with job boards and ATS systems
- [ ] **Machine Learning**: Enhanced matching algorithms
- [ ] **Cloud Deployment**: AWS, Azure, GCP deployment options

---

**Made with ❤️ for HR professionals and job seekers**

*This application is production-ready with enterprise-grade security, performance, and reliability features.*