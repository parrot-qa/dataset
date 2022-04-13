import re

from bs4 import BeautifulSoup


VALID_TAGS = re.compile(r'^(?:h\d|p|span|ul|ol|pre|code|table)$')


def _get_root(soup):
    """Find the "root" tag which has the main content."""

    if soup.main:
        root = soup.main
    elif soup.header:
        # Some documents don't specify main, so use the next sibling of header tag
        root = soup.header.next_sibling
    else:
        # Some documents seem to have a attribute "role" for the main content
        root = soup.find(attrs={'role': 'main'})

    if root is None:
        raise RuntimeError('Cannot determine location of main content.')

    return root


def _flatten_list(root):
    """ Annotate list items with support for nesting."""

    for item in root.find_all('li'):
        level = len(item.find_parents(['ul', 'ol']))
        item.insert(0, f' {"•" * level} ')

    text = ''.join(root.strings)
    text = re.sub('[\s\n]+', ' ', text)
    return text


def _flatten_table(root):
    # TODO: Add markers to denote table rows/columns
    text = ''.join(root.strings)
    text = re.sub('[\s\n]+', ' ', text)
    return text


def categorize_documents(content, prefix=None, max_depth=6):
    """Convert a flat list of headers and paragraphs into titled documents."""

    docs = []

    stack = [prefix] if prefix else []
    level = []
    for c in content:
        h = re.match(rf'h([1-{max_depth}])', c[0])
        if h:
            h = int(h.group(1))
            while len(level) and level[-1] >= h:
                stack.pop()
                level.pop()
            stack.append(c[1])
            level.append(h)
        else:
            if len(stack) == 0:
                # Don't capture text before the first heading
                continue
            docs.append((tuple(stack), *c))

    return docs


def format_documents(sections):
    parts = []

    last_title = None
    for title, tag, text in sections:
        if title != last_title:
            parts.append({'title': ' '.join(title), 'contents': []})
            last_title = title

        if tag in {'ul', 'ol'}:
            ptag = 'list'
        elif tag in {'pre', 'code'}:
            ptag = 'code'
        elif tag == 'table':
            ptag = 'table'
        else:
            ptag = 'plain'
        parts[-1]['contents'].append({'tag': ptag, 'text': text})

    return parts


def extract_text(path, *args, **kwargs) -> list[dict]:
    """Take a file path as input, and return a list of text with headings."""

    with open(path, 'r', encoding='utf-8') as fp:
        html = fp.read()

    soup = BeautifulSoup(html, features='html.parser')
    root = _get_root(soup)

    def most_ancestral_tag(tag):
        name_valid = VALID_TAGS.search(tag.name) is not None
        parent_valid = tag.find_parent(VALID_TAGS) is None  # Ensures text is not already captured by some ancestor
        return name_valid and parent_valid

    results = []
    for tag in root.find_all(most_ancestral_tag):
        if tag.name in {'ul', 'ol'}:
            text = _flatten_list(tag)
        elif tag.name == 'table':
            text = _flatten_table(tag)
        else:
            text = ''.join(tag.strings)
        if not text:
            continue
        results.append((tag.name, text))

    sections = categorize_documents(results, max_depth=2)
    sections = format_documents(sections)
    return sections


if __name__ == '__main__':
    sections = extract_text('.cache/materials/DS100/1_1__The_Students_of_Data_100.html')
    assert type(sections) == list
