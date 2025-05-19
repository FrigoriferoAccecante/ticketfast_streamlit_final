from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
creds = flow.run_local_server(port=0)  # QUI si aprirà il browser

with open('token.json', 'w') as token_file:
    token_file.write(creds.to_json())

print("✅ token.json generato!")
