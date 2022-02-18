import requests
from bs4 import BeautifulSoup
from convert_date import convert_date_fn
from convert_price import convert_price_fn
from config import dev


def weblancer(page_limit, posts_limit):

    url = "https://www.weblancer.net"
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
        query = "/jobs/?page=" + str(page)

        try:
            req = requests.get(str(url) + str(query))
            soup = BeautifulSoup(req.content, "html.parser")
        except Exception as e:
            write_error(e, "Ошибка подключения")
            break

        try:
            first_injection = soup.find_all("div", {"class": "cols_table divided_rows"})[0]
        except Exception as e:
            write_error(e, "Ошибка тега first_injection на странице " + str(page))
            break

        second_injection = first_injection.find_all("div", {"class": "row click_container-link set_href"})
        if len(second_injection) == 0:
            if page == 1:
                write_error("No have posts", "Ошибка тега second_injection на странице " + str(page))
                break
            break

        for post in second_injection:
            try:
                try:
                    title = post.find_all("div", {"class": "col-sm-10"})[0]
                    title = title.find_all("div", {"class": "title"})[0]
                    if len(title.find_all("a", {"class": "text-bold click_target show_visited"})) == 1:
                        title = title.find_all("a", {"class": "text-bold click_target show_visited"})[0]
                        title = title.text.lstrip().rstrip()
                    elif len(title.find_all("a", {"class": "text-bold click_target blocked"})) == 1:
                        title = title.find_all("a", {"class": "text-bold click_target blocked"})[0]
                        title = title.text.lstrip().rstrip()
                except Exception:
                    raise ValueError("wrong tag of title")

                try:
                    description = post.find_all("div", {"class": "col-sm-10"})[0]
                    if len(description.find_all("div", {"class": "text_field text-inline"})) == 1:
                        description = description.find_all("div", {"class": "text_field text-inline"})[0]
                        if len(description.find_all("span", {"class": "snippet"})) == 1:
                            description = description.find_all("span", {"class": "snippet"})[0]
                        buttons_read_more_in_description = description.find_all("a", {"class": "d-inline-block dotted text-nowrap dropdown-toggle snippet_toggle"})
                        buttons_href_in_description = description.find_all("a", {"class": "dotted text-muted"})
                        buttons = buttons_read_more_in_description + buttons_href_in_description
                        for button in buttons:
                            button.decompose()
                        description = description.text.lstrip().rstrip()
                    elif len(post.find_all("p", {"class": "text_field text-muted"})) == 1:
                        description = post.find_all("p", {"class": "text_field text-muted"})[0]
                        description = description.text.lstrip().rstrip()
                except Exception:
                    raise ValueError("wrong tag of description")

                try:
                    price = post.find_all("div", {"class": "col-sm-2 text-sm-right"})[0]
                    price = price.find_all("div", {"class": "float-right float-sm-none title amount indent-xs-b0"})[0]
                    price = price.find_all("span", {"data-toggle": "tooltip"})
                    if len(price) == 0:
                        price = None
                    else:
                        price = price[0].text.lstrip().rstrip()
                except Exception:
                    raise ValueError("wrong tag of price")

                try:
                    link = post.find_all("div", {"class": "col-sm-10"})[0]
                    link = link.find_all("div", {"class": "title"})[0]
                    if len(link.find_all("a", {"class": "text-bold click_target show_visited"})) == 1:
                        link = link.find_all("a", {"class": "text-bold click_target show_visited"})[0]
                        link = link["href"].lstrip().rstrip()
                        link = url + str(link)
                    elif len(link.find_all("a", {"class": "text-bold click_target blocked"})) == 1:
                        link = link.find_all("a", {"class": "text-bold click_target blocked"})[0]
                        link = link["href"].lstrip().rstrip()
                        link = url + str(link)
                except Exception:
                    raise ValueError("wrong tag of link")

                try:
                    date = post.find_all("div", {"class": "col-sm-4 text-sm-right"})[0]
                    if len(date.find_all("span", {"class": "text-success"})) == 1:
                        date = date.find_all("span", {"class": "text-success"})[0]
                        date = date.text.lstrip().rstrip()
                    elif len(date.find_all("span", {"class": "text-muted"})) == 1:
                        date = date.find_all("span", {"class": "text-muted"})[0]
                        if len(date.find_all("span", {"class": "time_ago"})) == 1:
                            date = date.find_all("span", {"class": "time_ago"})[0]
                            date = date["title"].lstrip().rstrip()
                        else:
                            date = date.text.lstrip().rstrip()
                    elif len(date.find_all("span", {"class": "text-danger"})) == 1:
                        date = date.find_all("span", {"class": "text-danger"})[0]
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
