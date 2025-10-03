from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

flow = InstalledAppFlow.from_client_secrets_file('token_gen/client_secret.json', SCOPES)
creds = flow.run_local_server(port=0)

# Salva il token per uso futuro
with open('token.json', 'w') as token:
    token.write(creds.to_json())


print("✅ token.json generato!")
