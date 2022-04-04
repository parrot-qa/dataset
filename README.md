# Database schema

## Courses

This collection stores data about the courses that are present in the dataset. This can be used, for example, to filter documents by relevant course during training.

```jsonc
[
    {
        "_id": "", // [auto-generated]
        "name": "DS100", // [unique]
        "uri": "https://ds100.org/fa21/",
        // [optional] other meta data, licenses, etc.
    },
    // ...
]
```

## Materials

This collection stores all information pertaining to raw documents: HTML files, PDFs, PPTs, etc. Each material is linked to its course, and holds the raw original content for reference.

```jsonc
[
    {
        "_id": "", // [auto-generated]
        "course": "DS100", // [foreign key]
        "name": "", // [optional]
        "uri": "https://ds100.org/fa21/grad_proj/gradproject/", // [unique]
        "type": "html", // [html|pdf|ppt]
        "raw": "<!DOCTYPE html>\n<html lang=\"en-US\">\n<head>\n  <meta charset=\"UTF-8\">\n <title>Graduate Project - Data 100</title>\n\n ..."
    },
    // ...
]
```

## Documents

This collection stores documents in a generic format that is most relevant for model training. Each document is titled and sectioned with tags, to allow flexible customization during pre-processing.

```jsonc
[
    {
        "_id": "", // [auto-generated]
        "material": "https://ds100.org/fa21/grad_proj/gradproject/", // [foreign key]
        "title": "Graduate Project\nRubrics", // [unique], \n separated if hierarchial
        "contents": [
            {
                "tags": "plain", // [code|table|list|plain]
                "text": "Each group will peer grade the projects from another group. The review will be graded out of a total of 15 points."
            },
            {
                "tags": "list",
                "text": "• A summary of the report (5 points). The summary should address at least the following: •• What research question does the group propose? Why is it important?"
            }
            // ...
        ]
    }
    // ...
]
```

## Question-Answers

TODO: @97emilylc

# dataset

- https://inst.eecs.berkeley.edu/~cs61a/fa21/
- https://sp21.datastructur.es/
- https://ds100.org/fa21/
