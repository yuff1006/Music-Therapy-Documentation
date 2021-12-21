import os

email_address = os.environ.get('GG_USER')
email_password = os.environ.get('GG_PASS')

print(email_address, email_password)