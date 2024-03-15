import re
from dataclasses import dataclass

import requests
from bs4 import BeautifulSoup, NavigableString, Tag, ResultSet

from recipester.recipester.models import Ingredient, Recipe, Unit


headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

# NOTE: Order matters to some extent so that period are removed
UNIT_TRANSLATIONS = {
    "c.": "cup",
    "cups": "cup",
    "pt.": "pint",
    "qt.": "quart",
    "Tbsp.": "tablespoon",
    "Tbsp": "tablespoon",
    "tablespoons": "tablespoon",
    "tsp.": "teaspoon",
    "tsp": "teaspoon",
    "teaspoons": "teaspoon",
    "lb": "pound",
    "pounds": "pound",
    "oz.": "ounce",
    "oz": "ounce",
    "ounces": "ounce",
}

QUANTITY_TRANSLATIONS: dict[str, float] = {
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


@dataclass
class QuantityRange:
    min: float
    max: float


@dataclass
class IngredientOptions:
    options: list[str]


def transform_quantity(quantity: str) -> float | QuantityRange | None:
    if transform := QUANTITY_TRANSLATIONS.get(quantity):
        return transform
    if "-" in quantity:
        min, max = quantity.split("-")
        return QuantityRange(float(min), float(max))
    # NOTE: This is not the same character as the last conditonal
    if "–" in quantity:
        min, max = quantity.split("–")
        return QuantityRange(float(min), float(max))
    for key, value in QUANTITY_TRANSLATIONS.items():
        if key in quantity:
            # remove string fraction from quantity str, then add
            return value + float(quantity.replace(key, "").strip())
    return float(quantity) if quantity != "" else None


def transform_unit(unit: str) -> str:
    return UNIT_TRANSLATIONS.get(unit, unit)


def transform_ingredient(
    ingredient: str, qty: float | QuantityRange | None
) -> tuple[float | QuantityRange | None, str | None, IngredientOptions | str]:
    # TODO: handle adjectives such as "cubed" or "diced" such that each option has the adjective
    unit = None
    subs = ""
    for key in UNIT_TRANSLATIONS:
        if key in ingredient:
            subs = key
            unit = UNIT_TRANSLATIONS[key]
            break
    if unit and ingredient.startswith(unit):
        ingredient = ingredient.replace(subs, "").strip()
    options = []
    for separator in [" or ", " and/or "]:
        if separator in ingredient:
            options = ingredient.split(separator)
            if re.match(options[1], r"^\d+"):
                # add the qty to the first option if the second option also has a qty
                options[0] = f"{qty} {options[0]}"
                qty = qty
            else:
                qty = None
    return qty, unit, IngredientOptions(options=options) if options else ingredient


def parse_nyt_cooking(ingredients_li: Tag):
    quantities = []
    units = []
    items = []
    for li in ingredients_li:
        spans = li.find_all("span")
        if len(spans) == 2:
            qty = transform_quantity(spans[0].get_text().strip())
            qty, unit, item = transform_ingredient(spans[1].get_text().strip(), qty)
            quantities.append(qty)
            units.append(unit)
            items.append(item)
        else:
            qty, unit, item = transform_ingredient(li.get_text().strip(), None)
            quantities.append(qty)
            units.append(unit)
            items.append(item)
    return quantities, units, items


def parse_delish(ingredients_li: ResultSet):
    quantities = []
    units = []
    items = []
    for li in ingredients_li:
        strongs = li.find_all("strong")
        ps = li.find_all("p")
        if strongs:
            qty = transform_quantity(strongs[0].get_text().strip())
            units.append(
                (
                    transform_unit(strongs[1].get_text().strip())
                    if len(strongs) > 1
                    else ""
                )
            )
            if isinstance(qty, str):
                qty = float(qty)
            qty, _, item = transform_ingredient(ps[0].get_text().strip(), qty)
            quantities.append(qty)
            items.append(item)
    return quantities, units, items


def parse_half_baked_harvest_love_and_lemons(ingredients_li: ResultSet):
    units = []
    quantities = []
    items = []
    for li in ingredients_li:
        qty_li = li.find(
            "span",
            class_=lambda x: "amount" in x if x is not None else False,
        )
        qty = (
            transform_quantity(qty_li.get_text().strip())
            if qty_li is not None
            else None
        )
        unit = li.find("span", class_=lambda x: "unit" in x if x is not None else False)
        units.append(
            transform_unit(unit.get_text().strip()) if unit is not None else ""
        )
        item = li.find("span", class_=lambda x: "name" in x if x is not None else False)
        qty, _, item = transform_ingredient(item.get_text().strip(), qty)
        quantities.append(qty)
        items.append(item)
    return quantities, units, items


def parse_bon_appetit(ingredients_div: Tag | NavigableString | None):
    items_units = [
        div.get_text().strip() for div in ingredients_div.div.find_all("div")
    ]
    items = []
    units = []
    quantities = [
        transform_quantity(div.get_text().strip())
        for div in ingredients_div.div.find_all("p")
        if isinstance(ingredients_div, Tag)
    ]
    for i in range(len(quantities)):
        qty = quantities[i]
        item_unit = items_units[i]
        qty, unit, item = transform_ingredient(item_unit, qty)
        units.append(transform_unit(unit))
        items.append(item)
        quantities[i] = qty
    return quantities, units, items


def create_entities(
    title: str,
    description: str,
    site_name: str,
    quantities: list[str | QuantityRange | None],
    units: list[str | None],
    ingredients: list[str | IngredientOptions],
):
    for i in range(len(ingredients)):
        if isinstance(ingredients[i], IngredientOptions):
            Ingredient.objects.create(name=" or ".join(ingredients[i].options))
        else:
            Ingredient.objects.create(name=ingredient[i])

        if not Unit.objects.get(name=units[i]):
            unit = Unit.objects.create(name=units[i])

    # Create Recipe entity
    recipe = Recipe.objects.create(
        title=title, description=description, sie_name=site_name
    )


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
    if isinstance(ingredients_div, Tag):
        ingredients_li = ingredients_div.find_all("li")
        quantities = []
        units = []
        items = []
        match site_name:
            case "NYT Cooking":
                quantities, units, items = parse_nyt_cooking(ingredients_li)
            case "Delish":
                quantities, units, items = parse_delish(ingredients_li)
            case "Half Baked Harvest" | "Love and Lemons":
                quantities, units, items = parse_half_baked_harvest_love_and_lemons(
                    ingredients_li
                )
            case _:
                pass
    else:
        ingredients_div = soup.find("div", attrs={"data-testid": "IngredientList"})
        quantities, units, items = parse_bon_appetit(ingredients_div)
    description_obj: Tag | NavigableString | None = soup.find(
        "meta", attrs={"name": "description"}
    )
    description = ""
    if isinstance(description_obj, Tag):
        description = description_obj.get("content", "")
    print("title: ", title, "description: ", description)
    print(quantities, units, items)
    create_entities(title, description, quantities, units, items)


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
    # response = requests.get(
    #     "https://www.bonappetit.com/recipe/sesame-tofu-with-broccoli", headers=headers
    # )
    response = requests.get(
        "https://www.bonappetit.com/recipe/sheet-pan-halloumi-avocado-citrus",
        headers=headers,
    )
    parse_url(response)
