import os
import re
import json

import requests

from common import setup_dir, read_spec, validate_spec, ArgsWrapper
from adapters import gdrive, piazza


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
        text = gdrive.download(file_id, mime_type, **getattr(args, 'dlflags', {}))
    else:
        resp = requests.get(args.uri, **getattr(args, 'dlflags', {}))
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
    outdir = setup_dir('materials', args.course)
    text, extn = get_material(args)
    with open(os.path.join(outdir, args.name + extn), 'wb') as fp:
        fp.write(text)


def get_forum(args):
    if m := re.match(r'https://piazza\.com/class/(\w+)$', args.uri, re.IGNORECASE):
        class_id = m.group(1)
        handle = piazza.login()
        posts = piazza.download_posts(handle, class_id, **getattr(args, 'dlflags', {}))
        return posts
    else:
        raise RuntimeError('Unknown URI type, only Piazza links are supported currently.')


def download_forum(args):
    outdir = setup_dir('forums', args.course)
    posts = get_forum(args)
    with open(os.path.join(outdir, args.name + '.json'), 'w') as fp:
        json.dump(posts, fp, indent=4)


def download_bulk(args):
    course, collection, df = read_spec(args.spec_file)
    if collection == 'materials':
        download_fn = download_material
    elif collection == 'forums':
        download_fn = download_forum
    else:
        raise RuntimeError('Unknown collection, should be one of: materials, forums')

    if validate_spec(df) == False:
        return

    for _, row in df.iterrows():
        try:
            dlflags = json.loads(row['dlflags']) if 'dlflags' in row else {}
            download_fn(ArgsWrapper(course=course, name=row['name'], uri=row['uri'], dlflags=dlflags))
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
    f_parser.add_argument('uri', help='link to forums (Piazza class)')
    f_parser.set_defaults(func=download_forum)

    b_parser = subparsers.add_parser('bulk')
    b_parser.add_argument('spec_file', help='file named <course>.<collection>.csv, containing name, links, etc.')
    b_parser.set_defaults(func=download_bulk)

    args = parser.parse_args()
    args.func(args)
