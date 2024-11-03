# Email Summarizer
This project is a React and Flask-based email summarization application that leverages the Gmail API and Gemini model for efficient summarization of unread emails. This application fetches unread emails from the user's Gmail inbox, summarizes the content for quick insights, and allows marking emails as read.

## Features
**Gmail API Integration** : Authenticate and fetch unread emails from the user's Gmail inbox.
**Email Summarization**: Summarizes the content of each email using the Gemini AI model.
**React Frontend**: Displays email summaries in a user-friendly interface with options to mark emails as read.

## Prerequisites
Node.js (for running the React frontend)
Python (for the Flask backend)
Pip (for installing Python dependencies)
Gmail API access: A Google Cloud project set up for Gmail API with OAuth 2.0 credentials.

## Installation

Clone the Repository:
git clone https://github.com/US-PRASATH/Email-Summarizer.git
cd email-summarizer

Backend Setup (Flask):
Navigate to the backend directory:
cd backend

Install Python dependencies:
pip install -r requirements.txt

Configure Gmail API:
Place your client_secret.json in the root of the backend directory.
This file is necessary for OAuth2 authentication with Gmail.
Set up Gemini API by configuring your Gemini API key in the backend code where genai.configure is called.

Frontend Setup (React):
Navigate to the frontend directory:
cd frontend

Install frontend dependencies:
npm install
Running the Application
Start the Backend Server:

Run the Flask server from the backend directory:
python server.py
This starts the server on http://localhost:5000.

Start the Frontend Server:
In a new terminal, navigate to the frontend directory:
cd frontend

Start the React app:
npm start
The app will open in http://localhost:3000.
