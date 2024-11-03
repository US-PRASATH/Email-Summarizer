import os
import base64
import csv
from flask import Flask, jsonify
from flask_cors import CORS
from flask import request
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import dateutil.parser as parser
from google.auth.transport.requests import Request
import pytesseract
from PIL import Image
import io
import quopri
from urllib import parse
from localStoragePy import localStoragePy

from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_models import ChatOllama
import google.generativeai as genai

app = Flask(__name__)
CORS(app)  # Enable CORS

genai.configure(api_key="YOUR-API-KEY")
model = genai.GenerativeModel("gemini-1.5-flash")

# Create the prompt template for summarization

def summarize_email(email_text):
    prompt = f"""
    YOU ARE A HIGHLY EFFICIENT EMAIL SUMMARIZATION ASSISTANT, TASKED WITH SUMMARIZING UNREAD EMAILS FOR A USER WHO WANTS TO QUICKLY UNDERSTAND THEIR CONTENT. YOUR SUMMARIES SHOULD BE CONCISE BUT COVER ALL IMPORTANT DETAILS. 

###INSTRUCTIONS###

- READ EACH EMAIL THOROUGHLY TO UNDERSTAND THE MAIN POINTS AND CONTEXT.
- EXTRACT KEY DETAILS, INCLUDING THE MAIN MESSAGE POINTS.
- PROVIDE A SUMMARY IN NO MORE THAN 3 SENTENCES PER EMAIL.
- HIGHLIGHT ANY URGENT OR ACTIONABLE ITEMS IN THE EMAIL.
- AVOID INCLUDING UNNECESSARY INFORMATION, ADVERTISEMENTS, OR SIGNATURE DETAILS UNLESS THEY CONTAIN CRITICAL INFORMATION.
- GROUP SIMILAR EMAILS TOGETHER IF THEY ARE PART OF AN ONGOING THREAD OR DISCUSSION.

###CHAIN OF THOUGHT###

1. IDENTIFY BASIC INFORMATION:
    1.1. DETERMINE if the email is part of a threaded conversation and group accordingly.

2. ANALYZE CONTENT FOR ESSENTIAL INFORMATION:
    2.1. READ the main body of the email, IGNORING signatures and irrelevant sections.
    2.2. SUMMARIZE key points such as requests, updates, or new information.

3. PRIORITIZE ACTIONABLE AND URGENT ITEMS:
    3.1. HIGHLIGHT any requests, deadlines, or tasks mentioned in the email.
    3.2. MARK emails that require immediate attention or follow-up.

4. PRESENT FINAL SUMMARY:
    4.1. PROVIDE a clear and concise summary for each email.
    4.2. GROUP summaries by sender or thread if they are part of the same conversation.

###FORMAT OF OUTPUT###

For each unread email, structure the output as follows:
dont use ** or # just give the plain text

Summary: [Concise summary of the main points in 1-3 sentences] 
insert a newline here 
Action Required: [List any actions the user needs to take, if applicable and include any links here,you must find the important links from the email_text and also shorten the url if possible]

    ###EMAIL CONTENT###
    {email_text}
    """
    response = model.generate_content(prompt)
    return response.text

# Set Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']  # 'modify' allows marking emails as read

