from datetime import datetime
from config import page_for_parse_limit
from config import posts_for_parse_limit
from parse_weblancer import weblancer
from parse_freelance_habr import freelance_habr
from parse_fl import fl
from parse_freelance import freelance
from parse_pchel import pchel
from parse_youdo import youdo
from database import Posts, Jobs, Errors

now = datetime.today()


def base_update():
    posts = []
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

    jobs_report = {
        "time": now,
        "posts_uploaded": len(posts),
        "posts_update": 0,
        "posts_delete": 0,
        "errors": len(errors)
    }

    for post in posts:
        post["parse_date"] = now

    # Проверка наличия постов
    # Загрузка только актуальных постов
    # Удаление неактуальных постов

    Posts.insert_many(posts).execute()

    job = Jobs.create(
        posts_uploaded=jobs_report["posts_uploaded"],
        posts_update=jobs_report["posts_update"],
        posts_delete=jobs_report["posts_delete"],
        errors=jobs_report["errors"],
        date=jobs_report["time"]
    )
    job_id = job.id

    for error in errors:
        error["job_id"] = job_id

    Errors.insert_many(errors).execute()


base_update()
