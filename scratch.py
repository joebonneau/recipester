import requests
from bs4 import BeautifulSoup, NavigableString, Tag

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

UNIT_TRANSLATIONS = {
    "c.": "cup",
    "cups": "cup",
    "pt.": "pint",
    "qt.": "quart",
    "tbsp": "tablespoon",
    "tbsp.": "tablespoon",
    "tablespoons": "tablespoon",
    "tsp": "teaspoon",
    "tsp.": "teaspoon",
    "teaspoons": "teaspoon",
    "pound": "lb",
    "pounds": "lb",
    "oz": "ounce",
    "oz.": "ounce",
    "ounces": "ounce",
}

QUANTITY_TRANSLATIONS = {
    "¼": 0.250,
    "1/4": 0.250,
    "½": 0.500,
    "1/2": 0.500,
    "¾": 0.750,
    "3/4": 0.750,
    "⅓": 0.333,
    "1/3": 0.333,
    "⅔": 0.667,
    "2/3": 0.667,
    "⅛": 0.125,
    "1/8": 0.125,
}


def parse_url(response):
    # url = request.POST.get("url")
    soup = BeautifulSoup(response.content, "html.parser")
    h1 = soup.h1
    title = ""
    if isinstance(h1, Tag):
        title = h1.get_text(separator=" ").strip()
    ingredients_div: Tag | NavigableString | None = soup.find(
        "div", class_=lambda x: "ingredient" in x if x is not None else False
    )
    site_name = ""
    site_name_obj: Tag | NavigableString | None = soup.find(
        "meta", attrs={"property": "og:site_name"}
    )
    if isinstance(site_name_obj, Tag):
        site_name = site_name_obj.get("content", "")
    ingredients = []
    if isinstance(ingredients_div, Tag):
        ingredients_li = ingredients_div.find_all("li")
        quantities = []
        units = []
        items = []
        match site_name:
            case "NYT Cooking":
                for li in ingredients_li:
                    spans = li.find_all("span")
                    if len(spans) == 2:
                        quantities.append(spans[0].get_text().strip())
                        items.append(spans[1].get_text().strip())
                    else:
                        quantities.append("")
                        items.append(li.get_text().strip())
                    units.append("")
            case "Delish":
                for li in ingredients_li:
                    strongs = li.find_all("strong")
                    ps = li.find_all("p")
                    if strongs:
                        quantities.append(strongs[0].get_text().strip())
                        units.append(
                            (strongs[1].get_text().strip() if len(strongs) > 1 else "")
                        )
                        items.append(ps[0].get_text().strip())
            case "Half Baked Harvest" | "Love and Lemons":
                for li in ingredients_li:
                    qty = li.find(
                        "span",
                        class_=lambda x: "amount" in x if x is not None else False,
                    )
                    quantities.append(qty.get_text().strip() if qty is not None else "")
                    unit = li.find(
                        "span", class_=lambda x: "unit" in x if x is not None else False
                    )
                    units.append(unit.get_text().strip() if unit is not None else "")
                    item = li.find(
                        "span", class_=lambda x: "name" in x if x is not None else False
                    )
                    items.append(item.get_text().strip() if item is not None else "")
            case _:
                pass
    else:
        # Bon Appetit
        ingredients_div = soup.find("div", attrs={"data-testid": "IngredientList"})
        items = [div.get_text().strip() for div in ingredients_div.div.find_all("div")]
        quantities = [
            div.get_text().strip() for div in ingredients_div.div.find_all("p")
        ]
        units = [""] * len(quantities)
    description_obj: Tag | NavigableString | None = soup.find(
        "meta", attrs={"name": "description"}
    )
    description = ""
    if isinstance(description_obj, Tag):
        description = description_obj.get("content", "")
    print("title: ", title, "description: ", description)
    print(quantities, units, items)


if __name__ == "__main__":
    # response = requests.get(
    #     "https://cooking.nytimes.com/recipes/1024665-coconut-saag", headers=headers
    # )
    # response = requests.get(
    #     "https://www.delish.com/cooking/recipe-ideas/a35421563/baked-feta-pasta-tiktok/",
    #     headers=headers,
    # )
    # response = requests.get(
    #     "https://www.halfbakedharvest.com/chicken-tzatziki-avocado-salad/",
    #     headers=headers,
    # )
    # response = requests.get(
    #     "https://www.loveandlemons.com/honey-mustard-dressing-recipe/", headers=headers
    # )
    response = requests.get(
        "https://www.bonappetit.com/recipe/sesame-tofu-with-broccoli", headers=headers
    )
    parse_url(response)
