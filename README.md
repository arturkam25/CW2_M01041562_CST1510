# Multi-Domain Intelligence Platform

## Student Information
- **Student:** Artur Kamerski
- **Student ID:** M01041562
- **Module:** CST1510 - BSc Cyber Security and Digital Forensics
- **Project:** CW2 - Multi-Domain Intelligence Platform

---

## 1. Project Overview

The Multi-Domain Intelligence Platform is a comprehensive web-based analytics and intelligence system built with Streamlit. It provides secure, role-based access to multiple data domains including cyber security incidents, IT support tickets, dataset metadata, and an AI-powered assistant.

### Key Features
- **Secure Authentication System** - Role-based access control with password hashing
- **Multi-Domain Analytics** - Interactive dashboards for cyber incidents, IT tickets, and datasets
- **AI Assistant** - OpenAI-powered chat interface with image analysis support
- **User Management** - Administrative interface for account management
- **Data Visualization** - Interactive charts and graphs using Plotly
- **Persistent Storage** - SQLite database with per-user chat history

---

## 2. Architecture

### Technology Stack
- **Frontend:** Streamlit (Python web framework)
- **Database:** SQLite3
- **Visualization:** Plotly Express & Graph Objects
- **Data Processing:** Pandas, NumPy
- **AI Integration:** OpenAI API (GPT-4o)
- **Security:** bcrypt for password hashing
- **Image Processing:** Pillow (PIL)

### Project Structure
```
├── Home.py                    # Main entry point and authentication
├── pages/                     # Streamlit pages (modules)
│   ├── 1_Users.py            # User management (Admin only)
│   ├── 2_Cyber_Incidents.py  # Cyber incidents analytics
│   ├── 3_Datasets.py         # Dataset metadata analytics
│   ├── 4_IT_Tickets.py       # IT tickets analytics
│   ├── 5_Forgot_Password.py  # Password recovery
│   └── 6_AI_Assistant.py      # AI chat assistant
├── app/
│   ├── data/                  # Data access layer
│   │   ├── db.py             # Database connection
│   │   ├── schema.py         # Database schema
│   │   ├── users.py          # User management
│   │   ├── security.py       # Authentication & password security
│   │   ├── cyber_incidents.py
│   │   ├── datasets.py
│   │   └── it_tickets.py
│   ├── services/              # Business logic layer
│   │   ├── chat_history.py   # Chat persistence
│   │   └── user_service.py   # User operations
│   └── utils/                 # Utility functions
│       ├── auth.py           # Authentication guards
│       └── navigation.py      # Navigation components
├── DATA/                      # Application data (gitignored)
│   ├── inteligence_platform.db
│   ├── chat_history/
│   └── *.csv
└── static/                    # Static assets
    └── middlesex_logo.png
```

---

## 3. Installation & Setup

### Prerequisites
- Python 3.10 or later
- pip package manager

### Installation Steps

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CW2_M01041562_CST1510
   ```

2. **Install dependencies**
   ```bash
   pip install -r requiremens.txt
   ```

3. **Configure OpenAI API (for AI Assistant)**
   - Create a `.streamlit/secrets.toml` file
   - Add your OpenAI API key:
     ```toml
     OPENAI_API_KEY = "your-api-key-here"
     ```

4. **Initialize the database** (optional)
   - The database will be created automatically on first run
   - To populate with sample data, run:
     ```bash
     python Week_7/main.py
     ```

5. **Run the application**
   ```bash
   streamlit run Home.py
   ```
   The application will open in your browser at `http://localhost:8501`

---

## 4. Application Modules

### 4.1 Authentication & Registration
- **Location:** `Home.py`
- **Features:**
  - User registration with email and recovery code
  - Secure login with account lockout (3 failed attempts)
  - Password recovery using email and recovery code
  - Username recovery
  - Role-based access control (user/admin)

### 4.2 User Management (Admin Only)
- **Location:** `pages/1_Users.py`
- **Features:**
  - View all registered users
  - Create new user accounts
  - Delete user accounts
  - Lock/unlock accounts
  - Reset user passwords
  - View user statistics

### 4.3 Cyber Incidents Analytics
- **Location:** `pages/2_Cyber_Incidents.py`
- **Features:**
  - Interactive dashboard for cyber security incidents
  - Filtering and data exploration
  - Visualizations: bar charts, pie charts, time series
  - Data export capabilities
  - Key metrics and statistics

### 4.4 Datasets Analytics
- **Location:** `pages/3_Datasets.py`
- **Features:**
  - Dataset metadata overview
  - Size and structure analysis
  - Uploader activity tracking
  - Dataset categorization
  - Interactive visualizations

### 4.5 IT Tickets Analytics
- **Location:** `pages/4_IT_Tickets.py`
- **Features:**
  - IT support ticket dashboard
  - Priority and status analysis
  - Issue type categorization
  - Workload distribution
  - Interactive filtering and export

### 4.6 AI Assistant
- **Location:** `pages/6_AI_Assistant.py`
- **Features:**
  - Conversational AI interface (GPT-4o)
  - Text and image input support
  - Per-user chat history persistence
  - Context window management (20 messages)
  - Image analysis capabilities

---

## 5. Security Features

### 5.1 Password Security
- **Hashing:** bcrypt with automatic salting
- **Policy Requirements:**
  - Minimum 8 characters
  - At least 1 uppercase letter
  - At least 1 lowercase letter
  - At least 1 digit
  - At least 1 special character
- **Storage:** Passwords are never stored in plaintext

### 5.2 Account Protection
- **Lockout Mechanism:** Accounts are locked after 3 failed login attempts
- **Recovery System:** Email + recovery code for password/username recovery
- **Session Management:** Streamlit session_state for authentication state

