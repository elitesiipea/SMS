from googleapiclient.discovery import build
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Function to create a G Suite account
def create_gsuite_account(email, nom, prenom):
    lien = "/home/daniel/Desktop/SMS/SMS/etudiants/credentials.json"

    SCOPES = ['https://www.googleapis.com/auth/admin.directory.user','https://www.googleapis.com/auth/admin.directory.group.member']

    creds = None

    if Path("token.json").exists():
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(lien, SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    service = build('admin', 'directory_v1', credentials=creds)
    user_data = {
        'primaryEmail': email,
        'name': {
            'familyName': nom,   # Replace with the student's last name
            'givenName': prenom,   # Replace with the student's first name
        },
        'password': '@elites@',  # Set a temporary password for the student
        'changePasswordAtNextLogin': True,
    }

    try:
        user = service.users().insert(body=user_data).execute()
        print(user)

        # Add the user to the "student@iipea.com" group
        group_key = 'student@iipea.com'  # Replace with the correct group email
        member_key = user['primaryEmail']

        members = {
            "email": member_key
        }

        result = service.members().insert(groupKey=group_key, body=members).execute()
        print(result)  # Print the result to check if the user was added to the group

        return user

    except Exception as e:
        # Handle other errors or exceptions
        print(f"Error creating G Suite account: {e}")
        return None

# Example usage
create_gsuite_account("dad@iipea.com", "bobo", "baba")
