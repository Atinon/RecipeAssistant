from rdflib import Graph
from food_energy_content import IngredientsList as il


def process_recipe(g, recipe_uri, include_list, exclude_list):
    recipe_query = f"""
    SELECT ?property ?value
    WHERE {{
      <{recipe_uri}> ?property ?value .
    }}
    """

    recipe_results = g.query(recipe_query)

    # Initialize variables to store information
    recipe_name = None
    cooking_time = None
    cooking_temperature = None
    serves = None
    link = None
    ingredients_list = []

    for row in recipe_results:
        property_name = row[0].split('/')[-1]  # Extract property name from the URI
        value = row[1]

        # Exclude unwanted property names
        unwanted_properties = [
            "recipe URI",
            "22-rdf-syntax-ns#type",
            "isRecommendedForCourse",
            "isRecommendedForMeal",
            "core#definition",
            "core#scopeNote",
            "prov#wasDerivedFrom",
            "rdf-schema#label"
        ]

        if property_name not in unwanted_properties:
            # Mapping property names to user-friendly labels
            if "hasIngredient" in property_name:
                # Extract the actual ingredient name after the last '/'
                ingredient_name = value.split('/')[-1]
                ingredients_list.append(ingredient_name)
            elif "hasCookTime" in property_name:
                cooking_time = value
            elif "hasCookingTemperature" in property_name:
                cooking_temperature = value
            elif "source" in property_name:
                link = value
                recipe_name = link.split(', "')[1].split(',"')[0]
            elif "serves" in property_name:
                serves = value
            else:
                # Display other information
                print(f"{property_name}: {value}")

    # Check if the recipe meets inclusion and exclusion criteria
    include_condition = all(ingredient in ingredients_list for ingredient in include_list)
    exclude_condition = not any(ingredient in ingredients_list for ingredient in exclude_list)

    if include_condition and exclude_condition:
        # Display the recipe name
        print('----------------------------------------------------------------' * 4)
        print(f"{recipe_name}\n")

        # Display cooking information
        if cooking_time:
            print(f"Cooking Time: {cooking_time}")
        if cooking_temperature:
            print(f"Cooking Temperature: {cooking_temperature}")
        if serves:
            print(f"Serves: {serves}")

        total_calories = 0

        # Display the list of ingredients
        print("\nIngredients you need:")
        for ingredient in ingredients_list:
            ingredient_calories = il.IngredientsList.get_calories_info(ingredient)
            if isinstance(ingredient_calories, int):
                total_calories += ingredient_calories
            print(f"- {ingredient}, calories: {ingredient_calories}")
        print(f"Total calories for this meal: {total_calories}")

        if link:
            print(f"\nLink: {link}")
        print('----------------------------------------------------------------' * 4)


def main():
    g = Graph()  # Initial empty Graph object

    # Load food energy content from file to IngredientsList class
    file_path = "food_energy_content/base_foods.json"
    try:
        il.IngredientsList.open_file(file_path)
    except FileNotFoundError:
        print(f"Failed to open ingredients file containing energy values at: {file_path}")
        exit(1)
    except il.json.JSONDecodeError:
        print(f"Error: Failed to decode JSON in '{file_path}'. Please check the file format.")
        exit(1)

    ontology_file_path = "ontology/WhatToMake_Individuals.rdf"
    g.parse(ontology_file_path)

    # Take user input for ingredients to include and exclude
    print("** Ingredients must start with a capital letter; Separate each ingredient with a comma(',') **")
    include_input = input("Enter the ingredient/s to include: ")
    exclude_input = input("Enter the ingredient/s to exclude: ")

    # Split user input into lists
    include_list = [ingredient.strip() for ingredient in include_input.split(',')]
    exclude_list = [ingredient.strip() for ingredient in exclude_input.split(',')]

    query = f"""
    PREFIX food: <http://purl.org/heals/food/>
    PREFIX ingredient: <http://purl.org/heals/ingredient/>
    SELECT DISTINCT ?recipe
    WHERE {{
      ?recipe food:hasIngredient ingredient:{include_list[0]} .
      FILTER NOT EXISTS {{
        ?recipe food:hasIngredient ingredient:{exclude_list[0]} .
      }}
    }}
    """

    results = g.query(query)

    # Extract the recipe URIs from the results
    recipe_uris = [row[0] for row in results]

    # Access information for each recipe
    for recipe_uri in recipe_uris:
        process_recipe(g, recipe_uri, include_list, exclude_list)


main()
