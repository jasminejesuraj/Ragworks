# Ragworks

Project Documentation

1. Executive Summary
 This repository contains a full-stack Retrieval-Augmented Generation (RAG) application, engineered to provide contextual, data-driven responses by leveraging proprietary documents. The system is designed for secure, user-specific interactions, featuring a robust authentication module, a streamlined document processing pipeline, and a persistent chat history. The architecture prioritizes data privacy and operational integrity, making it suitable for professional and enterprise-level use cases.

2. Core Components & Functionality
 The application is built upon a modular architecture with three key components:
 
 User Authentication System: Manages user identity and access control. It utilizes SQLite for user data persistence and passlib with bcrypt for secure password hashing and verification.
 
 RAG Pipeline: The core of the application's intelligence. Upon document upload, text is extracted from PDF files using PyPDF2. The extracted content serves as a knowledge base, which is then dynamically incorporated into prompts to the Gemini API, enabling context-aware and verifiable responses.
 
 Persistent Chat History: User conversations are logged to an SQLite database, ensuring that chat history is maintained across sessions. This provides a seamless and continuous user experience.

3. Technical Stack

 Component	Technology	Purpose
 #Backend	Python 3.8+ :
 Core application logic, API communication, and data processing.
 
 #Frontend:
 Streamlit	Provides the web-based, interactive user interface.
 
 #AI Model:
 Google Gemini API	Powers the generative AI and RAG capabilities.
 
 #Database:
 SQLite3	A lightweight, file-based database for user and chat data.
 
 #Security:
 passlib (bcrypt)	Secure password hashing and verification.

4. Usage & Local Deployment
 This application is provided for local execution only. Follow these steps to set up and run the application on your machine.
 
 Prerequisites:
 Python 3.8 or higher
 
 Application Setup:
 Download Project Files: Download and extract the project files from this repository to your local machine.
 
 Environment Setup: Navigate to the project directory and create a Python virtual environment to manage dependencies.
 python -m venv venv
  On Windows: venv\Scripts\activate
  On macOS/Linux: source venv/bin/activate
 
 Dependency Installation: Install all required libraries.
 pip install streamlit python-dotenv google-generativeai pypdf "passlib[bcrypt]<1.8.0,>=1.7.4"
 
 API Key Management:
 Acquire API Key: Obtain a valid API key from the Google AI Studio.
 Configuration: Create a .env file in the project's root directory based on the provided env-example template.
 GEMINI_API_KEY="your-api-key-here"
 
 Execution:
 Launch the application using the following command from the terminal:
 streamlit run app.py
 The application will automatically open in your default web browser, accessible via a local host address.

5. Intellectual Property & Rights Reserved
 This repository is published without an explicit license. All rights to the code and documentation are reserved by copyright.
 You are permitted to download and run this application on your local machine for personal use.
 You are not permitted to copy, modify, distribute, or otherwise reproduce this code, in whole or in part, without explicit written permission from the author.
 This includes actions such as cloning, forking, and creating derivative works, all of which are prohibited.
 
