import json
import os
import re

from pymongo import MongoClient
from pymongo.server_api import ServerApi


def _read_license_path():
    with open('.secrets/config.json', 'r') as fp:
        conf = json.load(fp)
        return os.path.join('.secrets', conf['mongodb_license'])


MONGO_DB_BASE_URL = 'mongodb+srv://parrot-qa-cluster-0.1ecao.mongodb.net'
MONGO_DB_LICENSE_PATH = _read_license_path()

DB_NAME_PATTERN = re.compile(r'^[-_a-z0-9]+$', re.IGNORECASE)

COURSES_SCHEMA = {
    'name': 'courses',
    'schema': {
        'bsonType': 'object',
        'required': ['name', 'uri'],
        'properties': {
            'name': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'uri': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            }
        }
    },
    'index': 'name'
}

MATERIALS_SCHEMA = {
    'name': 'materials',
    'schema': {
        'bsonType': 'object',
        'required': ['course', 'uri', 'type', 'raw'],
        'properties': {
            'course': {
                'bsonType': 'objectId',
                'description': 'must be an ObjectId and is required'
            },
            'uri': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'type': {
                'enum': ['html', 'pdf', 'docx', 'pptx', 'xlsx', 'csv', 'tsv'],
                'description': 'must be one of valid document types'
            },
            'raw': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            }
        }
    },
    'index': 'uri'
}

FORUMS_SCHEMA = {
    'name': 'forums',
    'schema': {
        'bsonType': 'object',
        'required': ['course', 'uri', 'type', 'raw'],
        'properties': {
            'course': {
                'bsonType': 'objectId',
                'description': 'must be an ObjectId and is required'
            },
            'uri': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            },
            'type': {
                'enum': ['piazza'],
                'description': 'must be one of valid document types'
            },
            'raw': {
                'bsonType': 'string',
                'description': 'must be a string and is required'
            }
        }
    },
    'index': 'uri'
}


def connect(db_name='test'):
    if not DB_NAME_PATTERN.match(db_name):
        raise ValueError('Database name is invalid.')

    uri = f'{MONGO_DB_BASE_URL}/{db_name}?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority'
    m = MongoClient(uri, tls=True, tlsCertificateKeyFile=MONGO_DB_LICENSE_PATH, server_api=ServerApi('1'))
    return m.get_database()


def create_collection(db, schema):
    coll = db.create_collection(
        schema['name'],
        validator={'$jsonSchema': schema['schema']}
    )
    coll.create_index(schema['index'], unique=True)
    return coll


if __name__ == '__main__':
    from pymongo.database import Database
    db = connect('test')
    assert type(db) == Database

    print('All unit tests passed.')
