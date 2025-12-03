# EVA: Enterprise Voice Assistant

**EVA** (Enterprise Voice Assistant) is a secure, AI-powered internal knowledge assistant designed for enterprise environments. It combines RAG (Retrieval-Augmented Generation) with a seamless voice interface to provide instant access to company knowledge.

## 🚀 Features

- **🔐 Secure Authentication**: Company-based workspaces with Admin/Employee roles.
- **📚 RAG Knowledge Base**: Upload PDFs to create a searchable company knowledge base.
- **💬 AI Chat Interface**: Text-based interaction with Mermaid.js diagram support for workflows.
- **📞 AI Call Mode**: Hands-free voice interaction with ultra-low latency and instant visual aids.
- **📊 Admin Dashboard**: Manage documents and view team statistics.
- **👤 User Profile**: View personal and company details.

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **LLM**: Google Gemini 2.0 Flash
- **Vector Store**: Qdrant
- **Embeddings**: HuggingFace (all-MiniLM-L6-v2)
- **TTS**: gTTS (Google Text-to-Speech)
- **STT**: SpeechRecognition (Google API)
- **Database**: SQLite

## 📦 Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd EVA
    ```

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Set up environment variables:**
    Create a `.env` file with the following:
    ```env
    GOOGLE_API_KEY=your_google_api_key
    QDRANT_URL=your_qdrant_url
    QDRANT_API_KEY=your_qdrant_api_key
    ```

4.  **Run the application:**
    ```bash
    streamlit run main.py
    ```

## 📂 Project Structure

```
EVA/
├── main.py                    # Entry point
├── pages/                     # Application pages
│   ├── 1_🔐_Login.py
│   ├── 2_💬_Chat.py
│   ├── 3_📞_Call_Mode.py
│   ├── 4_📊_Admin_Dashboard.py
│   └── 5_👤_User_Profile.py
├── utils/                     # Shared utilities
│   ├── database.py
│   ├── auth.py
│   ├── rag.py
│   ├── audio.py
│   ├── styling.py
│   └── sidebar.py
├── eva.db                     # SQLite database
└── requirements.txt
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
