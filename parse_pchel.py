from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from convert_date import convert_date_fn
from convert_price import convert_price_fn
from config import dev


def pchel(page_limit, posts_limit):

    url = "https://pchel.net"
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
        query = "/jobs/page-" + str(page) + "/"
        hdr = {'User-Agent': 'Mozilla/5.0'}

        try:
            req = Request(str(url) + str(query), headers=hdr)
            site_page = urlopen(req)
            soup = BeautifulSoup(site_page, "html.parser")
        except Exception as e:
            write_error(e, "Ошибка подключения")
            break

        try:
            first_injection = soup.find_all("div", {"class": "project-blocks"})[0]
        except Exception as e:
            write_error(e, "Ошибка тега first_injection на странице " + str(page))
            break

        second_injection = first_injection.find_all("div", {"class": "project-block project-block2"})
        if len(second_injection) == 0:
            if page == 1:
                write_error("No have posts", "Ошибка тега second_injection на странице " + str(page))
                break
            break

        for post in second_injection:
            try:
                try:
                    title = post.find_all("div", {"class": "project-block-cont"})[0]
                    title = title.find_all("div", {"class": "project-title"})[0]
                    title = title.find_all("a")[0]
                    title = title.text.lstrip().rstrip()
                except Exception:
                    raise ValueError("wrong tag of title")

                try:
                    description = post.find_all("div", {"class": "project-block-cont"})[0]
                    description = description.find_all("div", {"class": "project-text"})[0]
                    description = description.find_all("p")[0]
                    description = description.text.lstrip().rstrip()
                except Exception:
                    raise ValueError("wrong tag of description")

                try:
                    price = post.find_all("div", {"class": "project-block-cont"})[0]
                    price = price.find_all("div", {"class": "price"})[0]
                    price = price.text.lstrip().rstrip()
                except Exception:
                    raise ValueError("wrong tag of price")

                try:
                    link = post.find_all("div", {"class": "project-block-cont"})[0]
                    link = link.find_all("div", {"class": "project-title"})[0]
                    link = link.find_all("a")[0]
                    link = link["href"].lstrip().rstrip()
                    link = url + str(link)
                except Exception:
                    raise ValueError("wrong tag of link")

                try:
                    date = post.find_all("div", {"class": "project-block-cov"})[0]
                    date = date.find_all("div", {"class": "project-block-right"})[0]
                    date = date.find_all("div", {"class": "date"})[0]
                    date = date.text.lstrip().rstrip()
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
