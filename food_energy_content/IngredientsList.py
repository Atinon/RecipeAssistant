import json


class IngredientsList:
    _ingredients = []

    @classmethod
    def open_file(cls, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            cls._ingredients = data.get("Ingredients", [])

    @classmethod
    def get_calories_info(cls, ingredient_to_find):
        matching_product_calories = [ingredient['Calories'] for ingredient in cls._ingredients if
                                     ingredient_to_find.lower() in ingredient['Product'].lower()]
        if matching_product_calories:
            return matching_product_calories[0]
        else:
            return "N/A"
