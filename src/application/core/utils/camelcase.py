import re
from functools import reduce


def snake2pascal(snake: str) -> str:
    """
    Converts a snake_case string to PascalCase.
    """
    camel = snake.title()
    camel = re.sub("([0-9A-Za-z])_(?=[0-9A-Z])", lambda m: m.group(1), camel)
    return camel


def snake2camel(snake: str) -> str:
    """
    Converts a snake_case string to camelCase.
    """
    pascal = snake.title()
    pascal = re.sub("([0-9A-Za-z])_(?=[0-9A-Z])", lambda m: m.group(1), pascal)
    pascal = re.sub("(^_*[A-Z])", lambda m: m.group(1).lower(), pascal)
    return pascal


def camel2snake(camel: str) -> str:
    """
    Converts a camelCase string to snake_case.
    """
    snake = re.sub(r"([a-zA-Z])([0-9])", lambda m: f"{m.group(1)}_{m.group(2)}", camel)
    snake = re.sub(r"([a-z0-9])([A-Z])", lambda m: f"{m.group(1)}_{m.group(2)}", snake)
    return snake.lower()


def change_case(string, type_="to_camel"):
    if type_ == "to_camel":
        temp = string.split("_")
        res = temp[0] + "".join(ele.title() for ele in temp[1:])
    elif type_ == "to_snake":
        res = reduce(lambda x, y: x + ("_" if y.isupper() else "") + y, string).lower()
    return res
