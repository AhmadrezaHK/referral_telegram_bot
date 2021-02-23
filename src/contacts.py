import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/contacts.readonly']

results = None


def check_contact(entry_number):

    entry_number = "+989" + entry_number.replace(" ", "")[-9:]

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials-contacts.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('people', 'v1', credentials=creds)

    # Call the People API

    global results
    if results is None:
        print("it was none")
        results = service.people().connections().list(
            resourceName='people/me',
            pageSize=200,
            personFields='names,phoneNumbers').execute()
    connections = results.get('connections', [])

    contacts = {}

    for person in connections:
        if person is None or person.get("phoneNumbers") is None:
            continue
        else:
            contacts[person.get('phoneNumbers')[0].get('value').replace(
                " ", "")] = person.get('names')[0].get('givenName')

    if entry_number in list(contacts.keys()):
        return contacts[entry_number]
    else:
        return None
