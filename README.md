# 🚀 Advanced HR Outreach Generator

An intelligent Streamlit application that helps HR professionals and job seekers by analyzing resumes, matching them with job descriptions, and generating personalized outreach messages.

## ✨ Features

- **📄 Resume Parsing**: Upload and parse PDF/TXT resumes with intelligent data extraction
- **🔍 Job Match Analysis**: Analyze how well a resume matches a job description
- **💬 Personalized Messages**: Generate customized HR outreach messages
- **🔎 Semantic Search**: Search through stored resumes using AI-powered semantic search
- **🗄️ Vector Database**: Store and retrieve resumes with ChromaDB and SQLite
- **🎯 Keyword Suggestions**: Get intelligent keyword recommendations for job applications

## 🛠️ Installation

### Prerequisites
- Python 3.12+
- Groq API key (optional, for enhanced AI features)

### Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd hr-messages
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GROQ_API_KEY
   ```

4. **Run the application**
   ```bash
   streamlit run advanced_app.py
   ```

## 🔧 Configuration

### Environment Variables
Create a `.env` file with:
```
GROQ_API_KEY=your_groq_api_key_here
```

### Optional Dependencies
The app works with or without these optional dependencies:
- **ChromaDB**: For advanced semantic search
- **SentenceTransformers**: For embedding generation
- **pdfplumber**: For PDF resume parsing

## 📱 Usage

### 1. Upload Resume
- Upload PDF or TXT resume files
- Automatic parsing extracts contact info, skills, and experience
- Data is stored in the local database

### 2. Analyze Job Match
- Paste job description
- Enter company and HR contact details
- Get match score and detailed analysis
- Receive keyword suggestions

### 3. Generate Outreach Message
- Choose message tone and length
- Customize with additional keywords
- Generate and download personalized messages

### 4. Search Resumes
- Use semantic search to find relevant candidates
- Search by skills, roles, or company names
- View detailed candidate information

## 🏗️ Architecture

- **Frontend**: Streamlit for interactive UI
- **Backend**: Python with modular class structure
- **Database**: SQLite for primary storage, ChromaDB for vector search
- **AI**: Groq API integration with fallback responses
- **Parsing**: Regex-based extraction with PDF support

## 🚀 Deployment

### Local Development
```bash
streamlit run advanced_app.py
```

### Production Deployment
1. Set up environment variables
2. Install dependencies
3. Run with production settings
4. Consider using Docker for containerization

## 📊 Database Schema

The application uses SQLite with the following schema:
- `resumes` table: Stores parsed resume data
- `chromadb` collection: Vector embeddings for semantic search

## 🔒 Security

- API keys are stored as environment variables
- Resume data is stored locally
- No external data transmission without explicit user action

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review the code comments
3. Open an issue on GitHub

---

**Made with ❤️ for HR professionals and job seekers**
