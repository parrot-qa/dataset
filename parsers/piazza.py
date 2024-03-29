from .html import extract_text_basic
import json
import re

def get_question_tags(posts):
    question_numbers = []
    for post in posts:
        question_numbers.append(int(post.get("tag_num")))
    return question_numbers

def trace_back_check(formatted_QA, rawQA):

    to_remove = []
    question_tag_numbers = get_question_tags(formatted_QA)
    for post in formatted_QA:
        student_answer = post.get("student_answer")         # the current post's student answer
        instructor_answer = post.get("instructor_answer")   # the current post's instructor answer
        if "@" in student_answer:                           # IF there is an @ symbol in the student's answer
            index = student_answer.index("@")
            if student_answer[index+1].isnumeric():         # and the next index is a number
                link_val = re.search('\@(\d*)', student_answer)[1]  # get the number next to the @ sign
                if int(link_val) in question_tag_numbers:                # IF the number is the num_tag to a question
                    for post_sub in formatted_QA:                   # LOOP through the formmatted posts
                        if post_sub.get("tag_num") == int(link_val):     # IF we find the right post
                            if post_sub.get("student_answer") != "":# and IF that linked post has a student answer
                                post["student_answer"] = post_sub.get("student_answer") # over write the dataset with the linked answer
                            else:
                                post["student_answer"] = post_sub.get("instructor_answer") # if there isn't a student answer in the linked post, rewrite with the instructor answer
                else: # IF the linked post is NOT a question
                    to_remove.append(post)
        
        
        if "@" in instructor_answer:                           # IF there is an @ symbol in the student's answer
            index = instructor_answer.index("@")
            if instructor_answer[index+1].isnumeric():         # and the next index is a number
                link_val = re.search('\@(\d*)', instructor_answer)[1]  # get the number next to the @ sign
                if int(link_val) in question_tag_numbers:                # IF the number is the num_tag to a question
                    for post_sub in formatted_QA:                   # LOOP through the formmatted posts
                        if post_sub.get("tag_num") == int(link_val):     # IF we find the right post
                            if post_sub.get("instructor_answer") != "":# and IF that linked post has a student answer
                                post["instructor_answer"] = post_sub.get("instructor_answer") # over write the dataset with the linked answer
                            else:
                                post["instructor_answer"] = post_sub.get("student_answer") # if there isn't a student answer in the linked post, rewrite with the instructor answer
                else: # IF the linked post is NOT a question
                    to_remove.append(post)
    for drop in to_remove:
        if drop in formatted_QA:
            formatted_QA.remove(drop)
    return formatted_QA


def extract_question_posts(post_list):
    questions = []
    for post in post_list:
        if (post.get("type") == "question") and ("unanswered" not in post.get("tags")):
            questions.append(post)
    return questions


def get_answers(post):
    instructor_answer = ""
    instructor_answer_thanks = 0
    student_answer = ""
    student_answer_thanks = 0
    children_posts = post.get("children")
    for child in children_posts:
        if child.get("type") == "i_answer":
            instructor_answer = child.get("history")[-1].get("content")
            if child.get("tag_endorse_arr"):
                instructor_answer_thanks = len(child.get("tag_endorse_arr"))
            else: 
                instructor_answer_thanks = 0
        if child.get("type") == "s_answer":
            student_answer = child.get("history")[-1].get("content")
            if child.get("tag_endorse_arr"):
                student_answer_thanks = len(child.get("tag_endorse_arr"))
            else:
                student_answer_thanks = 0
    return instructor_answer, instructor_answer_thanks, student_answer, student_answer_thanks


def get_question_content(post):
    return post.get("history")[-1].get("content")


def get_subject(post):
    return post.get("history")[-1].get("subject")

def get_answerability(post):
    str_list_content = ["my grade", "waitlist", "stolen", "lost", "png", "jpeg", "howamidoing"]
    str_list_i_answer = ["private", "email me", "email us", "privately", "resolved"]
    
    content_clean = re.sub(r'[^\w\s]', '', extract_text_basic(post.get("content")).lower())
    i_answer_clean = re.sub(r'[^\w\s]', '', extract_text_basic(post.get("instructor_answer")).lower())
    if any(ext in content_clean for ext in str_list_content) or any(ext in i_answer_clean for ext in str_list_i_answer):
        result = False
    else:
        result = True
    return result


def extract_qa(path, *args, **kwargs) -> list[dict]:
    """Take a file path as input, and return a list of question-answers."""
    f1 = open(path)
    raw_QA = json.load(f1)
    f1.close()

    answered_questions = extract_question_posts(raw_QA)
    formatted_QA = []
    for post in answered_questions:
        i_answer, i_thanks_count, s_answer, s_thanks_count = get_answers(post)
        post_dict = {"id": post.get("id"),
                     "tag_num": post.get("nr"),
                     "subject": get_subject(post),
                     "content": extract_text_basic(get_question_content(post)),
                     "student_answer": extract_text_basic(s_answer),
                     "student_answer_thanks_count": s_thanks_count,
                     "instructor_answer": extract_text_basic(i_answer),
                     "instructor_answer_thanks_count": i_thanks_count,
                     "folders": post.get("folders"),
                     "good_question_count": len(post.get("tag_good"))}
         
        if (post_dict["student_answer"] + post_dict["instructor_answer"]) == "":
            # Answer exists but is probably not text, so skip this post
            continue
        post_dict["is_answerable"] = get_answerability(post_dict)
        formatted_QA.append(post_dict)
    final_QA = trace_back_check(formatted_QA, raw_QA)
    return final_QA


if __name__ == '__main__':
    print('Write any tests or debugging code here.')
