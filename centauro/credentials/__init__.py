from google.oauth2 import service_account

credentials = service_account.Credentials.from_service_account_file(
    "./credentials/credentials.json",
)
