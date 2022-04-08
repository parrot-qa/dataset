# Database schema

We will use MongoDB for our database needs. MongoDB being no-SQL natively supports JSON structured documents, which will make it straightfoward to import/export data locally as needed.

In MongoDB, documents are grouped and stored in "collections", which are equivalent to tables in a traditional RDBMS sense. For more details, see: https://www.mongodb.com/docs/manual/core/databases-and-collections/

## Courses

This collection stores data about the courses that are present in the dataset. This can be used, for example, to filter documents by relevant course during training.

```jsonc
[
    {
        "_id": "11111111",  // [auto-generated]
        "name": "DS100",    // [unique]
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
        "_id": "22222222",                                       // [auto-generated]
        "course": "ObjectId(11111111)",                          // [foreign key]
        "name": "",                                              // [optional]
        "uri": "https://ds100.org/fa21/grad_proj/gradproject/",  // [unique]
        "type": "html",                                          // [html|pdf|ppt]
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
        "_id": "33333333",                     // [auto-generated]
        "material": "ObjectId(22222222)",      // [foreign key]
        "title": "Graduate Project\nRubrics",  // [unique], \n separated if hierarchial
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

## Forums

This collection stores the raw data for question-answers, collected from forums such as Piazza.

```jsonc
[
    {
        "_id": "44444444",                                // [auto-generated]
        "course": "ObjectId(11111111)",                   // [foreign key]
        "uri": "https://piazza.com/class/ksqyjn4qfo7c5",  // [unique]
        "type": "piazza",                                 // [piazza|<future_extensions>]
        "raw": "[{\"folders\": [\"logistics\", \"other\"], \"nr\": 1421, \"created\": \"2019-12-30T23:20:16Z\", \"bucket_order\": 0, \"no_answer_followup\": 0}]"
    }
    // ...
]
```

## Question-Answers

```jsonc
[
    {
        "course": "ObjectId(44444444)",                          // [Course ref]
        "_id": "55555555",                                       // [Piazza ID code, unique]
        "subject": "Regrade submissions did not go through",     // [Subject line of Piazza Post]
        "content": "Hey! I've noticed that my regrade..",        // [Parsed text of the question]
        "student_answer": "",                                    // [Either contains parsed text answer or empty]
        "instructor_answer": "Will look into it and...",         // [Either contains parsed text answer or empty]
        "folder" : ["other"]                                     // [The folder that the student put the question in]
    },
    // ...
]
```

# dataset

- https://inst.eecs.berkeley.edu/~cs61a/fa21/
- https://sp21.datastructur.es/
- https://ds100.org/fa21/
