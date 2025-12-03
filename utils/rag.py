"""RAG utilities for EVA application."""
import os
import streamlit as st
import datetime
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings 
from langchain_qdrant import QdrantVectorStore
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough


import requests
from bs4 import BeautifulSoup
import docx2txt

def ingest_file(conn, file, category, user):
    """Ingest a file (PDF, DOCX, TXT, MD) into the vector store and database."""
    text = ""
    if file.name.endswith('.pdf'):
        text = "".join([p.extract_text() for p in PdfReader(file).pages])
    elif file.name.endswith('.docx'):
        text = docx2txt.process(file)
    elif file.name.endswith('.txt') or file.name.endswith('.md'):
        text = file.read().decode("utf-8")
        
    if not text: return

    chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100).split_text(text)
    
    c = conn.cursor()
    c.execute("INSERT INTO documents (company_id, filename, category, uploaded_by, upload_date, full_text) VALUES (?, ?, ?, ?, ?, ?)",
              (user["company_id"], file.name, category, user["email"], datetime.datetime.now().isoformat(), text))
    conn.commit()
    
    _push_to_qdrant(chunks, user)

def ingest_url(conn, url, category, user):
    """Ingest content from a URL."""
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text()
        
        chunks = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100).split_text(text)
        
        c = conn.cursor()
        c.execute("INSERT INTO documents (company_id, filename, category, uploaded_by, upload_date, full_text) VALUES (?, ?, ?, ?, ?, ?)",
                  (user["company_id"], url, category, user["email"], datetime.datetime.now().isoformat(), text))
        conn.commit()
        
        _push_to_qdrant(chunks, user)
        return True
    except Exception as e:
        st.error(f"URL Error: {e}")
        return False

def _push_to_qdrant(chunks, user):
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    collection_name = f"collection_{user['company_id']}"
    
    try:
        QdrantVectorStore.from_texts(
            texts=chunks,
            embedding=embeddings,
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
            collection_name=collection_name,
            force_recreate=False
        )
    except Exception as e: st.error(f"Qdrant Error: {e}")


def chat_with_jarvis(user, query):
    """Process a query using RAG and the LLM."""
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    collection_name = f"collection_{user['company_id']}"
    
    try:
        vector_store = QdrantVectorStore.from_existing_collection(
            embedding=embeddings,
            collection_name=collection_name,
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
        )
        retriever = vector_store.as_retriever(search_kwargs={"k": 4})
        
        template = """You are EVA, a professional internal knowledge assistant for {company_name}.
        GUIDELINES:
        1. **Tone:** Professional, concise, and direct.
        2. **Accuracy:** Answer ONLY based on the Context.
        VISUALIZATION RULES:
        1. If the answer describes a workflow/process, generate a Mermaid.js diagram.
        2. **Syntax Safety:** No brackets () in node labels. Use A[Start] --> B[Process].
        3. Place mermaid code at the end.

        Context: {context}
        Question: {question}
        Professional Answer:"""
        
        model = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.2)
        prompt_template = ChatPromptTemplate.from_template(template)
        chain = (
            {
                "context": retriever | (lambda docs: "\n\n".join(d.page_content for d in docs)), 
                "question": RunnablePassthrough(),
                "company_name": lambda x: user['company_name']
            }
            | prompt_template 
            | model 
            | StrOutputParser()
        )
        return chain.invoke(query)
    except Exception:
        return "⚠️ I am unable to access the company knowledge base at this moment."
