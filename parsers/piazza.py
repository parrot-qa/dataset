from os import link
from .html import extract_text_basic
import json
import re

def get_question_tags(posts):
    question_numbers = []
    for post in posts:
        question_numbers.append(int(post.get("tag_num")))
    return question_numbers

def trace_back_check(formatted_QA, rawQA):
    question_tag_numbers = get_question_tags(formatted_QA)
    for post in formatted_QA:
        student_answer = post.get("student_answer")         # the current post's student answer
        instructor_answer = post.get("instructor_answer")   # the current post's instructor answer
        if "@" in student_answer: 
            index = student_answer.index("@")
            if student_answer[index+1].isnumeric():
                link_val = re.search('\@(\d*)', student_answer)[1]
                if link_val in question_tag_numbers:
                    for post_sub in formatted_QA:
                        if post_sub.get("tag_num") == link_val:
                            if post_sub.get("student_answer") != "":
                                post["student_answer"] = post_sub.get("student_answer")
                            else:
                                post["student_answer"] = post_sub.get("instructor_answer")
                else:
                    for note in rawQA:
                        if note.get("nr") == link_val:
                            post["student_answer"] = note.get("children")[-1].get("history")[-1].get("content")
        if "@" in instructor_answer: 
            index = instructor_answer.index("@")
            if instructor_answer[index+1].isnumeric():
                link_val = re.search('@\d*', instructor_answer)[0]
                for post_sub in formatted_QA:
                    if post_sub.get("tag_num") == int(link_val[1:]):
                        if post_sub.get("instuctor_answer") != "":
                            post["instructor_answer"] = post_sub.get("instuctor_answer")
    return formatted_QA


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
                     "tag_num": post.get("nr"),
                     "subject": get_subject(post),
                     "content": extract_text_basic(get_question_content(post)),
                     "student_answer": extract_text_basic(s_answer),
                     "instructor_answer": extract_text_basic(i_answer),
                     "folders": post.get("folders")}
        formatted_QA.append(post_dict)
    final_QA = trace_back_check(formatted_QA, raw_QA)
    return final_QA


if __name__ == '__main__':
    print('Write any tests or debugging code here.')
