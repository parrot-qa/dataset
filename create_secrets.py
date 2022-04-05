import os
import json
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('gkey', help='Google Drive API key. For more details, refer: https://developers.google.com/drive/api/quickstart/python')
parser.add_argument('mlicense', help='path to the MongoDB license file. For more details, refer: https://www.mongodb.com/docs/manual/tutorial/configure-x509-client-authentication')

args = parser.parse_args()

# Create the secrets folder
if not os.path.isdir('.secrets'):
    os.mkdir('.secrets')

# Copy MongoDB license
mlicense_name = os.path.basename(args.mlicense)
os.replace(args.mlicense, os.path.join('.secrets', mlicense_name))

# Create config file
config = {
    "google_drive_api_key": args.gkey,
    "mongodb_license": mlicense_name
}
with open(os.path.join('.secrets', 'config.json'), 'w') as fp:
    json.dump(config, fp, indent=4)

print('Secrets successfully created.')
