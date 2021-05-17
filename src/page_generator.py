"""
Pokemon pagination json generator.
"""

# Author:
# Lajos Neto <lajosneto@gmail.com>

import argparse
import os
from shutil import copyfile

import requests
import json

PAGES_BASE_PATH = "pages/page_"

BASE_POKEMON_DETAILS_API_URL = "https://pokeapi.co/api/v2/pokemon/"
BASE_NAMES_API_URL = "https://pokeapi.co/api/v2/pokemon-species/"

BASE_SPRITE_PATH = "https://raw.githubusercontent.com/LajosNeto/pokedex-backend-sprites/main/resources/sprites/original-source/"
SPRITE_FILE_TYPE = ".png"

ALL_REGIONS_ID_RANGE = range(1, 899)
PAGE_SIZE = 20

TYPES_COLORS = {
    "normal": "#9e9e6f",
    "fire": "#ed7835",
    "fighting": "#b72f29",
    "water": "#5f84ea",
    "flying": "#9e85eb",
    "grass": "#6dc04c",
    "poison": "#953a93",
    "electric": "#f6cb3b",
    "ground": "#dbb963",
    "psychic": "#f6527e",
    "rock": "#af9539",
    "ice": "#8ed2d2",
    "bug": "#9daf2b",
    "dragon": "#6630f3",
    "ghost": "#654e8c",
    "dark": "#644e40",
    "steel": "#afafc9",
    "fairy": "#eb90a4",
    "???": "#5e9585"
}

def build_pages():
    pokemons = list()
    for id in ALL_REGIONS_ID_RANGE:
        print(f"Building data for id {id} of 898")
        pokemon_details = requests.get(BASE_POKEMON_DETAILS_API_URL + str(id))
        pokemon_details = dict(pokemon_details.json())
        pokemon_names = requests.get(BASE_NAMES_API_URL + str(id))
        pokemon_names = dict(pokemon_names.json())

        nameJa = "-"
        for name in pokemon_names['names']:
            if (name['language']['name'] == "ja"):
                nameJa = name['name']

        pokemon_data = dict()
        pokemon_data['id'] = id
        pokemon_data['nameEn'] = pokemon_details['name']
        pokemon_data['nameJa'] = nameJa
        pokemon_data['sprite'] = BASE_SPRITE_PATH + str(id) + SPRITE_FILE_TYPE
        pokemon_data['types'] = [type['type']['name'] for type in pokemon_details['types']]
        pokemon_data['typesColors'] = [TYPES_COLORS[type['type']['name']] for type in pokemon_details['types']]

        pokemons.append(pokemon_data)
    
    page_number = 0
    for i in range(0, len(pokemons), PAGE_SIZE):
        page = pokemons[i:i + PAGE_SIZE]
        with open(PAGES_BASE_PATH + str(page_number), 'w') as fout:
            json.dump(page , fout, ensure_ascii=False, indent=4)
        page_number += 1

if __name__ == '__main__':
    filter_argparse = argparse.ArgumentParser()
    filter_argparse.add_argument('-s', '--setup', action='store_true')
    args = filter_argparse.parse_args()
    if(args.setup):
        build_pages()
