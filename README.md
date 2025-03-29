📌 Legal Case Manager & RAG System

A powerful web application that combines a **Legal Case Manager** and a **Retrieval-Augmented Generation (RAG) System** to streamline legal case management and document analysis. Built using **React.js, Flask, and MongoDB**, this tool helps legal professionals organize cases, search case details, and leverage AI for legal document summarization and query answering. ⚖️📄

---

✨ Features

 🗂️ Legal Case Manager
- Add, update, and manage legal cases 📑
- Search and filter cases 🔍
- View detailed case descriptions and images 🖼️
 🤖 RAG System
- Upload legal documents 📂
- Summarize documents using AI 🤯
- Ask legal queries based on document contents and get AI-generated responses 💡

---

 🏗️ Tech Stack

 🖥️ Frontend
- React.js ⚛️
- Framer Motion for animations 🎭
- Lucide Icons for UI enhancements 🎨

 🖧 Backend
- Flask (Python) 🐍
- Flask-CORS for handling cross-origin requests 🔄
- MongoDB as the database 🛢️
- Axios for API requests 🚀

---

 📥 Installation & Setup

 🔄 Clone the Repository
```bash
 git clone https://github.com/G2HackFest/Outliers.git
 cd Outliers
```

 ⚙️ Backend Setup (Flask API)
1. Navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Mac/Linux
   venv\Scripts\activate     # Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the Flask server:
   ```bash
   python app.py
   ```

 🖥️ Frontend Setup (React)
1. Navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the React app:
   ```bash
   npm start
   ```

---

🚀 Usage
- Open **http://localhost:3000/** in your browser 🌐
- Switch between **Legal Case Manager** and **RAG System** using the navigation bar 🏛️
- Manage cases efficiently and analyze legal documents with AI-powered insights 🤖📜

---

 📌 API Endpoints

 **Legal Case Manager**
- `GET /cases` - Fetch all cases
- `POST /cases/add` - Add a new case
- `GET /cases/:id` - Get details of a specific case

 **RAG System**
- `POST /rag/process` - Upload and process a document
- `POST /rag/query` - Get AI response to a legal query

---

💡 Future Enhancements
- **User Authentication** 🔐
- **Role-Based Access Control** ⚖️
- **Advanced AI-based Legal Recommendations** 🤯
- **Cloud Storage for Documents** ☁️

---

 🤝 Contributing
Feel free to submit issues and pull requests! 🚀

---

📝 License
This project is licensed under the **MIT License** 📜.

---

## ✉️ Contact
For queries or contributions, reach out via GitHub Issues or Pull Requests! 💬

