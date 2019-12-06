import pickle
import os.path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from email.mime.text import MIMEText
import base64
from server import crud

def get_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    service = build('gmail', 'v1', credentials=creds)
    return service

def compose_email(sender, to, subject, body, cc=None):
    email = MIMEText(body, 'html')
    email['to'] = to
    if cc:
        email['cc'] = cc
    email['from'] = sender
    email['subject'] = subject
    return {'raw': base64.urlsafe_b64encode(email.as_bytes()).decode()}

def compose_email_from_me(to, subject, body, cc_customer=False):
    cc = '<customer@psyclonicstudios.com.au>' if cc_customer else None
    return compose_email(f"Anne-Maree Hunter <annemaree@psyclonicstudios.com.au>", to, subject, body, cc=cc)

def compose_email_to_me_as_customer(sender, subject, body):
    return compose_email(sender, f"Anne-Maree Hunter <customer@psyclonicstudios.com.au>", subject, body)

def send_email(message):
    try:
        email = get_service().users().messages().send(userId='me', body=message).execute()
        return email
    except HttpError as error:
        print(f'An error occurred: {error}')

def get_email_link(id):
    return f'https://mail.google.com/mail?authuser=annemaree@psyclonicstudios.com.au#all/{id}'