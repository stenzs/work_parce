import requests
from time import sleep
from datetime import datetime
from convert_price import convert_price_fn
from config import dev


def youdo(page_limit, posts_limit):

    url = "https://youdo.com"
    final_posts = []
    errors = []
    page = 1

    def write_error(error, error_description):
        error_object = {"error": str(error), "description": str(error_description), "source": str(url)}
        errors.append(error_object)

    while True:
        if page > page_limit or len(final_posts) == posts_limit:
            break
        if dev:
            print("~~ ", page, " ~~")
        query = "/api/tasks/tasks/"
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
        body = {"q": "", "list": "all", "status": "opened", "radius": None, "page": page, "noOffers": False,
                "onlySbr": False, "onlyB2B": False, "onlyVacancies": False, "priceMin": "", "sortType": 1,
                "onlyVirtual": True, "categories": ["all"]}

        try:
            req = requests.post(str(url) + str(query), json=body, headers=headers)
            posts = req.json()["ResultObject"]["Items"]
        except Exception as e:
            write_error(e, "Ошибка подключения к api")
            break

        for post in posts:
            try:
                try:
                    title = post["Name"]
                except Exception:
                    raise ValueError("wrong tag of title")

                try:
                    price = str(post["PriceAmount"]) + "руб"
                    if str(price) == "0":
                        price = post["BudgetDescription"]
                        if "от" in price:
                            price = str(price.replace("от", "")) + "руб"
                        elif "до" in price:
                            price = str(price.replace("до", "")) + "руб"
                except Exception:
                    raise ValueError("wrong tag of price")

                try:
                    link = post["Url"]
                    link = url + str(link)
                except Exception:
                    raise ValueError("wrong tag of link")

                try:
                    converted_price = convert_price_fn(price)
                except Exception:
                    raise ValueError("not converted price: " + str(price))

                post_obj = {"title": title,
                            "description": None,
                            "price_amount": converted_price["amount"],
                            "price_currency": converted_price["currency"],
                            "link": link,
                            "date": datetime.today(),
                            "source": url}

                if post_obj["date"] != "closed":
                    final_posts.append(post_obj)
                    if len(final_posts) == int(posts_limit):
                        break

            except Exception as e:
                write_error(e, "Ошибка чтения поста на странице " + str(page))

        page += 1
        sleep(1)
    return {"posts": final_posts, "errors": errors, "source": url}
