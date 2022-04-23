import os

import pandas as pd


DATA_DIR = '.cache'

MIN_DOCUMENT_TOKEN_COUNT = 10


class ArgsWrapper:
    """Wrap (key, value) arguments into properties."""

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def setup_dir(collection, course):
    path = os.path.join(DATA_DIR, collection, course)
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def read_spec(path):
    course, collection, _ = os.path.basename(path).split('.')
    df = pd.read_csv(path)
    return course, collection, df


def validate_spec(df):
    dup_uri = df.duplicated('uri', keep=False)
    dup_name = df.duplicated('name', keep=False)
    dup_df = df[dup_uri | dup_name]
    if len(dup_df) > 0:
        print('Duplicate entries! Please fix and try again:')
        print(dup_df)
        return False
    else:
        return True
