import time
from piazza_api import Piazza
from piazza_api.network import FolderFilter


def login():
    p = Piazza()
    p.user_login()
    return p


def download_posts(p, course_id, folder=None, limit=None):
    course_net = p.network(course_id)
    if folder:
        filter = FolderFilter(folder)
        course_posts = course_net.get_filtered_feed(filter)
        course_posts = course_posts['feed']
    else:
        course_posts = course_net.iter_all_posts()

    raw_posts = []
    for post in course_posts:
        if not folder:
            # Pause every post to avoid rate limit errors.
            # Only applicable for all posts since it does not use a bulk API.
            time.sleep(1)
        if limit and len(raw_posts) == limit:
            break
        raw_posts.append(post)

    return raw_posts


if __name__ == '__main__':
    # Unit test: Basic check
    handle = login()
    posts = download_posts(handle, 'ky7ls2h92kpwe', folder='coding1', limit=5)
    assert type(posts) == list
    assert len(posts) == 5

    print('All unit tests passed.')
