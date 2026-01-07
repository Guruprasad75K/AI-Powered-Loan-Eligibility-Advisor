# 🏦 AI-Powered Loan Eligibility Advisor

An intelligent loan approval system powered by machine learning, featuring real-time predictions, AI explainability with LIME, professional visual reports, and a financial advisor chatbot.

---

## 📌 Project Overview

This project implements a comprehensive loan approval system that analyzes 12+ factors to provide instant, accurate loan eligibility decisions. The system integrates XGBoost machine learning for predictions, LIME for explainable AI, and Llama 3.2 for financial advisory chatbot functionality.

The application provides:
- **Real-time loan approval predictions** with confidence scores
- **AI-powered explanations** showing which factors influenced the decision
- **Professional visual reports** in PNG format with detailed analytics
- **Interactive financial chatbot** for personalized advice

---

## 🧠 Core Functionalities

- **Loan Prediction Engine**: XGBoost model with 98% accuracy analyzing 12 key factors
- **Explainable AI**: LIME-based feature importance visualization
- **Risk Assessment**: Automatic identification of risk factors (credit score, DTI, defaults)
- **Visual Report Generation**: Professional A4 reports with circular progress rings and metrics
- **Financial Advisor Chatbot**: AI-powered assistant for financial queries
- **Interactive Web Interface**: Modern, responsive UI with smooth animations

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Hugging Face API Token ([Get free token here](https://huggingface.co/settings/tokens))

### Installation

```bash
# Clone the repository
git clone https://github.com/Guruprasad75K/AI-Powered-Loan-Eligibility-Advisor.git
cd AI-Powered-Loan-Eligibility-Advisor

# Install dependencies
pip install -r requirements.txt
```

### ⚠️ Required: Add API Key

Create a `.env` file in the project root directory:

```env
HUGGINGFACE_API_TOKEN=your_token_here
```

**How to get your API token:**
1. Visit https://huggingface.co/settings/tokens
2. Click "New token"
3. Select "Read" permission
4. Copy the token (starts with `hf_`)
5. Paste it in the `.env` file

### Run the Application

```bash
python main.py
```

Then open your browser and navigate to:
```
http://localhost:5000
```

---

## 🏗️ System Architecture

```
User Input (Web Form)
   │
   ▼
Flask API (app.py)
   │
   ├── XGBoost Model (Predictions)
   ├── LIME Explainer (AI Explanations)
   ├── Report Generator (Visual Reports)
   └── Chatbot (Financial Advice)
   │
   ▼
Output (Approval Decision + Report + Chat)
```

---

## 📊 Model Information

**Algorithm**: XGBoost (Gradient Boosting)  
**Features**: 12 input parameters  
**Accuracy**: ~98% on test data  
**Threshold**: 0.5 (probability ≥ 0.5 = approved)

### Input Features

| Feature | Type | Description |
|---------|------|-------------|
| person_age | Numeric | Applicant's age (18-100) |
| person_income | Numeric | Annual income |
| person_emp_exp | Numeric | Employment experience (years) |
| loan_amnt | Numeric | Requested loan amount |
| credit_score | Numeric | Credit score (300-850) |
| cb_person_cred_hist_length | Numeric | Credit history length (years) |
| person_gender | Categorical | Gender (male/female) |
| person_education | Categorical | Education level (5 categories) |
| person_home_ownership | Categorical | Home ownership status (4 types) |
| loan_intent | Categorical | Loan purpose (6 categories) |
| previous_loan_defaults_on_file | Categorical | Previous defaults (Yes/No) |

### Risk Factors Detected

- Low credit score (< 600)
- Previous loan defaults on file
- High debt-to-income ratio (> 40%)
- No employment experience
- Short credit history (< 2 years)

---

## 🖥️ System Outputs

**Web Interface**:
- Real-time loan approval decision
- Confidence score with visual indicators
- Risk factors list
- Confetti animation on approval

**Visual Report (PNG)**:
- Circular approval score ring
- Positive vs negative factors (LIME analysis)
- Key financial metrics visualization
- Personalized improvement recommendations

**Financial Chatbot**:
- Finance-focused conversational AI
- Answers questions about loans, budgeting, credit
- Maintains conversation context
- Provides personalized advice

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Main application page |
| `/api/predict` | POST | Submit loan application |
| `/api/chat` | POST | Chat with financial advisor |
| `/api/download-report` | GET | Download visual report |
| `/health` | GET | System health check |

---

## 🛠️ Technologies Used

**Backend**: Flask, Python 3.8+  
**Machine Learning**: XGBoost, scikit-learn  
**Explainable AI**: LIME  
**Chatbot**: Llama 3.2 (via Hugging Face API)  
**Visualization**: Matplotlib  
**Frontend**: HTML5, CSS3, JavaScript  
**Data Processing**: pandas, numpy  

---

## 📂 Repository Structure

```
AI-Powered-Loan-Eligibility-Advisor/
├── main.py                     # Entry point - RUN THIS
├── app.py                      # Flask application
├── loanPredictor.py            # ML prediction module
├── chatbot.py                  # Financial advisor chatbot
├── reportGenerator.py          # LIME + report generation
├── requirements.txt            # Python dependencies
├── .env                        # API credentials (CREATE THIS)
├── models/
│   ├── loan_modelA1.ubj        # XGBoost model
│   └── loan_encoder.joblib     # OneHotEncoder
├── templates/
│   └── index.html              # Main page
└── static/
    ├── css/
    │   └── style.css
    └── js/
        └── script.js
```

---


## 🔮 Future Enhancements

- User authentication system
- Loan application history tracking
- Email notifications for decisions
- Admin dashboard with analytics
- Multiple ML models (ensemble approach)
- Mobile application
- Multi-language support
- Integration with credit bureaus

---

## 🏁 Project Status

✔ Production-ready web application  
✔ Real-time ML predictions  
✔ AI explainability integrated  
✔ Professional report generation  

---

## 📜 License

This project is licensed under the MIT License.

---

## 👨‍💻 Author

**Guruprasad Kamath**  
GitHub: [@Guruprasad75K](https://github.com/Guruprasad75K)  
Project: [AI-Powered-Loan-Eligibility-Advisor](https://github.com/Guruprasad75K/AI-Powered-Loan-Eligibility-Advisor)

---

## 🤝 Contributing

Contributions are welcome! Please fork the repository and submit a pull request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## ⭐ Support

If you find this project useful, please give it a star!

[![GitHub Stars](https://img.shields.io/github/stars/Guruprasad75K/AI-Powered-Loan-Eligibility-Advisor.svg?style=social)](https://github.com/Guruprasad75K/AI-Powered-Loan-Eligibility-Advisor/stargazers)
