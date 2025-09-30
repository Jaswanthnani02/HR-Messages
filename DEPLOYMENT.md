# 🚀 Deployment Guide

This guide will help you deploy the HR Messages application to various platforms.

## 📋 Prerequisites

- Python 3.12+
- Git
- Docker (for containerized deployment)
- Groq API key (optional)

## 🏠 Local Development

### Quick Start
```bash
# 1. Clone the repository
git clone <your-repo-url>
cd hr-messages

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up environment
cp env.example .env
# Edit .env with your GROQ_API_KEY

# 4. Run the application
python run_app.py
# OR
streamlit run advanced_app.py
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)
```bash
# 1. Set up environment
cp env.example .env
# Edit .env with your configuration

# 2. Build and run
docker-compose up -d

# 3. Access the application
# Open http://localhost:8501 in your browser
```

### Using Docker directly
```bash
# 1. Build the image
docker build -t hr-messages .

# 2. Run the container
docker run -p 8501:8501 -e GROQ_API_KEY=your_key hr-messages
```

## ☁️ Cloud Deployment

### Heroku
1. Create a `Procfile`:
   ```
   web: streamlit run advanced_app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. Deploy:
   ```bash
   git add .
   git commit -m "Deploy to Heroku"
   git push heroku main
   ```

### Railway
1. Connect your GitHub repository
2. Set environment variables in Railway dashboard
3. Deploy automatically

### Streamlit Cloud
1. Push to GitHub
2. Connect to Streamlit Cloud
3. Set environment variables
4. Deploy

## 🔧 Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `GROQ_API_KEY` | Groq API key for enhanced AI features | No | - |
| `DB_PATH` | Database file path | No | `resume_vectors.db` |
| `DEBUG` | Debug mode | No | `False` |

## 📊 Database Management

### Backup Database
```bash
cp resume_vectors.db backup_$(date +%Y%m%d).db
```

### Reset Database
```bash
rm resume_vectors.db
# The app will create a new database on next run
```

## 🔒 Security Considerations

1. **API Keys**: Never commit API keys to version control
2. **Database**: Store database files securely
3. **Environment**: Use environment variables for sensitive data
4. **HTTPS**: Use HTTPS in production

## 🚀 Production Checklist

- [ ] Set up environment variables
- [ ] Configure database persistence
- [ ] Set up monitoring and logging
- [ ] Configure HTTPS
- [ ] Set up backup strategy
- [ ] Test all features
- [ ] Configure error handling

## 🆘 Troubleshooting

### Common Issues

1. **Port already in use**:
   ```bash
   streamlit run advanced_app.py --server.port 8502
   ```

2. **Database locked**:
   - Check if another instance is running
   - Restart the application

3. **Missing dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **API key issues**:
   - Verify the key is correct
   - Check environment variable loading

### Logs and Debugging

Enable debug mode:
```bash
export DEBUG=True
streamlit run advanced_app.py
```

## 📈 Performance Optimization

1. **Database**: Use SQLite with proper indexing
2. **Caching**: Leverage Streamlit's caching features
3. **Memory**: Monitor memory usage with large datasets
4. **API**: Implement rate limiting for external APIs

## 🔄 Updates and Maintenance

1. **Regular Updates**: Keep dependencies updated
2. **Backup**: Regular database backups
3. **Monitoring**: Monitor application performance
4. **Security**: Regular security updates

---

For more help, check the [README.md](README.md) or open an issue on GitHub.
