import os
import json
import glob

import pandas as pd

from parsers import html, pdf, piazza


DATA_DIR = '.cache'


def _setup_dir(collection, course):
    path = os.path.join(DATA_DIR, collection, course)
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def get_files(args):
    files = glob.glob(os.path.join(args.dir, '*', '*.*'), recursive=False)
    meta = []
    for f in files:
        parts = f.split(os.sep)
        meta.append([parts[-2], parts[-1], f])
    return pd.DataFrame(meta, columns=['Course', 'File', 'Path'])


def extract_documents(args):
    df = get_files(args)
    for _, row in df.iterrows():
        try:
            outdir = _setup_dir('documents', row['Course'])
            name = row['File'].split('.')[0]
            extn = row['File'][len(name):]
            if extn == '.pdf':
                spans = pdf.extract_text(row['Path'])
            elif extn == '.html':
                spans = html.extract_text(row['Path'])
            else:
                raise ValueError('No parser available for material:', row['Path'])
            with open(os.path.join(outdir, f'{name}.json'), 'w') as fp:
                json.dump(spans, fp, indent=4)
            print(f'Completed: {row["Path"]}')
        except Exception as e:
            print(f'Failed: {row["Path"]}')
            print(f'>', e)


def extract_qa_pairs(args):
    df = get_files(args)
    for _, row in df.iterrows():
        try:
            outdir = _setup_dir('qa_pairs', row['Course'])
            name = row['File'].split('.')[0]
            extn = row['File'][len(name):]
            if extn == '.json':
                pairs = piazza.extract_qa(row['Path'])
            else:
                raise ValueError('No parser available for forum:', row['Path'])
            with open(os.path.join(outdir, f'{name}.json'), 'w') as fp:
                json.dump(pairs, fp, indent=4)
            print(f'Completed: {row["Path"]}')
        except Exception as e:
            print(f'Failed: {row["Path"]}')
            print(f'>', e)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='collection')

    d_parser = subparsers.add_parser('documents')
    d_parser.add_argument('dir', help='folder containing materials')
    d_parser.set_defaults(func=extract_documents)

    q_parser = subparsers.add_parser('qa_pairs')
    q_parser.add_argument('dir', help='folder containing forums')
    q_parser.set_defaults(func=extract_qa_pairs)

    args = parser.parse_args()
    args.func(args)
