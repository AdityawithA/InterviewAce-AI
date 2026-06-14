# 🚀 InterviewAce AI

An AI-powered interview preparation platform that helps users practice interviews, receive intelligent feedback, and improve their performance through personalized reports generated using Google Gemini AI.

---

## 🌐 Live Demo

**Live Application:** https://interviewace-ai-3ra7.onrender.com

**GitHub Repository:** https://github.com/AdityawithA/InterviewAce-AI

---

## 📌 Overview

InterviewAce AI is a full-stack web application designed to simulate real-world interview experiences. Users can select a job role and difficulty level, answer AI-generated interview questions, and receive detailed performance analysis with strengths, weaknesses, and improvement suggestions.

The platform uses Google Gemini AI to evaluate responses and generate personalized interview reports.

---

## ✨ Features

### 🔐 User Authentication

* User Registration
* Secure Login System
* Session Management
* Profile Management

### 🤖 AI-Powered Interviews

* HR Interview
* Frontend Developer Interview
* Backend Developer Interview
* Full Stack Developer Interview
* Data Analyst Interview
* Machine Learning Engineer Interview

### 📊 Intelligent Evaluation

* AI-generated interview questions
* Detailed answer analysis
* Question-wise scoring
* Personalized feedback

### 📈 Performance Reports

* Overall interview score
* Strength analysis
* Weakness analysis
* Improvement recommendations
* Question-wise feedback report

### 📂 Resume Support

* Resume upload functionality
* PDF resume processing
* Resume-based interview customization

### 📜 Interview History

* View previous interviews
* Access past reports
* Track performance growth

### 👤 User Dashboard

* Performance statistics
* Highest score tracking
* Average score monitoring
* Interview history overview

---

## 🛠️ Tech Stack

### Frontend

* HTML5
* CSS3
* JavaScript
* Jinja2 Templates

### Backend

* Python
* Flask

### Database

* MySQL

### AI Integration

* Google Gemini AI

### Deployment

* Render

### Additional Libraries

* Flask-WTF
* mysql-connector-python
* PyPDF2
* ReportLab
* python-dotenv
* Requests

---

## 📁 Project Structure

```bash
InterviewAce-AI/
│
├── static/
│   ├── css/
│   ├── js/
│   ├── uploads/
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── interview.html
│   ├── report.html
│   ├── history.html
│   └── profile.html
│
├── app.py
├── config.py
├── requirements.txt
├── Procfile
├── runtime.txt
├── .env
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the Repository

```bash
git clone https://github.com/AdityawithA/InterviewAce-AI.git
cd InterviewAce-AI
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

#### Windows

```bash
venv\Scripts\activate
```

#### Linux/Mac

```bash
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file:

```env
SECRET_KEY=your_secret_key

MYSQL_HOST=your_host
MYSQL_PORT=3306
MYSQL_USER=your_username
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=your_database

GEMINI_API_KEY=your_gemini_api_key

MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
MAIL_USE_TLS=True
MAIL_USE_SSL=False
```

### 6. Import Database

Import the provided SQL file into your MySQL database.

### 7. Run the Application

```bash
python app.py
```

Visit:

```text
http://127.0.0.1:5000
```

---



## 🔒 Security Features

* Password hashing
* Session protection
* Environment variable configuration
* Secure database credentials
* File upload validation

---

## 🚀 Future Enhancements

* Voice-based interviews
* Video interview simulation
* Resume-to-interview generation
* AI career guidance
* Leaderboards and achievements
* Multi-language support
* Export reports as PDF

---

## 👨‍💻 Author

**Aditya Kumar**

GitHub: https://github.com/AdityawithA

---

## ⭐ Support

If you found this project useful, consider giving it a star on GitHub.

```bash
⭐ Star this repository
```

---

## 📄 License

This project is developed for educational and portfolio purposes.
