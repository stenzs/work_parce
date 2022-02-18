from string import digits

currency_dictionary = {"р": "rub", "₽": "rub", "руб": "rub", "$": "usd", "руб.запроект": "rub", "руб/заказ": "rub",
                       "руб.зачас": "rub/hour", "руб/час": "rub/hour"}


def convert_price_fn(string_price):

    if string_price is None:
        return {"amount": None, "currency": None}
    string_price = string_price.lower().replace(" ", "").replace(" ", "")
    price = False

    if string_price in ["договорная", "подоговоренности", "порезультатамсобеседования"]:
        return {"amount": None, "currency": None}

    if string_price.startswith("от"):
        string_price = string_price.replace("от", "")

    if string_price.startswith("до"):
        string_price = string_price.replace("до", "")

    currency = string_price.translate(str.maketrans("", "", digits))
    string_amount = string_price.replace(currency, "")

    if currency in ["р", "₽", "руб", "$", "руб.запроект", "руб.зачас", "руб/заказ", "руб/час"]:
        if string_price.startswith(currency) or string_price.endswith(currency):
            normalize_currency = currency_dictionary[currency]
            amount = ""
            for i in range(len(string_amount)):
                amount += string_amount[i]
            price = {"amount": int(amount), "currency": normalize_currency}

    if not price:
        raise ValueError("price not converted")
    return price
