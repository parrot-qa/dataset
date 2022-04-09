import time
from piazza_api import Piazza


def login():
    p = Piazza()
    p.user_login()
    return p


def download_posts(p, course_id, limit=None):
    course_net = p.network(course_id)
    course_posts = course_net.iter_all_posts()
    raw_posts = []
    for post in course_posts:
        if limit and len(raw_posts) == limit:
            break
        raw_posts.append(post)
        time.sleep(1)
    return raw_posts


if __name__ == '__main__':
    # Unit test: Basic check
    handle = login()
    posts = download_posts(handle, 'ky7ls2h92kpwe', limit=5)
    assert type(posts) == list
    assert len(posts) == 5

    print('All unit tests passed.')
