from datetime import datetime
from config import page_for_parse_limit
from config import posts_for_parse_limit
from parse_weblancer import weblancer
from parse_freelance_habr import freelance_habr
from parse_fl import fl
from parse_freelance import freelance
from parse_pchel import pchel
from parse_youdo import youdo
from database import Posts, Jobs, Errors, Favorites
from operator import itemgetter
import time

now = datetime.today()
start_time = time.time()


def base_update():
    posts = []
    posts_for_upload = []
    posts_update = []
    not_for_delete_links = []
    errors = []
    parsers = [
        weblancer(page_for_parse_limit, posts_for_parse_limit),
        freelance_habr(page_for_parse_limit, posts_for_parse_limit),
        fl(page_for_parse_limit, posts_for_parse_limit),
        freelance(page_for_parse_limit, posts_for_parse_limit),
        pchel(page_for_parse_limit, posts_for_parse_limit),
        youdo(page_for_parse_limit, posts_for_parse_limit)
    ]

    for parser in parsers:
        posts = posts + parser["posts"]
        errors = errors + parser["errors"]

        print("---   ---   ---")
        print("Источник: ", parser["source"])
        print("Всего постов: ", len(parser["posts"]))
        print("Всего ошибок: ", len(parser["errors"]))

    db_posts = list(Posts.select().dicts())
    links_of_db_posts = list(map(itemgetter("link"), db_posts))

    for check_post in posts:
        not_for_delete_links.append(check_post["link"])
        if check_post["link"] not in links_of_db_posts:
            posts_for_upload.append(check_post)
        else:
            posts_update.append(check_post)

    links_of_posts_for_delete = [item for item in links_of_db_posts if item not in not_for_delete_links]

    Posts.insert_many(posts_for_upload).execute()

    deletes_posts = list(Posts.select().where((Posts.link.not_in(not_for_delete_links)) & (Posts.source != "https://workdirect.ru/")).dicts())
    ids_of_deletes_posts = list(map(itemgetter("id"), deletes_posts))
    Favorites.delete().where(Favorites.obj_id << ids_of_deletes_posts).execute()
    Posts.delete().where(Posts.id << ids_of_deletes_posts).execute()

    lead_time = ("%s" % (time.time() - start_time))

    jobs_report = {
        "time": now,
        "posts_parsed": len(posts),
        "posts_uploaded": len(posts_for_upload),
        "posts_update": len(posts_update),
        "posts_delete": len(links_of_posts_for_delete),
        "errors": len(errors),
        "lead_time": lead_time
    }

    job = Jobs.create(
        posts_parsed=jobs_report["posts_parsed"],
        posts_uploaded=jobs_report["posts_uploaded"],
        posts_update=jobs_report["posts_update"],
        posts_delete=jobs_report["posts_delete"],
        errors=jobs_report["errors"],
        lead_time=jobs_report["lead_time"],
        date=jobs_report["time"]
    )
    job_id = job.id

    for error in errors:
        error["job_id"] = job_id

    Errors.insert_many(errors).execute()


while True:
    base_update()
    hours = 12
    time.sleep(hours * 60 * 60)
