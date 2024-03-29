from dataclasses import dataclass, field
import re

from bs4 import BeautifulSoup


# To capture code, add the following: |pre|code
VALID_TAGS = re.compile(r'^(?:h\d|p|span|ul|ol|table)$')

DOCUMENT_PARTITION_LENGTH = 100


@dataclass
class Section:
    level: int
    header: str
    contents: list = field(default_factory=list)
    children: list = field(default_factory=list)
    length: int = None

    def compute_length(self):
        length = sum(
            len(c['text']) for c in self.contents
        )

        for child in self.children:
            length += child.compute_length()

        self.length = length
        return length

    def prune_empty(self):
        for child in self.children:
            child.prune_empty()

        self.children = list(filter(lambda child: child.length > 0, self.children))


def _get_root(soup):
    """Find the "root" tag which has the main content."""

    root = None

    if soup.main:
        root = soup.main
    elif soup.header:
        # Some documents don't specify main, so use the next sibling of header tag
        root = soup.header.next_sibling
    elif root := soup.find(attrs={'role': 'main'}):
        # Some documents seem to have a attribute "role" for the main content
        pass
    elif root := soup.find('div', attrs={'class': 'slides'}):
        # Based on CS61A, slide materials
        pass
    elif root := soup.find('div', attrs={'class': 'inner-content'}):
        # Based on CS61A, book materials
        pass

    if root is None:
        raise RuntimeError('Cannot determine location of main content.')

    return root


def _flatten_list(root):
    """ Annotate list items with support for nesting."""

    for item in root.find_all('li'):
        level = len(item.find_parents(['ul', 'ol']))
        item.insert(0, f' {"•" * level} ')

    text = ''.join(root.strings)
    text = re.sub(r'[\s\n]+', ' ', text)
    return text


def _flatten_table(root):
    # TODO: Add markers to denote table rows/columns
    text = ''.join(root.strings)
    text = re.sub(r'[\s\n]+', ' ', text)
    return text


def _standardize_tag(tag):
    if tag in {'ul', 'ol'}:
        return 'list'
    elif tag in {'pre', 'code'}:
        return 'code'
    elif tag == 'table':
        return 'table'
    else:
        return 'plain'


def embed_hierarchy(content):
    """Convert a flat list of headers and paragraphs into a tree of sections."""

    stack = [Section(0, None)]

    for c in content:
        if header := re.match(r'h(\d)', c[0]):
            level = int(header.group(1))
            while stack[-1].level > level:
                stack.pop()
            siblings = []
            idx = len(stack) - 1
            while stack[idx].level == level:
                siblings.append(stack[idx].header)
                idx -= 1
            if c[1] in siblings:
                # Head is already seen at a sibling node, reuse last header
                stack[-1].contents.append({'tag': 'plain', 'text': c[1]})
                continue
            section = Section(level, c[1])
            stack[idx].children.append(section)
            stack.append(section)
        else:
            if len(stack) > 1:
                # Only capture text after the first header
                stack[-1].contents.append({
                    'tag': _standardize_tag(c[0]),
                    'text': c[1]
                })

    stack[0].compute_length()
    stack[0].prune_empty()
    return stack[0]


def partition_docs(node, threshold=DOCUMENT_PARTITION_LENGTH, prefix=[]):
    doc = []
    next_prefix = prefix + [node.header] if node.header else prefix

    self_length = sum(len(c['text']) for c in node.contents)
    if self_length:
        doc.append({'title': ': '.join(next_prefix), 'contents': node.contents})
    if len(node.children) == 0:
        return doc

    if ((self_length > 0 and self_length < threshold) or
            any(child.length < threshold for child in node.children)):
        # Children content is too short to be used individually, merge them
        if len(doc) == 0:
            doc.append({'title': ': '.join(next_prefix), 'contents': []})
        for child in node.children:
            for subdoc in partition_docs(child, prefix=next_prefix):
                if not doc[-1]['title']:
                    # Sometimes the root has no title but multiple children. If so, use the first child's title as document title.
                    doc[-1]['title'] = subdoc['title']
                else:
                    doc[-1]['contents'].append({'tag': 'plain', 'text': subdoc['title']})
                doc[-1]['contents'].extend(subdoc['contents'])
    else:
        for child in node.children:
            doc.extend(partition_docs(child, prefix=next_prefix))

    return doc


def extract_text(path, **partition_args) -> list[dict]:
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
        elif tag.name in {'pre', 'code'}:
            text = ''.join(tag.strings)
        else:
            text = ''.join(tag.strings)
            text = re.sub(r'[\s\n]+', ' ', text)
        if not text:
            continue
        results.append((tag.name, text))

    doctree = embed_hierarchy(results)
    sections = partition_docs(doctree, **partition_args)
    return sections


def extract_text_basic(html):
    soup = BeautifulSoup(html, features='html.parser')
    text = ' '.join(soup.stripped_strings)
    text = re.sub(r'[\s\n]+', ' ', text)
    return text


if __name__ == '__main__':
    with open('playground.html', 'w') as fp:
        fp.write("""
            <main>
            <p>This data should be lost.</p>
            <h1>Project</h1>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
            <h2>Grading</h2>
            <h3>Peer Option</h3>
            <p>Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
            <h3>Tutor Option</h3>
            <p>Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.</p>
            <h2>Submission</h2>
            <p>Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.</p>
            <h3>Timeline</h3>
            <p>...tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat...</p>
            <h3>Breakup</h3>
            <p>15 points.</p>
            </main>
        """)
    sections = extract_text('playground.html', threshold=100)
    assert type(sections) == list

    text = extract_text_basic('<p>\nHello!\n<b> How are you doing? </b>\n</p>')
    assert text == 'Hello! How are you doing?'

    print('All unit tests passed.')
