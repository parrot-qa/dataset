import os
import json
import glob
import re

import pandas as pd

from common import DATA_DIR, MIN_DOCUMENT_TOKEN_COUNT
from common import setup_dir, read_spec, validate_spec, ArgsWrapper
from parsers import html, pdf, piazza


def validate_qa(pair):
    stu_ans = pair.get('student_answer')
    ins_ans = pair.get('instructor_answer')
    if type(stu_ans) != str or type(ins_ans) != str:
        raise RuntimeError(f'Post @{pair["tag_num"]}: Student/instructor answers should be strings.')
    if (stu_ans + ins_ans) == '':
        raise RuntimeError(f'Post @{pair["tag_num"]}: Both student and instructor answers are empty/missing.')


def validate_qa_list(pairs):
    if len(pairs) == 0:
        raise RuntimeError('QA pairs are empty.')

    qa_df = pd.DataFrame.from_records(pairs)
    dup_df = qa_df.loc[qa_df['tag_num'].duplicated(keep=False)]
    if len(dup_df) > 0:
        print('\n', dup_df[['id', 'tag_num']])
        raise RuntimeError('Duplicate tags in QA pairs.')


def validate_doc(doc):
    if not doc.get('title', '').strip():
        raise RuntimeError('Document title is empty or missing.')

    paras = [c['text'] for c in doc['contents']]
    text = ' '.join(paras)
    tokens = re.split(r'\s+', text)
    if len(tokens) < MIN_DOCUMENT_TOKEN_COUNT:
        raise ValueError(f'Document text is too short: Minimum {MIN_DOCUMENT_TOKEN_COUNT} words expected.')


def validate_doc_list(docs):
    if len(docs) == 0:
        raise RuntimeError('Documents are empty.')

    doc_df = pd.DataFrame.from_records(docs)
    dup_df = doc_df.loc[doc_df['title'].duplicated(keep=False)]
    if len(dup_df) > 0:
        print('\n', dup_df[['material_name', 'title']])
        raise RuntimeError('Duplicate titles in documents.')


def parse_material(args):
    outdir = setup_dir('documents', args.course)

    infiles = glob.glob(os.path.join(DATA_DIR, 'materials', args.course, f'{glob.escape(args.name)}.*'))
    if len(infiles) == 1:
        extn = infiles[0].split('.')[-1]
        if extn == 'pdf':
            spans = pdf.extract_text(infiles[0], **getattr(args, 'pflags', {}))
        elif extn == 'html':
            spans = html.extract_text(infiles[0], **getattr(args, 'pflags', {}))
        else:
            raise ValueError(f'No parser available for material type "{extn}".')
    elif len(infiles) == 0:
        raise RuntimeError('Could not find material, run dlutil first.')
    else:
        raise RuntimeError('Multiple materials found, please remove duplicates.')

    if len(spans) == 0:
        raise RuntimeError('No text found by parser.')

    for span in spans:
        validate_doc(span)
        # Add meta data to spans
        span['material_name'] = args.name
        span['material_type'] = extn

    with open(os.path.join(outdir, f'{args.name}.json'), 'w') as fp:
        json.dump(spans, fp, indent=4)

    return spans


def parse_forum(args):
    outdir = setup_dir('qa_pairs', args.course)

    infiles = glob.glob(os.path.join(DATA_DIR, 'forums', args.course, f'{glob.escape(args.name)}.*'))
    if len(infiles) == 1:
        extn = infiles[0].split('.')[-1]
        if extn == 'json':
            pairs = piazza.extract_qa(infiles[0], **getattr(args, 'pflags', {}))
        else:
            raise ValueError(f'No parser available for forum type "{extn}".')
    elif len(infiles) == 0:
        raise RuntimeError('Could not find forum, run dlutil first.')
    else:
        raise RuntimeError('Multiple forums found, please remove duplicates.')

    for pair in pairs:
        validate_qa(pair)

    with open(os.path.join(outdir, f'{args.name}.json'), 'w') as fp:
        json.dump(pairs, fp, indent=4)

    return pairs


def parse_bulk(args):
    course, collection, df = read_spec(args.spec_file)
    if collection == 'materials':
        parse_fn = parse_material
        validate_fn = validate_doc_list
    elif collection == 'forums':
        parse_fn = parse_forum
        validate_fn = validate_qa_list
    else:
        raise RuntimeError('Unknown collection, should be one of: materials, forums')

    if validate_spec(df) == False:
        return

    suc = 0
    records = []
    for _, row in df.iterrows():
        try:
            if 'pflags' in row and not pd.isnull(row['pflags']):
                pflags = json.loads(row['pflags'])
            else:
                pflags = {}
            records.extend(
                parse_fn(ArgsWrapper(course=course, name=row['name'], pflags=pflags))
            )
            print(f'Completed: {row["name"]}')
            suc += 1
        except Exception as e:
            print(f'Failed: {row["name"]}')
            print(f'>', e)

    print(f'\nCompleted {suc}/{len(df)} successfully. Records generated: {len(records)}')
    try:
        validate_fn(records)
    except Exception as e:
        print('\nWARNING: Parsed data has issues!')
        print(f'>', e)


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='collection')

    m_parser = subparsers.add_parser('material')
    m_parser.add_argument('course', help='course to which the material belongs')
    m_parser.add_argument('name', help='name of the document to parse')
    m_parser.set_defaults(func=parse_material)

    f_parser = subparsers.add_parser('forum')
    f_parser.add_argument('course', help='course to which the forum belongs')
    f_parser.add_argument('name', help='name of the document to parse')
    f_parser.set_defaults(func=parse_forum)

    b_parser = subparsers.add_parser('bulk')
    b_parser.add_argument('spec_file', help='file named <course>.<collection>.csv, containing name, links, etc.')
    b_parser.set_defaults(func=parse_bulk)

    args = parser.parse_args()
    args.func(args)
