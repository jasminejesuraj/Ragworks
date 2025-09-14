# This script creates a full-stack RAG application with Streamlit and Gemini.
# It includes user authentication, document upload, and a chat interface with a
# simple SQLite database for persistent user data and chat history.
#
# To run this application:
# 1. Save the code as 'app.py'.
# 2. Create a .gitignore file in the same directory and add .env to it.
# 3. Create a .env file in the same directory with your Gemini API key:
#    GEMINI_API_KEY="your-api-key-here"
# 4. Install the required libraries:
#    pip install streamlit python-dotenv google-generativeai pypdf passlib
# 5. Run the app from your terminal:
#    streamlit run app.py

import os
import streamlit as st
import google.generativeai as genai
import sqlite3
from passlib.context import CryptContext
from dotenv import load_dotenv
from PyPDF2 import PdfReader

# The st.set_page_config command must be the first command in a Streamlit script.
st.set_page_config(layout="wide")

# --- Configuration & Utility Functions ---

# Load environment variables
load_dotenv()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_gemini_api_key():
    """Retrieves the Gemini API key from environment variables."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("Error: GEMINI_API_KEY not found. Please set your environment variable.")
        st.stop()
    return api_key

# Configure the Gemini API client
api_key = get_gemini_api_key()
if api_key:
    genai.configure(api_key=api_key)

# --- Database Functions ---

def init_db():
    """Initializes the SQLite database and creates tables if they don't exist."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password_hash TEXT
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            role TEXT,
            content TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    """Hashes a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    """Verifies a plain-text password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def register_user(username, password):
    """Registers a new user and returns True if successful, False otherwise."""
    try:
        conn = sqlite3.connect("users.db")
        c = conn.cursor()
        hashed_password = hash_password(password)
        c.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Username already exists
    finally:
        conn.close()

def login_user(username, password):
    """Logs in a user and returns their user ID if credentials are correct, None otherwise."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    user_data = c.fetchone()
    conn.close()
    if user_data and verify_password(password, user_data[1]):
        return user_data[0]  # Return user ID
    return None

def get_chat_history(user_id):
    """Retrieves a user's chat history from the database."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT role, content FROM chat_history WHERE user_id = ?", (user_id,))
    history = [{"role": row[0], "content": row[1]} for row in c.fetchall()]
    conn.close()
    return history

def save_message(user_id, role, content):
    """Saves a single message to the user's chat history in the database."""
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (user_id, role, content) VALUES (?, ?, ?)", (user_id, role, content))
    conn.commit()
    conn.close()

# --- Document Processing for RAG ---

def extract_text_from_pdf(file):
    """
    Extracts text from a PDF file.
    """
    reader = PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text

# --- Main Application Logic ---

def main_app():
    """
    Main Streamlit application logic, runs after successful authentication.
    """
    st.markdown("""
        <style>
            .stTextInput>div>div>input {
                -webkit-text-security: none;
                -moz-text-security: none;
                text-security: none;
                -webkit-appearance: none;
                -moz-appearance: none;
                appearance: none;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f"""
        <h1 style="text-align: center; color: black; font-size: 3em; 
        font-family: 'Helvetica Neue', sans-serif;">
            <span style="display:inline-block; animation: bounce 1s infinite;">
                🤖
            </span> 
            Gemini RAG Chatbot 
            <span style="display:inline-block; animation: bounce 1s infinite; animation-delay: 0.2s;">
                📄
            </span>
        </h1>
        <style>
            @keyframes bounce {{
                0%, 100% {{ transform: translateY(0); }}
                50% {{ transform: translateY(-10px); }}
            }}
        </style>
    """, unsafe_allow_html=True)

    st.markdown("---") # Add a horizontal line for separation
    st.markdown(f"Welcome, {st.session_state.username}!")
    st.markdown("Ask questions about your own documents!")

    # Sidebar for document upload and settings
    with st.sidebar:
        st.header("Document Upload")
        uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")
        
        if uploaded_file is not None:
            document_content = extract_text_from_pdf(uploaded_file)
            st.session_state.document_content = document_content
            st.success("Document uploaded and processed successfully!")
        
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.username = None
            st.session_state.document_content = None
            st.rerun()

    # Initialize chat history from the database
    if "messages" not in st.session_state or st.session_state.messages == []:
        st.session_state.messages = get_chat_history(st.session_state.user_id)

    # Display chat messages from history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input and message handling
    if prompt := st.chat_input("What is your question?"):
        # Add user message to chat history and save to DB
        user_message = {"role": "user", "content": prompt}
        st.session_state.messages.append(user_message)
        save_message(st.session_state.user_id, "user", prompt)

        with st.chat_message("user"):
            st.markdown(prompt)

        # Check if a document has been uploaded before answering
        if st.session_state.document_content:
            # Augment the prompt with the document content (RAG)
            context = st.session_state.document_content
            full_prompt = (f"Based on the following document content, answer the user's question. "
                           f"Document: {context}\n\nUser Question: {prompt}")
            
            # Call the Gemini API to get a response
            model = genai.GenerativeModel('gemini-1.5-flash')
            try:
                response = model.generate_content(full_prompt)
                ai_response = response.text
            except Exception as e:
                ai_response = f"An error occurred: {e}"
        else:
            ai_response = "Please upload a document first to enable the RAG feature."

        # Display AI response and save to history
        assistant_message = {"role": "assistant", "content": ai_response}
        st.session_state.messages.append(assistant_message)
        save_message(st.session_state.user_id, "assistant", ai_response)
        with st.chat_message("assistant"):
            st.markdown(ai_response)


# --- Authentication Logic ---

def login_page():
    st.title("Login / Register")
    choice = st.selectbox("Choose an action", ["Login", "Register"])

    if choice == "Login":
        st.subheader("Login to your account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            user_id = login_user(username, password)
            if user_id:
                st.session_state.logged_in = True
                st.session_state.user_id = user_id
                st.session_state.username = username
                st.success("Logged in successfully!")
                st.rerun()
            else:
                st.error("Invalid username or password.")
    else:
        st.subheader("Create a new account")
        new_username = st.text_input("Choose a Username")
        new_password = st.text_input("Choose a Password", type="password")
        if st.button("Register"):
            if register_user(new_username, new_password):
                st.success("Account created successfully! Please login.")
            else:
                st.error("Username already exists. Please choose a different one.")

# Main app entry point
if __name__ == "__main__":
    init_db()  # Ensure database is initialized
    
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        main_app()
    else:
        login_page()
