# Smart Customer Service Chatbot

A bilingual (English/Chinese) AI-powered customer service chatbot built with FastAPI, scikit-learn, and modern web technologies. Demonstrates intent classification, entity recognition, and multi-turn conversation capabilities for e-commerce customer support.

## 🚀 Live Demo

- **Frontend**: [https://regal-custard-47715d.netlify.app](https://regal-custard-47715d.netlify.app)
- **API Documentation**: [https://smart-chatbot-production.up.railway.app/docs](https://smart-chatbot-production.up.railway.app/docs)
- **Backend API**: [https://smart-chatbot-production.up.railway.app](https://smart-chatbot-production.up.railway.app)

## 🎯 Features

### Core Capabilities
- **Bilingual Support**: Automatic language detection (English/Chinese)
- **Intent Classification**: Understands customer intents (order status, cancellation, product inquiry, etc.)
- **Entity Extraction**: Identifies key information (order numbers, emails, phone numbers, dates)
- **Context Management**: Maintains conversation history and session state
- **Real-time Processing**: Instant responses via REST API

### Technical Features
- **Hybrid NLP Approach**: Machine learning + rule-based classification
- **RESTful API**: FastAPI with automatic documentation
- **Production-Ready**: Deployed with proper CORS, error handling, and logging
- **Analytics Ready**: Conversation tracking and performance monitoring
- **Scalable Architecture**: Microservices-ready design

## 🏗️ Architecture

```
Frontend (HTML/JS)     ←→     FastAPI Backend     ←→     NLP Engine
     ↓                              ↓                        ↓
  Netlify CDN              Railway.app Hosting         scikit-learn
                                    ↓                        ↓
                           Conversation Manager        Intent Classifier
```

## 🛠️ Technology Stack

**Backend:**
- FastAPI (Python web framework)
- scikit-learn (Machine learning)
- Uvicorn (ASGI server)

**Frontend:**
- Vanilla JavaScript
- HTML5/CSS3

**Deployment:**
- Railway.app (Backend hosting)
- Netlify (Frontend CDN)
- GitHub (Source control)

**NLP Pipeline:**
- TF-IDF Vectorization
- Naive Bayes Classification
- Regular Expressions (Entity extraction)
- Language detection algorithms

## 📊 Performance Metrics

### Current Status
- **Intent Classification**: Tested on basic scenarios with 5 intent categories
- **Language Detection**: Simple Chinese character detection (no formal accuracy testing yet)
- **Response Time**: Fast local processing (formal benchmarking pending)
- **Entity Extraction**: Successfully extracts order numbers, emails, phone numbers from test cases
- **Supported Languages**: English, Chinese (Simplified)

*Comprehensive performance testing and benchmarking planned for next development phase.*

## 🚦 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/mt-robotics/smart-chatbot.git
   cd smart-chatbot
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # venv\Scripts\activate   # Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment configuration**
   ```bash
   # Copy the example environment file for your development environment
   cp .env.example .env              # For local development

   # For deploying to production/staging (optional)
   cp .env.example .env.production   # For production setup
   cp .env.example .env.staging      # For staging setup
   ```
   Edit the copied files to add your specific configurations:
   - For local development, you can use the defaults in `.env`
   - For production, update `CORS_ORIGINS` to your frontend domain
   - For production, update `BACKEND_API_URL` to your hosted API URL
   - Set `API_DEBUG` and `ENABLE_DEBUG_INFO` to false in production

5. **Generate frontend configuration**
   ```bash
   python scripts/build-frontend-config.py
   ```

6. **Run the backend**
   ```bash
   python main.py
   ```

7. **Open frontend**
   ```bash
   cd frontend
   python -m http.server 3000
   # Open http://localhost:3000
   ```

## 📱 API Usage

### Chat Endpoint
```bash
curl -X POST "https://smart-chatbot-production.up.railway.app/chat" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "I want to check my order status",
       "session_id": "optional-session-id"
     }'
```

### Response Format
```json
{
  "response": "I'll help you check your order status. Please provide your order number.",
  "session_id": "b25ca0fc-86f2-4240-8de9-fa9c2c59599d",
  "intent": "order_status",
  "confidence": 0.89,
  "entities": {
    "order_number": "12345"
  }
}
```

## 🧠 NLP Capabilities

### Supported Intents
- **order_status**: Check order progress
- **cancel_order**: Cancel existing orders
- **product_inquiry**: Product information requests
- **greeting**: Welcome messages
- **goodbye**: Farewell messages

### Entity Extraction
- Order numbers (4-6 digits)
- Email addresses
- Phone numbers
- Monetary amounts
- Dates and times
- Product names

### Bilingual Examples
**English:**
- "Where is my order #12345?"
- "I want to cancel my purchase"
- "Tell me about your products"

**Chinese:**
- "我的订单在哪里？"
- "我要取消订单"
- "介绍一下你们的产品"

## 🔧 Configuration

### Environment Setup
This project uses environment-specific configuration files:
- `.env.example` - Template with documentation (committed to git)
- `.env` - Local development settings (not committed)
- `.env.production` - Production settings (not committed)
- `.env.staging` - Staging settings (not committed)

The `.env.example` file serves as a template and documentation for all available configuration options. When setting up the project:
1. Copy `.env.example` to create your environment-specific files
2. Update the values in each file according to your needs
3. Never commit actual `.env` files to version control

### Environment Variables
```bash
# API Configuration
API_HOST=127.0.0.1            # Use 0.0.0.0 for production
API_PORT=8000                 # Or $PORT for cloud hosting
API_DEBUG=true               # Set to false in production

# CORS Settings (Critical for security)
CORS_ORIGINS=http://localhost:3000  # Comma-separated list of allowed domains

# Logging (Adjust per environment)
LOG_LEVEL=DEBUG              # Use INFO or WARNING in production
ENABLE_REQUEST_LOGGING=true  # Optional for development debugging
```

### Training Data
Located in `app/data/training_data.py` - easily expandable for new intents and languages.

## 📈 Future Enhancements

- **Advanced NLP**: Transformer models (BERT/GPT)
- **Voice Support**: Speech-to-text integration
- **Analytics Dashboard**: Real-time performance monitoring
- **Multi-language**: Support for additional languages
- **Integration**: CRM and helpdesk system connections

## 📚 Additional Documentation

- [NLP Concepts Guide](docs/NLP_CONCEPTS.md) - Deep dive into TF-IDF and Naive Bayes
- [Development Workflow](docs/DEVELOPMENT_WORKFLOW.md) - Professional Git and deployment practices
- [Regular Expressions Guide](docs/REGEX_GUIDE.md) - Comprehensive regex documentation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Developer

**Monireach Tang**
- LinkedIn: [linkedin.com/in/monireach-tang](https://www.linkedin.com/in/monireach-tang/)
- Email: monireach.tang@gmail.com
- Website: [monireach.com](https://www.monireach.com)

---

*Built as a demonstration of full-stack development, NLP implementation, and production deployment capabilities.*