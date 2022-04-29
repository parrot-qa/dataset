import os
import json
import glob
import re

import pandas as pd

from common import DATA_DIR, read_spec, validate_spec


def collate_document(doc, skip=['code']):
    """Collate a document JSON containing sections into a single string."""
    text = [sec['text'] for sec in doc['contents']
            if sec['tag'] not in skip]
    title = doc['title']
    return title, ' '.join(text)


def collate_answers(pair):
    answers = [pair['student_answer'], pair['instructor_answer']]
    scores = [pair['student_answer_thanks_count'], pair['instructor_answer_thanks_count']]

    records = {
        'a_id': [],
        'text': [],
        'score': []
    }
    for i in range(len(answers)):
        if answers[i] == '':
            continue
        else:
            records['a_id'].append(pair["id"] + str(i + 1))
            records['text'].append(answers[i])
            records['score'].append(scores[i] + 1)

    return records


def collate_course(meta):
    course = meta.name

    qa_pairs = []
    for fname in meta['forums']:
        ffile = os.path.join(DATA_DIR, 'qa_pairs', course, f'{fname}.json')
        try:
            with open(ffile) as fp:
                for pair in json.load(fp):
                    qa_pairs.append({
                        'q_id': pair['id'],
                        'title': f'{pair["subject"]} . {pair["content"]}',
                        'answers': collate_answers(pair),
                        'course': course,
                        'tags': pair['folders'],
                        'is_answerable': pair['is_answerable']
                    })
        except Exception as e:
            print(f'Aborting forum midway due to error: {course} {fname}')
            print(' >', e)

    documents = []
    for mname in meta['materials']:
        mfile = os.path.join(DATA_DIR, 'documents', course, f'{mname}.json')
        try:
            with open(mfile) as fp:
                for doc in json.load(fp):
                    title, text = collate_document(doc)
                    documents.append({
                        'course': course,
                        'article_title': title,
                        'section_title': '',
                        'passage_text': text,
                        'source_type': doc['material_type']
                    })
        except Exception as e:
            print(f'Aborting document midway due to error: {course} {mname}')
            print(' >', e)

    return qa_pairs, documents


def display_stats(qa_pairs, documents):
    qa_df = pd.DataFrame(qa_pairs)
    doc_df = pd.DataFrame(documents)

    qa_stat = qa_df.groupby('course').agg({'title': 'count', 'is_answerable': 'sum'})
    qa_stat.columns = ['count', 'answerable']

    doc_stat = doc_df.groupby('course').agg({'passage_text': 'count'})
    doc_stat.columns = ['count']

    stat = qa_stat.join(doc_stat, lsuffix='_qa', rsuffix='_doc', how='outer')
    stat = stat.fillna(0).astype(int)
    print('\n', stat)


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
        qa, docs = collate_course(row)
        qa_pairs.extend(qa)
        documents.extend(docs)

    db_file = os.path.join(DATA_DIR, 'parrot-qa.json')
    with open(db_file, 'w') as fp:
        json.dump({
            'qa_pairs': qa_pairs,
            'documents': documents
        }, fp, indent=4)
        print(f'\nGenerated dataset in: {db_file}')
        display_stats(qa_pairs, documents)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('spec_dir', help='folder containing specification files named <course>.<collection>.csv')
    parser.add_argument('--course', help='regex to filter by course name', default=r'.*')
    parser.set_defaults(func=export_dataset)

    args = parser.parse_args()
    args.func(args)