### 5.3 Access Control
- **Role-Based Access:** User and Admin roles
- **Page-Level Guards:** Authentication required for all protected pages
- **Admin-Only Pages:** User management restricted to administrators

---

## 6. Data Storage

### 6.1 Database (SQLite)
- **Location:** `DATA/inteligence_platform.db`
- **Tables:**
  - `users` - User accounts and authentication data
  - `cyber_incidents` - Cyber security incident records
  - `datasets` - Dataset metadata
  - `it_tickets` - IT support ticket records

### 6.2 Chat History
- **Location:** `DATA/chat_history/user_{id}.json`
- **Format:** JSON files per user
- **Content:** Conversation history with timestamps

### 6.3 CSV Data Files
- **Location:** `DATA/*.csv`
- **Purpose:** Initial data import and migration
- **Files:**
  - `cyber_incidents.csv`
  - `it_tickets.csv`
  - `datasets_metadata.csv`

---

## 7. Dependencies

All required packages are listed in `requiremens.txt`:

```
streamlit
bcrypt>=4.0.0
pandas
numpy
plotly
openai
Pillow>=10.0.0
```

### Key Libraries
- **streamlit** - Web framework
- **bcrypt** - Password hashing
- **pandas** - Data manipulation
- **numpy** - Numerical computing
- **plotly** - Interactive visualizations
- **openai** - AI API integration
- **Pillow** - Image processing

---

## 8. Usage Guide

### 8.1 First-Time Setup

**Default Accounts (Pre-configured):**

For immediate access to all features, use the following pre-configured accounts:

1. **Administrator Account:**
   - **Username:** `admin`
   - **Password:** `Mateusz26`
   - **Access:** Full admin privileges, can manage users and access all modules

2. **User Account (with AI chat history):**
   - **Username:** `Matt`
   - **Password:** `Mateusz26`
   - **Access:** Standard user privileges, includes existing AI conversation history

**Note:** New users registering through the registration form will only receive **user** privileges. Only existing administrators can grant admin privileges to other users through the User Management page.

**First-Time Steps:**
1. Log in using one of the default accounts above, or
2. Register a new account on the home page (will have user privileges only)
3. Save your recovery code if registering (displayed during registration)
4. Access available modules from the sidebar

### 8.2 Admin Access
- Users with username "admin" automatically receive admin privileges
- Admins can access the "Users" page for account management
- Admin functions: create users, delete users, lock/unlock accounts, reset passwords
- **Only admins can grant admin privileges to other users** - new registrations default to user role

### 8.3 Using the AI Assistant
1. Navigate to "AI Assistant" from the sidebar
2. Enter your message in the chat input
3. Upload images (optional) for analysis
4. Chat history is automatically saved per user
5. Clear chat history using the sidebar button

### 8.4 Analytics Dashboards
- Use filters to explore data
- Interact with charts (zoom, pan, hover for details)
- Export filtered data using the export button
- View key metrics in summary cards

---

## 9. Development Notes

### 9.1 Code Organization
- **Separation of Concerns:** UI, business logic, and data access are separated
- **Modular Design:** Each page is independent and focused
- **Type Safety:** Clear function signatures and documentation
- **Error Handling:** Graceful error messages and fallbacks

### 9.2 Database Schema
- Tables are created automatically on first run via `app/data/schema.py`
- Migration scripts available in `Week_7/main.py`
- CSV data can be imported using migration functions

### 9.3 Session Management
- Authentication state stored in `st.session_state`
- Per-user chat history isolated by user ID
- Session persists across page navigation

---

## 10. File Structure Details

### Core Application Files
- `Home.py` - Main entry point, authentication UI
- `pages/*.py` - Individual module pages
- `app/data/*.py` - Data access layer (database operations)
- `app/services/*.py` - Business logic services
- `app/utils/*.py` - Utility functions and helpers

### Configuration
- `.streamlit/secrets.toml` - API keys and secrets (gitignored)
- `requiremens.txt` - Python dependencies
- `.gitignore` - Git ignore rules

### Data Files (Gitignored)
- `DATA/` - All application data
- `logs.txt` - Legacy log file (not used in current version)
- `users.txt` - Legacy user file (migrated to database)

---

## 11. Limitations & Future Enhancements

### Current Limitations
- No email sending for recovery codes (manual display)
- No multi-factor authentication (MFA)
- SQLite database (single-file, not suitable for high concurrency)
- Chat history stored as JSON files (not in database)

### Potential Enhancements
- Email integration for recovery codes
- Multi-factor authentication (SMS/email/TOTP)
- PostgreSQL or MySQL for production database
- Chat history in database for better querying
- Real-time notifications
- Advanced analytics and reporting
- API endpoints for external integrations
- Docker containerization
- CI/CD pipeline

---

## 12. Troubleshooting

### Common Issues

**Issue:** Application won't start
- **Solution:** Ensure all dependencies are installed: `pip install -r requiremens.txt`

**Issue:** OpenAI API errors
- **Solution:** Check `.streamlit/secrets.toml` contains valid `OPENAI_API_KEY`

**Issue:** Database errors
- **Solution:** Delete `DATA/inteligence_platform.db` and restart (will recreate schema)

**Issue:** Chat history not loading
- **Solution:** Check `DATA/chat_history/` directory exists and has proper permissions

**Issue:** Account locked
- **Solution:** Admin must unlock account via Users page, or use password recovery

---

## 13. License & Credits

- **Course:** CST1510 - Programming for Data Communication and Networks
- **Institution:** Middlesex University
- **Academic Year:** 2025-26

---

## 14. Contact

For questions or issues related to this coursework project, please contact:
- **Student:** Artur Kamerski (M01041562)

---

**Last Updated:** 2025
