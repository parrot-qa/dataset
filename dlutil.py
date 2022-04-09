import os
import re
import json

import requests
import pandas as pd

from adapters import gdrive, piazza


DATA_DIR = '.cache'


def _setup_dir(collection, course):
    path = os.path.join(DATA_DIR, collection, course)
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def get_material(args):
    if match := re.match(r'https://docs.google.com/(\w+)/d/([-_a-z0-9]+)/', args.uri, re.IGNORECASE):
        file_type = match.group(1)
        if file_type == 'document':
            mime_type = 'text/html'
            extn = '.html'
        else:
            mime_type = 'application/pdf'
            extn = '.pdf'
        file_id = match.group(2)
        text = gdrive.download(file_id, mime_type)
    else:
        resp = requests.get(args.uri)
        resp.raise_for_status()
        if 'text/html' in resp.headers['content-type']:
            extn = '.html'
        elif 'application/pdf' in resp.headers['content-type']:
            extn = '.pdf'
        else:
            raise RuntimeError('Unknown URI type, it was neither Google Drive nor HTML!')
        text = resp.content

    return text, extn


def download_material(args):
    outdir = _setup_dir('materials', args.course)
    text, extn = get_material(args)
    with open(os.path.join(outdir, args.name + extn), 'wb') as fp:
        fp.write(text)


def get_forum(args):
    handle = piazza.login()
    posts = piazza.download_posts(handle, args.class_id)
    return posts


def download_forum(args):
    outdir = _setup_dir('forums', args.course)
    posts = get_forum(args)
    with open(os.path.join(outdir, args.name + '.json'), 'w') as fp:
        json.dump(posts, fp, indent=4)


def download_bulk(args):
    class ArgsWrapper:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)

    course = os.path.basename(args.spec_file).split('.')[0]
    df = pd.read_csv(args.spec_file)
    dup_uri = df.duplicated('uri', keep=False)
    dup_name = df.duplicated('name', keep=False)
    dup_df = df[dup_uri | dup_name]
    if len(dup_df) > 0:
        print('Duplicate entries! Please fix and try again:')
        print(dup_df)
        return

    for _, row in df.iterrows():
        try:
            download_material(ArgsWrapper(course=course, name=row['name'], uri=row['uri']))
            print(f'Completed: {row["name"]}: {row["uri"]}')
        except Exception as e:
            print(f'Failed: {row["name"]}: {row["uri"]}')
            print(f'>', e)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='collection')

    m_parser = subparsers.add_parser('material')
    m_parser.add_argument('course', help='course to which the material belongs')
    m_parser.add_argument('name', help='name of the document to save with')
    m_parser.add_argument('uri', help='document link on HTTP')
    m_parser.set_defaults(func=download_material)

    f_parser = subparsers.add_parser('forum')
    f_parser.add_argument('course', help='course to which the forum belongs')
    f_parser.add_argument('name', help='name of the document to save with')
    f_parser.add_argument('class_id', help='class ID on Piazza')
    f_parser.set_defaults(func=download_forum)

    b_parser = subparsers.add_parser('bulk')
    b_parser.add_argument('spec_file', help='file named <course>.materials.csv, containing name and links')
    b_parser.set_defaults(func=download_bulk)

    args = parser.parse_args()
    args.func(args)
