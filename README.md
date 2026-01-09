# 🚀 **AI Personal Expense Categorizer**  
*Full-stack web app with AI-powered expense classification & analytics*



A modern expense tracker that uses **rule-based AI** to automatically categorize spending from natural language descriptions. Built as a final-year CSE project showcasing full-stack development, authentication, data visualization, and intelligent text processing.

## ✨ **Key Features**

| Feature | Status |
|---------|--------|
| 🔐 **Multi-user authentication** (email + secure password hashing) | ✅ Complete |
| 🤖 **AI categorization** (Food, Bills, Shopping, Transport, etc.) | ✅ Live |
| 📱 **Dual input modes**: Free-text OR structured forms | ✅ Dual support |
| 📊 **Interactive charts** (Chart.js) + category totals | ✅ Responsive |
| 🗑️ **Recent expenses** with per-row delete | ✅ Functional |
| 📅 **Month selector**: This month / Last month / All time | ✅ Filtering works |
| 🎨 **Responsive Bootstrap UI** | ✅ Mobile-ready |
| 👁️ **Password visibility toggle** (eye emoji) | ✅ UX enhanced |

## 🛠️ **Tech Stack**
```
Backend: Python 3.8+ | Flask | Werkzeug (security)
Frontend: HTML5 | Bootstrap 5 | Chart.js 4 | Vanilla JS
Database: SQLite3 (user_id foreign keys)
Deployment: Render/Railway ready
```

## 🎯 **Live Demo Flow**
```
Register/Login → Add "spent 250 biriyani" → AI → Food category
→ Switch "Monthly Summary" → See Chart.js bar graph
→ Filter "Last month" → Data updates instantly
→ 🗑 Delete wrong entries → Logout
```

## 🚀 **Quick Start** 

```bash
# Clone & setup
git clone https://github.com/YOUR-USERNAME/ai-expense-categorizer.git
cd ai-expense-categorizer

# Virtual environment
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate

# Install & run
pip install flask werkzeug
python app.py
```

**Open:** `http://127.0.0.1:5000`

## 🤖 **AI Categorization Demo**

```python
# Input: "Paid 200 for chicken biriyani"
# Output: "Food" (keyword matching)

# Input: "Uber ride 150 to office"  
# Output: "Transport" (keyword matching)

# 8+ categories with 50+ keywords covering:
# Food • Bills • Transport • Shopping • Rent
# Entertainment • Health • Education • Other
```

**Manual override** available in structured form.

## 📁 **Project Structure**
```
expense_categorizer/
├── app.py                 # Flask app + AI logic
├── requirements.txt       # Dependencies
├── templates/
│   ├── index.html        # Dashboard + charts
│   ├── login.html        # Auth UI
│   └── register.html     # Registration
└── expenses.db           # SQLite (local only)
```


**👤 Built by Gautam Dev**   
**✉️** gautamdev1910.com **| 📱** +91 8138825032
**🔗** [LinkedIn] www.linkedin.com/in/gautam-dev1910























