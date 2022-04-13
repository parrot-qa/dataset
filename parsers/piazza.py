
from html import extract_text_basic
import json


def extract_question_posts(post_list):
    questions = []
    for post in post_list:
        if post.get("type") == "question":
            questions.append(post)
    return questions


def get_answers(post):
    instructor_answer = ""
    student_answer = ""
    children_posts = post.get("children")
    for child in children_posts:
        if child.get("type") == "i_answer":
            instructor_answer = child.get("history")[-1].get("content")
        if child.get("type") == "s_answer":
            student_answer = child.get("history")[-1].get("content")
    return instructor_answer, student_answer


def get_question_content(post):
    return post.get("history")[-1].get("content")


def get_subject(post):
    return post.get("history")[-1].get("subject")


def extract_qa(path, *args, **kwargs) -> list[dict]:
    """Take a file path as input, and return a list of question-answers."""
    f1 = open(path)
    raw_QA = json.load(f1)
    f1.close()

    answered_questions = extract_question_posts(raw_QA)
    formatted_QA = []
    for post in answered_questions:
        i_answer, s_answer = get_answers(post)
        post_dict = {"id": post.get("id"),
                     "subject": get_subject(post),
                     "content": get_question_content(post),
                     "student_answer": s_answer,
                     "instructor_answer": i_answer,
                     "folders": post.get("folders")}
        formatted_QA.append(post_dict)

    return formmated_QA


if __name__ == '__main__':
    print('Write any tests or debugging code here.')
