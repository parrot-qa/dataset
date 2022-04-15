"""
Format for documents:
---------------------

Each document can be divided into sub-documents based on high-level headings.
Each sub-documents can be divided into paragraphs or sections, with optional tags.

E.g., consider the following HTML:

<h1>Heading 1</h1>
    <p>Lorem ipsum dolor sit amet</p>
    <table>consectetur adipiscing elit</table>
<h2>Heading 2</h2>
    <p>sed do eiusmod tempor incididunt ut labore et dolore magna aliqua</p>

This should parsed as follows:

[
    {
        'title': 'Heading 1',
        'contents': [
            {
                'tag': 'plain',
                'text': 'Lorem ipsum dolor sit amet'
            },
            {
                'tag': 'table',
                'text': 'consectetur adipiscing elit'
            }
        ]
    },
    {
        'title': 'Heading 2',
        'contents': [
            {
                'tag': 'plain',
                'text': 'sed do eiusmod tempor incididunt ut labore et dolore magna aliqua'
            }
        ]
    }
]


Format for QA pairs:
--------------------

From each Piazza JSON, the extracted QA pairs must be formatted as follows:

[
    {
        'subject': 'Subject line of Piazza Post',
        'content': 'Parsed text of the question',
        'student_answer': 'Either contains parsed text answer or empty',
        'instructor_answer': 'Either contains parsed text answer or empty',
        'tags' : ['coding1', 'logistics']
    },
    // ...
]

"""
