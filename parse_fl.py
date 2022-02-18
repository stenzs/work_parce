import requests
from bs4 import BeautifulSoup
from convert_date import convert_date_fn
from convert_price import convert_price_fn
from config import dev


def fl(page_limit, posts_limit):

    url = "https://www.fl.ru"
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
        query = "/projects/?page=" + str(page) + "&kind=1#/"

        try:
            req = requests.get(str(url) + str(query))
            soup = BeautifulSoup(req.content, "html.parser")
        except Exception as e:
            write_error(e, "Ошибка подключения")
            break

        try:
            first_injection = soup.find_all("div", {"class": "b-page__lenta"})[0]
            first_injection = first_injection.find_all("div", {"id": "projects-list"})[0]
        except Exception as e:
            if page > 1:
                break
            write_error(e, "Ошибка тега first_injection на странице " + str(page))
            break

        second_injection = first_injection.find_all("div", {"data-id": "qa-lenta-1"})
        if len(second_injection) == 0:
            if page == 1:
                write_error("No have posts", "Ошибка тега second_injection на странице " + str(page))
                break
            break

        for post in second_injection:
            try:
                try:
                    title = post.find_all("div", {"class": "b-post__grid"})[0]
                    if len(title.find_all("h2", {"class": "b-post__title b-post__grid_title p-0 b-post__pin"})) == 1:
                        title = title.find_all("h2", {"class": "b-post__title b-post__grid_title p-0 b-post__pin"})[0]
                        title = title.find_all("a")[0]
                        title = title.text.lstrip().rstrip()
                    elif len(title.find_all("h2", {"class": "b-post__title b-post__grid_title p-0"})) == 1:
                        title = title.find_all("h2", {"class": "b-post__title b-post__grid_title p-0"})[0]
                        title = title.find_all("a")[0]
                        title = title.text.lstrip().rstrip()
                except Exception:
                    raise ValueError("wrong tag of title")

                try:
                    description_scripts = post.find_all("div", {"class": "b-post__grid"})[0]
                    description_scripts = description_scripts.find_all("script", {"type": "text/javascript"})
                    description_script = description_scripts[1].text.strip("document.write('").rstrip("');")
                    description = BeautifulSoup(description_script, "html.parser")
                    description = description.find_all("div", {"class": "b-post__body b-post__grid_descript b-post__body_overflow_hidden b-layuot_width_full"})[0]
                    description = description.find_all("div", {"class": "b-post__txt"})[0]
                    description = description.text.lstrip().rstrip()
                except Exception:
                    raise ValueError("wrong tag of description")

                try:
                    price_scripts = post.find_all("div", {"class": "b-post__grid"})[0]
                    price_scripts = price_scripts.find_all("script", {"type": "text/javascript"})
                    price_scripts = price_scripts[0].text.strip("document.write('").rstrip("');")
                    price = BeautifulSoup(price_scripts, "html.parser")
                    if len(price.find_all("div", {"class": "b-post__price p-0 ml-lg-16 b-post__grid_price b-post__price_fontsize_15 b-post__price_bold"})) == 1:
                        price = price.find_all("div", {"class": "b-post__price p-0 ml-lg-16 b-post__grid_price b-post__price_fontsize_15 b-post__price_bold"})[0]
                        price_delete = price.find_all("a", {"class": "b-layout__txt_fontsize_12 b-layout__txt_padright_10 b-layout__txt_color_61a22b b-layout__txt_text_decor_none b-layout__txt_bold"})
                        for delete_obj in price_delete:
                            delete_obj.decompose()
                        price = price.text.lstrip().rstrip()
                    elif len(price.find_all("div", {"class": "b-post__price p-0 ml-lg-16 b-post__grid_price b-post__price_fontsize_13"})) == 1:
                        price = price.find_all("div", {"class": "b-post__price p-0 ml-lg-16 b-post__grid_price b-post__price_fontsize_13"})[0]
                        price_delete = price.find_all("a", {"class": "b-layout__txt_fontsize_12 b-layout__txt_padright_10 b-layout__txt_color_61a22b b-layout__txt_text_decor_none b-layout__txt_bold"})
                        for delete_obj in price_delete:
                            delete_obj.decompose()
                        price = price.text.lstrip().rstrip()
                except Exception:
                    raise ValueError("wrong tag of price")

                try:
                    link = post.find_all("div", {"class": "b-post__grid"})[0]
                    if len(link.find_all("h2", {"class": "b-post__title b-post__grid_title p-0 b-post__pin"})) == 1:
                        link = link.find_all("h2", {"class": "b-post__title b-post__grid_title p-0 b-post__pin"})[0]
                        link = link.find_all("a")[0]
                        link = link["href"].lstrip().rstrip()
                        link = url + str(link)
                    elif len(link.find_all("h2", {"class": "b-post__title b-post__grid_title p-0"})) == 1:
                        link = link.find_all("h2", {"class": "b-post__title b-post__grid_title p-0"})[0]
                        link = link.find_all("a")[0]
                        link = link["href"].lstrip().rstrip()
                        link = url + str(link)
                except Exception:
                    raise ValueError("wrong tag of link")

                try:
                    date_scripts = post.find_all("div", {"class": "b-post__grid"})[0]
                    date_scripts = date_scripts.find_all("script", {"type": "text/javascript"})
                    date_script = date_scripts[2].text.strip("document.write('").rstrip("');")
                    date = BeautifulSoup(date_script, "html.parser")
                    date = date.find_all("div", {"class": "b-post__txt b-post__txt_fontsize_11"})[0]
                    date_answers = date.find_all("a", {"class": "b-post__link b-post__txt_float_right b-post__link_bold b-post__link_fontsize_11 b-post__link_color_4e b-post__link_color_0f71c8_hover b-post__link_margtop_7 b-page__desktop"})
                    for delete_obj in date_answers:
                        delete_obj.decompose()
                    date_answers_second = date.find_all("a", {"class": "b-post__link b-post__txt_float_right b-post__link_bold b-post__link_fontsize_11 b-post__link_color_4e b-post__link_color_0f71c8_hover b-page__desktop"})
                    for delete_obj in date_answers_second:
                        delete_obj.decompose()
                    date_views = date.find_all("span", {"class": "b-post__txt b-post__txt_float_right b-post__txt_fontsize_11 b-post__txt_bold b-post__link_margtop_7"})
                    for delete_obj in date_views:
                        delete_obj.decompose()
                    date_views_second = date.find_all("span", {"class": "b-post__txt b-post__txt_float_right b-post__txt_fontsize_11 b-post__txt_bold"})
                    for delete_obj in date_views_second:
                        delete_obj.decompose()
                    date_delete_element = date.find_all("div", {"class": "b-post__txt b-post__txt_fontsize_11 b-post__txt_bold b-post__txt_float_right b-page__desktop b-post__link_margtop_7"})
                    for delete_obj in date_delete_element:
                        delete_obj.decompose()
                    date_delete_element_second = date.find_all("div", {"class": "b-post__txt b-post__txt_fontsize_11 b-post__txt_bold b-post__txt_float_right b-page__desktop"})
                    for delete_obj in date_delete_element_second:
                        delete_obj.decompose()
                    date_name = date.find_all("span", {"class": "b-post__bold b-layout__txt_inline-block"})
                    for delete_obj in date_name:
                        delete_obj.decompose()
                    date = date.text.lstrip().rstrip()
                except Exception:
                    raise ValueError("wrong tag of date")

                try:
                    status_scripts = post.find_all("div", {"class": "b-post__grid"})[0]
                    status_scripts = status_scripts.find_all("script", {"type": "text/javascript"})
                    status_script = status_scripts[2].text.strip("document.write('").rstrip("');")
                    status = BeautifulSoup(status_script, "html.parser")
                    status = status.find_all("div", {"class": "b-post__txt b-post__txt_fontsize_11"})[0]
                    status = status.text.lstrip().rstrip().lower().replace(" ", "")
                    if "исполнительопределён" in status:
                        status = "closed"
                except Exception:
                    raise ValueError("wrong tag of status")

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

                if post_obj["date"] != "closed" and status != "closed":
                    final_posts.append(post_obj)
                    if len(final_posts) == int(posts_limit):
                        break

            except Exception as e:
                write_error(e, "Ошибка чтения поста на странице " + str(page))

        page += 1

    return {"posts": final_posts, "errors": errors, "source": url}
