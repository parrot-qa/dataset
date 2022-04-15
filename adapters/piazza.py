import time
from piazza_api import Piazza
from piazza_api.network import FolderFilter


def login():
    p = Piazza()
    p.user_login()
    return p


def _from_all(course_net):
    course_posts = course_net.iter_all_posts()
    for post in course_posts:
        time.sleep(1)
        yield post


def _from_folders(course_net, folders):
    seen = set()  # To remove duplicates, when a post is tagged to multiple folders
    for folder in folders:
        filter = FolderFilter(folder)
        course_posts = course_net.get_filtered_feed(filter)
        for post in course_posts['feed']:
            if post['id'] in seen:
                continue
            else:
                seen.add(post['id'])
                time.sleep(1)
                # The folder feed is just meta data, need another endpoint for complete post info
                yield course_net.get_post(post['id'])


def download_posts(p, course_id, folders=[], limit=None):
    course_net = p.network(course_id)
    if len(folders) > 0:
        post_generator = _from_folders(course_net, folders)
    else:
        post_generator = _from_all(course_net)

    raw_posts = []
    for post in post_generator:
        if limit and len(raw_posts) == limit:
            break
        else:
            raw_posts.append(post)

    return raw_posts


if __name__ == '__main__':
    # Unit test: Basic check
    handle = login()

    posts = download_posts(handle, 'ky7ls2h92kpwe', folders=['coding1'], limit=5)
    assert type(posts) == list
    assert len(posts) == 5

    posts = download_posts(handle, 'ky7ls2h92kpwe', limit=5)
    assert type(posts) == list
    assert len(posts) == 5

    print('All unit tests passed.')
