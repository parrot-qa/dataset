import os
import json
import glob

from common import DATA_DIR, setup_dir, read_spec, validate_spec, ArgsWrapper
from parsers import html, pdf, piazza


def parse_material(args):
    outdir = setup_dir('documents', args.course)

    infiles = glob.glob(os.path.join(DATA_DIR, 'materials', args.course, f'{glob.escape(args.name)}.*'))
    if len(infiles) == 1:
        extn = infiles[0].split('.')[-1]
        if extn == 'pdf':
            spans = pdf.extract_text(infiles[0])
        elif extn == 'html':
            spans = html.extract_text(infiles[0])
        else:
            raise ValueError(f'No parser available for material type "{extn}".')
    elif len(infiles) == 0:
        raise RuntimeError('Could not find material, run dlutil first.')
    else:
        raise RuntimeError('Multiple materials found, please remove duplicates.')

    with open(os.path.join(outdir, f'{args.name}.json'), 'w') as fp:
        json.dump(spans, fp, indent=4)


def parse_forum(args):
    outdir = setup_dir('qa_pairs', args.course)

    infiles = glob.glob(os.path.join(DATA_DIR, 'forums', args.course, f'{glob.escape(args.name)}.*'))
    if len(infiles) == 1:
        extn = infiles[0].split('.')[-1]
        if extn == 'json':
            pairs = piazza.extract_qa(infiles[0])
        else:
            raise ValueError(f'No parser available for forum type "{extn}".')
    elif len(infiles) == 0:
        raise RuntimeError('Could not find forum, run dlutil first.')
    else:
        raise RuntimeError('Multiple forums found, please remove duplicates.')

    with open(os.path.join(outdir, f'{args.name}.json'), 'w') as fp:
        json.dump(pairs, fp, indent=4)


def parse_bulk(args):
    course, collection, df = read_spec(args.spec_file)
    if collection == 'materials':
        parse_fn = parse_material
    elif collection == 'forums':
        parse_fn = parse_forum
    else:
        raise RuntimeError('Unknown collection, should be one of: materials, forums')

    if validate_spec(df) == False:
        return

    for _, row in df.iterrows():
        try:
            parse_fn(ArgsWrapper(course=course, name=row['name']))
            print(f'Completed: {row["name"]}')
        except Exception as e:
            print(f'Failed: {row["name"]}')
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
