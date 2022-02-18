import requests
from bs4 import BeautifulSoup
from convert_date import convert_date_fn
from convert_price import convert_price_fn
from config import dev


def freelance(page_limit, posts_limit):

    url = "https://freelance.ru"
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
        query = "/project/search/pro?page=" + str(page)

        try:
            req = requests.get(str(url) + str(query))
            soup = BeautifulSoup(req.content, "html.parser")
        except Exception as e:
            write_error(e, "Ошибка подключения")
            break

        try:
            first_injection = soup.find_all("div", {"class": "list-view"})[0]
        except Exception as e:
            write_error(e, "Ошибка тега first_injection на странице " + str(page))
            break

        second_injection_first = first_injection.find_all("div", {"class": "box-shadow project highlight"})
        second_injection_second = first_injection.find_all("div", {"class": "box-shadow project"})
        second_injection = second_injection_first + second_injection_second
        if len(second_injection) == 0:
            if page == 1:
                write_error("No have posts", "Ошибка тега second_injection на странице " + str(page))
                break
            break

        for post in second_injection:
            try:
                try:
                    title = post.find_all("div", {"class": "row"})[0]
                    title = title.find_all("div", {"class": "col-md-9"})[0]
                    title = title.find_all("div", {"class": "box-title"})[0]
                    title = title.find_all("h2", {"class": "title"})[0]
                    title = title["title"].lstrip().rstrip()
                except Exception:
                    raise ValueError("wrong tag of title")

                try:
                    description = post.find_all("div", {"class": "row"})[0]
                    description = description.find_all("div", {"class": "col-md-9"})[0]
                    description = description.find_all("div", {"class": "box-title"})[0]
                    description = description.find_all("a", {"class": "description"})[0]
                    description = description.text.lstrip().rstrip()
                except Exception:
                    raise ValueError("wrong tag of description")

                try:
                    price = post.find_all("div", {"class": "row"})[0]
                    price = price.find_all("div", {"class": "col-md-3"})[0]
                    price = price.find_all("div", {"class": "box-info"})[0]
                    price = price.find_all("div", {"class": "cost"})[0]
                    price = price.text.lstrip().rstrip()
                except Exception:
                    raise ValueError("wrong tag of price")

                try:
                    link = post.find_all("div", {"class": "row"})[0]
                    link = link.find_all("div", {"class": "col-md-9"})[0]
                    link = link.find_all("div", {"class": "box-title"})[0]
                    link = link.find_all("h2", {"class": "title"})[0]
                    link = link.find_all("a")[0]
                    link = link["href"].lstrip().rstrip()
                    link = url + str(link)
                except Exception:
                    raise ValueError("wrong tag of link")

                try:
                    date = post.find_all("div", {"class": "row"})[0]
                    date = date.find_all("div", {"class": "col-md-9"})[0]
                    date = date.find_all("div", {"class": "box-title"})[0]
                    date = date.find_all("span", {"class": "prop"})[0]
                    date = date.find_all("time", {"class": "timeago"})[0]
                    date = date["datetime"].lstrip().rstrip()
                except Exception:
                    raise ValueError("wrong tag of date")

                try:
                    converted_date = convert_date_fn(date)
                except Exception:
                    raise ValueError("not converted date: " + str(date))

                try:
                    converted_price = convert_price_fn(price)
                except Exception:
                    raise ValueError("not converted price: " + str(price))

                post_obj = {"title": title,
                            "description": description,
                            "price_amount": converted_price["amount"],
                            "price_currency": converted_price["currency"],
                            "link": link,
                            "date": converted_date,
                            "source": url}

                if post_obj["date"] != "closed":
                    final_posts.append(post_obj)
                    if len(final_posts) == int(posts_limit):
                        break

            except Exception as e:
                write_error(e, "Ошибка чтения поста на странице " + str(page))

        page += 1

    return {"posts": final_posts, "errors": errors, "source": url}
