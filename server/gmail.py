import pickle
import os.path
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
import base64


def get_service():
    creds = None
    if os.path.exists("gmail_token.pickle"):
        with open("gmail_token.pickle", "rb") as token:
            creds = pickle.load(token)
    else:
        raise ValueError("Cannot find gmail credentials")
    service = build("gmail", "v1", credentials=creds)
    return service


def compose_email(sender, to, subject, body, cc=None):
    email = MIMEText(body, "html")
    email["to"] = to
    if cc:
        email["cc"] = cc
    email["from"] = sender
    email["subject"] = subject
    return {"raw": base64.urlsafe_b64encode(email.as_bytes()).decode()}


def compose_email_from_me(to, subject, body, alias=None):
    cc = "Anne-Maree Hunter <annemaree@psyclonicstudios.com.au>" if alias else None
    sender = (
        f"{alias} <{alias.lower()}@psyclonicstudios.com.au>"
        if alias
        else "Anne-Maree Hunter <annemaree@psyclonicstudios.com.au>"
    )
    return compose_email(sender, to, subject, body, cc=cc)


def send_email(message):
    try:
        email = (
            get_service().users().messages().send(userId="me", body=message).execute()
        )
        return email
    except HttpError as error:
        print(f"An error occurred: {error}")


def get_email_link(id):
    return f"https://mail.google.com/mail?authuser=annemaree@psyclonicstudios.com.au#all/{id}"
