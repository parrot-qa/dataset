import os
import json
import glob
import re

import pandas as pd

from common import DATA_DIR, read_spec, validate_spec


def validate_qa(p):
    pass


def validate_doc(d):
    if not d.get('title', ''):
        raise RuntimeError('Document title is empty or missing.')


def collate_document(doc, skip=['code']):
    """Collate a document JSON containing sections into a single string."""
    text = [sec['text'] for sec in doc['contents']
            if sec['tag'] not in skip]
    title = doc['title']
    return title, ' '.join(text)


def collate_course(meta):
    course = meta.name

    qa_pairs = []
    for fname in meta['forums']:
        ffile = os.path.join(DATA_DIR, 'qa_pairs', course, f'{fname}.json')
        try:
            with open(ffile) as fp:
                for pair in json.load(fp):
                    validate_qa(pair)
                    pair['course'] = course
                    qa_pairs.append(pair)
        except Exception as e:
            print(f'Skipping forum due to error: {course} {fname}')
            print(' >', e)

    documents = []
    for mname in meta['materials']:
        mfile = os.path.join(DATA_DIR, 'documents', course, f'{mname}.json')
        try:
            with open(mfile) as fp:
                for doc in json.load(fp):
                    validate_doc(doc)
                    title, text = collate_document(doc)
                    documents.append({
                        'course': course,
                        'title': title,
                        'content': text
                    })
        except Exception as e:
            print(f'Skipping document due to error: {course} {mname}')
            print(' >', e)

    return qa_pairs, documents


def export_dataset(args):
    spec_files = glob.glob(os.path.join(args.spec_dir, '*.*.csv'), recursive=False)
    meta_df = []
    for f in spec_files:
        course, collection, contents = read_spec(f)
        if re.search(args.course, course) is None:
            continue
        if validate_spec(contents) == False:
            return
        meta_df.append([course, collection, contents['name'].to_list()])

    meta_df = pd.DataFrame(meta_df, columns=['Course', 'Collection', 'Files'])
    meta_df = meta_df.pivot(index='Course', columns='Collection', values='Files')
    if meta_df.isna().any(axis=None):
        print('Error: Either forum or document spec missing for some courses!')
        print(meta_df)
        return

    qa_pairs = []
    documents = []
    for _, row in meta_df.iterrows():
        q, d = collate_course(row)
        qa_pairs.extend(q)
        documents.extend(d)

    db_file = os.path.join(DATA_DIR, 'parrot-qa.json')
    with open(db_file, 'w') as fp:
        json.dump({
            'qa_pairs': qa_pairs,
            'documents': documents
        }, fp)
        print(f'Generated dataset in: {db_file}')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('spec_dir', help='folder containing specification files named <course>.<collection>.csv')
    parser.add_argument('--course', help='regex to filter by course name', default=r'.*')
    parser.set_defaults(func=export_dataset)

    args = parser.parse_args()
    args.func(args)
