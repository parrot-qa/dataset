import os
import re
import json

import requests

from adapter import gdrive, piazza


DATA_DIR = '.cache'


def _setup_dir(collection, course):
    path = os.path.join(DATA_DIR, collection, course)
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def download_material(args):
    outdir = _setup_dir('materials', args.course)

    if match := re.match(r'https://docs.google.com/(\w+)/d/([-_a-z0-9]+)/', args.uri, re.IGNORECASE):
        file_type = match.group(1)
        file_id = match.group(2)
        text = gdrive.download(file_id, 'application/pdf')
        extn = '.pdf'
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

    with open(os.path.join(outdir, args.name + extn), 'wb') as fp:
        fp.write(text)


def download_forum(args):
    outdir = _setup_dir('forums', args.course)
    handle = piazza.login()
    posts = piazza.download_posts(handle, args.class_id)
    with open(os.path.join(outdir, args.name + '.json'), 'w') as fp:
        json.dump(posts, fp)


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

    args = parser.parse_args()
    args.func(args)