def authenticate_gmail():
    """Authenticate and return Gmail API service."""
    creds = None
    localstorage = localStoragePy('emailsummarizer','sqlite')
    token = localstorage.getItem('token')
    if token:
    #if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        #with open('token.json', 'w') as token:
            #token.write(creds.to_json())
        localstorage.setItem('token',creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def list_unread_messages(service, page_token=None):
    """Fetch unread messages and return their details."""
    results = service.users().messages().list(
        userId='me', labelIds=['INBOX', 'UNREAD'], pageToken=page_token, maxResults=3).execute()
    messages = results.get('messages', [])
    print(f"Total unread messages in this batch: {len(messages)}")
    return messages, results.get('nextPageToken')

def extract_images_and_ocr(parts):
    ocr_text = ""
    for part in parts:
        if part['mimeType'].startswith("image/"):
            image_data = part['body'].get('data')
            if image_data:
                image_bytes = base64.urlsafe_b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                
                # Run OCR on the image
                ocr_text += pytesseract.image_to_string(image) + "\n"
    return ocr_text

def get_message_details(service, msg_id):
    """Get message details for a given message ID and summarize the content."""
    msg = service.users().messages().get(userId='me', id=msg_id).execute()
    payload = msg['payload']
    headers = payload.get('headers')
    
    #msg_details = {'Snippet': msg.get('snippet')}
    msg_details = {'Snippet': msg.get('snippet'), 'ID': msg_id}
    
    # Extract headers: Subject, Date, From
    for header in headers:
        if header['name'] == 'Subject':
            msg_details['Subject'] = header['value']
        if header['name'] == 'Date':
            msg_date = parser.parse(header['value'])
            msg_details['Date'] = msg_date.strftime('%Y-%m-%d')
        if header['name'] == 'From':
            msg_details['Sender'] = header['value']
        

    # Extract message body
    parts = payload.get('parts', [])
    message_body = ""
    links_text = ""
    for part in parts:
        if part['mimeType'] == 'text/plain':
            data = part['body'].get('data')
            if data:
                decoded_data = base64.urlsafe_b64decode(data).decode('utf-8')
                message_body = decoded_data
        elif part['mimeType'] == 'text/html':
            data = part['body'].get('data')
            if data:
                decoded_data = base64.urlsafe_b64decode(data).decode('utf-8')
                soup = BeautifulSoup(decoded_data, "html.parser")
                message_body = soup.get_text()
                 # Extract links and text from buttons and anchors
                for link in soup.find_all(['a', 'button']):
                    link_text = link.get_text().strip()
                    #link_text = parse.unquote_plus(quopri.decodestring(link_text).decode('utf-8'))
                    link_text = parse.unquote(link_text)
                    href = link.get('href')
                    if href:
                        links_text += f"Text: {link_text}, Link: {href}\n"
    
    # Combine email body text and extracted links
    #combined_text = message_body + "\n\nLinks and Buttons:\n" + links_text

    # Summarize the email content using the chain
    # Extract images and run OCR
    ocr_text = extract_images_and_ocr(parts)
    print("ocr text:"+ocr_text)
    # Combine email body text and OCR text
    combined_text = message_body + "\n\nImages Text:\n" + ocr_text + "\n\nLinks and Buttons:\n" + links_text
    
    # Summarize combined content with Gemini
    summary_result = summarize_email(combined_text)

    # Adding the summary to message details
    msg_details['Summary'] = summary_result# Directly assign the summary string
    msg_details['Links'] = links_text
    
    # Mark the message as read
    #service.users().messages().modify(userId='me', id=msg_id, body={'removeLabelIds': ['UNREAD']}).execute()
    return msg_details

def export_to_csv(messages, filename='emails.csv'):
    """Export list of message dictionaries to a CSV file."""
    if messages:
        keys = messages[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as output_file:
            dict_writer = csv.DictWriter(output_file, fieldnames=keys)
            dict_writer.writeheader()
            dict_writer.writerows(messages)
        print(f"Data exported to {filename}")

def get_unread_emails():
    # Authenticate and get Gmail API service
    page_token = request.args.get('pageToken')
    service = authenticate_gmail()
    page_token = None
    #messages, page_token = list_unread_messages(service, page_token)
    messages, next_page_token = list_unread_messages(service, page_token)
    final_list = []
    for message in messages:
        msg_id = message['id']
        msg_details = get_message_details(service, msg_id)
        final_list.append(msg_details)
        print(f"Retrieved message: {msg_details}")
    return jsonify({
        'emails':final_list,
        'next_page_token':next_page_token
    })


@app.route('/emails', methods=['GET'])
def get_emails():
    
    emails = get_unread_emails()
    #return jsonify(emails)
    return emails

if __name__ == '__main__':
    app.run(port=5000)
