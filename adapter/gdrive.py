import re
import json
from urllib.error import HTTPError

import requests


def _read_api_key():
    with open('.secrets/config.json', 'r') as fp:
        conf = json.load(fp)
        return conf['google_drive_api_key']


GOOGLE_DRIVE_API_URL = 'https://www.googleapis.com/drive/v3'
GOOGLE_DRIVE_API_KEY = _read_api_key()

FILE_ID_PATTERN = re.compile(r'^[-_a-z0-9]+$', re.IGNORECASE)
MIME_TYPE_OPTIONS = ['application/pdf', 'application/json', 'text/html']


def download(file_id, mime_type):
    if not FILE_ID_PATTERN.match(file_id):
        raise ValueError(f'Invalid file ID: Must match pattern {FILE_ID_PATTERN.pattern}')

    if mime_type not in MIME_TYPE_OPTIONS:
        raise ValueError(f'Invalid mime type: Must be one of {", ".join(MIME_TYPE_OPTIONS)}')

    url = f'{GOOGLE_DRIVE_API_URL}/files/{file_id}/export'
    resp = requests.get(url, {'mimeType': mime_type, 'key': GOOGLE_DRIVE_API_KEY})
    if resp.ok:
        return resp.content
    else:
        # Create new instance of error that includes response JSON in message
        raise HTTPError(resp.url, resp.status_code, resp.json(), resp.headers, None)


if __name__ == '__main__':
    # Unit test: Valid file
    doc = download('1b8V53ddjN9GCCSDB2e-EKtPQpl3N_xCkMOj_cgvJGPI', 'application/pdf')
    assert doc != None

    # Unit test: File ID pattern is invalid
    try:
        doc = download('random file', 'application/pdf')
    except ValueError:
        pass

    # Unit test: File does not exist
    try:
        doc = download('invalid_file_id', 'application/pdf')
    except HTTPError as e:
        assert e.code == 404

    print('All unit tests passed.')
