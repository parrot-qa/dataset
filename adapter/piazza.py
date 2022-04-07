import time
from piazza_api import Piazza

def login():
    p = Piazza()
    p.user_login()
    return p


def download_posts(p, course_id):
    course_net = p.network(course_id)
    course_posts = course_net.iter_all_posts()
    raw_posts = []
    for post in course_posts:
        raw_posts.append(post)
        time.sleep(1)
    return raw_posts


if __name__ == '__main__':
    # Unit test: <Verify some basic functionality>
    # TODO
    p = download_posts('course_id')
    assert type(p) == list

    print('All unit tests passed.')
