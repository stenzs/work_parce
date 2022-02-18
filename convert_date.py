from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

months_numerate = {"января": "01", "февраля": "02", "марта": "03", "апреля": "04", "мая": "05", "июня": "06",
                   "июля": "07", "августа": "08", "сентября": "09", "октября": "10", "ноября": "11", "декабря": "12"}

minutes_dictionary = ["минута", "минут", "минуты", "минуту"]
hours_dictionary = ["часов", "часа", "час"]
days_dictionary = ["день", "дня", "дней"]
weekends_dictionary = ["неделя", "недели", "недель"]
months_dictionary = ["месяц", "месяца", "месяцев"]
years_dictionary = ["год", "года", "лет"]

now = datetime.today()


def convert_date_fn(string_time):

    if string_time[:2] == "~ ":
        string_time = string_time[2:]
    string_time = string_time.lower().lstrip().rstrip()
    time_symbols = string_time.split(" ")
    time = False

    try:
        time_obj = datetime.strptime(string_time, "%d.%m.%Y %H:%M")
        return time_obj
    except Exception:
        pass
    try:
        time_obj = datetime.strptime(string_time, "%d.%m.%Y в %H:%M")
        return time_obj
    except Exception:
        pass
    try:
        time_obj = datetime.strptime(string_time[:16], "%Y-%m-%dt%H:%M")
        return time_obj
    except Exception:
        pass

    if string_time in ["завершен", "завершена", "в работе", "закрыт", "закрыта", "отклонен", "без победителей", "выбор победителя"]:
        return "closed"
    if string_time == "срочный проект":
        time = now - timedelta(days=1)
    if string_time == "только что":
        time = now
    if len(time_symbols) == 3 and time_symbols[1] in ["января,", "февраля,", "марта,", "апреля,", "мая,",
                                                      "июня,", "июля,", "августа,", "сентября,", "октября,",
                                                      "ноября,", "декабря,"]:
        day = time_symbols[0]
        if len(str(day)) == 1:
            day = str("0") + str(day)
        time_obj = day + "." + months_numerate[(time_symbols[1])[:-1]] + ".2022 " + time_symbols[2]
        time = datetime.strptime(time_obj, "%d.%m.%Y %H:%M")

    if len(time_symbols) == 3 \
            and time_symbols[1] in minutes_dictionary \
            and time_symbols[2] == "назад":
        time = now - timedelta(minutes=int(time_symbols[0]))
    if len(time_symbols) == 3 \
            and time_symbols[1] in hours_dictionary \
            and time_symbols[2] == "назад":
        time = now - timedelta(hours=int(time_symbols[0]))
    if len(time_symbols) == 3 \
            and time_symbols[1] in days_dictionary \
            and time_symbols[2] == "назад":
        time = now - timedelta(days=int(time_symbols[0]))
    if len(time_symbols) == 3 \
            and time_symbols[1] in weekends_dictionary \
            and time_symbols[2] == "назад":
        days = int(time_symbols[0]) * 7
        time = now - timedelta(days=days)
    if len(time_symbols) == 3 \
            and time_symbols[1] in months_dictionary \
            and time_symbols[2] == "назад":
        time = now
        time = time - relativedelta(months=int(time_symbols[0]))
    if len(time_symbols) == 3 \
            and time_symbols[1] in years_dictionary \
            and time_symbols[2] == "назад":
        time = now
        time = time - relativedelta(years=int(time_symbols[0]))
    if len(time_symbols) == 5 \
            and time_symbols[1] in hours_dictionary \
            and time_symbols[3] in minutes_dictionary \
            and time_symbols[4] == "назад":
        time = now - timedelta(hours=int(time_symbols[0]), minutes=int(time_symbols[2]))
    if len(time_symbols) == 7 \
            and time_symbols[1] in months_dictionary \
            and time_symbols[3] in hours_dictionary \
            and time_symbols[5] in minutes_dictionary \
            and time_symbols[6] == "назад":
        time = now - timedelta(hours=int(time_symbols[2]), minutes=int(time_symbols[4]))
        time = time - relativedelta(months=int(time_symbols[0]))
    if len(time_symbols) == 7 \
            and time_symbols[1] in years_dictionary \
            and time_symbols[3] in hours_dictionary \
            and time_symbols[5] in minutes_dictionary \
            and time_symbols[6] == "назад":
        time = now - timedelta(hours=int(time_symbols[2]), minutes=int(time_symbols[4]))
        time = time - relativedelta(years=int(time_symbols[0]))
    if len(time_symbols) == 9 \
            and time_symbols[1] in years_dictionary \
            and time_symbols[3] in months_dictionary \
            and time_symbols[5] in hours_dictionary \
            and time_symbols[7] in minutes_dictionary \
            and time_symbols[8] == "назад":
        time = now - timedelta(hours=int(time_symbols[4]), minutes=int(time_symbols[6]))
        time = time - relativedelta(years=int(time_symbols[0]), months=int(time_symbols[2]))

    if not time:
        raise ValueError("date not converted")

    try:
        return time
    except Exception:
        raise ValueError("date not converted")
