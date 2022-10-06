"""
Pokemon detail generator.
"""

# Author:
# Lajos Neto <lajosneto@gmail.com>

import argparse
import multiprocessing
import os
from shutil import copyfile

import requests
import json

LOCAL_DETAIL_BASE_PATH = "../resources/detail/"
LOCAL_CRY_BASE_PATH = "../resources/cry/"

ALL_REGIONS_ID_RANGE = range(1, 898)

BASE_POKEMON_DATA_API_URL = "https://pokeapi.co/api/v2/pokemon/"
BASE_POKEMON_DETAILS_API_URL = "https://pokeapi.co/api/v2/pokemon/"
BASE_POKEMON_SPECIES_DATA_API_URL = "https://pokeapi.co/api/v2/pokemon-species/"
BASE_NAMES_API_URL = "https://pokeapi.co/api/v2/pokemon-species/"

REMOTE_BASE_SPRITE_PATH = "https://raw.githubusercontent.com/LajosNeto/pokedex-backend-sprites/main/resources/sprite/"
SPRITE_FILE_TYPE = ".png"
REMOTE_BASE_CRY_PATH = "https://raw.githubusercontent.com/LajosNeto/pokedex-backend-sprites/main/resources/cry/"
CRY_FILE_TYPE = ".wav"
ID_ART_MAP_FILE = "../resources/id_art_map"

SPECIES_COLORS = {
    'black': "#585858",
    'blue': "#4589e9",
    'brown': "#a8733d",
    'gray': "#a0a0a0",
    'green': "#62b570",
    'pink': "#eb96c6",
    'purple': "#9e6dbb",
    'red': "#e0626a",
    'white': "#f0f0f0",
    'yellow': "#ecd061"
}

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

session = None

def set_global_session():
    global session
    if not session:
        session = requests.Session()

def load_pokemon_data(pokemon_id):
    pokemon_id = str(pokemon_id)
    pokemon_data = requests.get(BASE_POKEMON_DETAILS_API_URL + pokemon_id)
    return dict(pokemon_data.json())

def load_species_data(pokemon_id):
    pokemon_id = str(pokemon_id)
    species_data = requests.get(BASE_POKEMON_SPECIES_DATA_API_URL + pokemon_id)
    return dict(species_data.json())

def load_name_data(pokemon_id):
    pokemon_id = str(pokemon_id)
    name_data = requests.get(BASE_NAMES_API_URL + pokemon_id)
    return dict(name_data.json())


def build_detail_data(pokemon_id):
    pokemon_id = str(pokemon_id)

    print(f"Building data for id {pokemon_id} of 898")

    with open(ID_ART_MAP_FILE) as id_art_map_file:
        id_art_map = json.load(id_art_map_file)


    pokemon_data = load_pokemon_data(pokemon_id)
    species_data = load_species_data(pokemon_id)
    name_data = load_name_data(pokemon_id)

    pokemon_detail = dict()
    pokemon_detail['id'] = pokemon_data['id']
    pokemon_detail['name_en'] = pokemon_data['name']
    pokemon_detail['name_ja'] = extract_japanese_name(name_data)
    pokemon_detail['attributes'] = extract_attributes(pokemon_data, species_data)
    pokemon_detail['sprite_url'] = REMOTE_BASE_SPRITE_PATH + pokemon_id + SPRITE_FILE_TYPE
    pokemon_detail['art_url'] = id_art_map[pokemon_id]
    pokemon_detail['cry_url'] = extract_cry_url(pokemon_id)
    pokemon_detail['base_stats'] = extract_base_stats(pokemon_data)
    pokemon_detail['abilities'] = extract_abilities(pokemon_data)
    pokemon_detail['types'] = extract_types(pokemon_data)
    pokemon_detail['short_description'] = extract_flavor_description(species_data)
    pokemon_detail['habitat'] = extract_habitat(species_data)
    pokemon_detail['color'] = SPECIES_COLORS[species_data['color']['name']]
    pokemon_detail['evolution_chain'] = process_evolution_chain(species_data['evolution_chain']['url'])
    with open(LOCAL_DETAIL_BASE_PATH + str(pokemon_id), 'w') as pokemon_detail_output_file:
        json.dump(pokemon_detail , pokemon_detail_output_file, ensure_ascii=False, indent=4)

    # clean up
    id_art_map_file.close()
    pokemon_detail_output_file.close()


def process_evolution_chain(chain_url):
    chain_data = requests.get(chain_url)
    chain_data = dict(chain_data.json())

    evolution_chain = []

    chain_first_details = extract_step_details(chain_data['chain'])
    evolution_chain.append(chain_first_details)

    # case when chain is not sequential (e.g. eevee)
    if (len(chain_data['chain']['evolves_to']) > 1):
        for step in chain_data['chain']['evolves_to']:
            step_details = extract_step_details(step)
            evolution_chain.append(step_details)
    
    # case when chain is sequential (e.g. charmander)
    elif (len(chain_data['chain']['evolves_to']) == 1):
        step = chain_data['chain']['evolves_to']
        while(len(step) > 0):
            step_details = extract_step_details(step[0])
            evolution_chain.append(step_details)
            step = step[0]['evolves_to']
    
    return evolution_chain

def extract_id_from_url(url):
    return url.split('/')[-2]

def extract_cry_url(pokemon_id):
    return REMOTE_BASE_CRY_PATH + pokemon_id + CRY_FILE_TYPE if os.path.isfile(LOCAL_CRY_BASE_PATH + pokemon_id + CRY_FILE_TYPE) else ""

def extract_step_details(chain_step):
    pokemon_id = extract_id_from_url(chain_step['species']['url'])
    step_pokemon_data = load_pokemon_data(pokemon_id)
    step_details = {
        'name': chain_step['species']['name'],
        'sprite_url': REMOTE_BASE_SPRITE_PATH + str(pokemon_id) + SPRITE_FILE_TYPE,
        'types': extract_types(step_pokemon_data),
        # 'types_colors': extract_types_colors(step_pokemon_data)
    }
    return step_details

def extract_types(pokemon_data):
    types_names = [type['type']['name'] for type in pokemon_data['types']]
    types_colors = [TYPES_COLORS[type['type']['name']] for type in pokemon_data['types']]
    return list(map(lambda name, color : {'name': name, 'color': color}, types_names, types_colors))


def extract_flavor_description(species_data):
    short_description = ""
    for flavor in species_data['flavor_text_entries']:
        if (flavor['language']['name'] == "en"):
            short_description = flavor['flavor_text'].replace("\n", " ")
    return short_description

def extract_base_stats(pokemon_data):
    base_stats = dict()
    base_stats['hp'] = pokemon_data['stats'][0]['base_stat']
    base_stats['attack'] = pokemon_data['stats'][1]['base_stat']
    base_stats['defense'] = pokemon_data['stats'][2]['base_stat']
    base_stats['special-attack'] = pokemon_data['stats'][3]['base_stat']
    base_stats['special-defense'] = pokemon_data['stats'][4]['base_stat']
    base_stats['speed'] = pokemon_data['stats'][5]['base_stat']
    base_stats['total'] = sum(base_stats.values())
    return base_stats

def extract_abilities(pokemon_data):
    abilities = []
    for ability in pokemon_data['abilities']:
        ability_data = requests.get(ability['ability']['url'])
        ability_data = dict(ability_data.json())

        ability_detail = dict()
        ability_description = ""
        for entry in ability_data['effect_entries']:
            if (entry['language']['name'] == "en"):
                ability_description = entry['short_effect']
        ability_detail['name'] = ability['ability']['name'].replace("-"," ").title()
        ability_detail['description'] = ability_description

        abilities.append(ability_detail)
    return abilities

def extract_habitat(species_data):
    return species_data['habitat']['name'] if species_data['habitat'] is not None else ""

def extract_japanese_name(name_data):
    name_japanese = ""
    for name in name_data['names']:
        if (name['language']['name'] == "ja"):
            name_japanese = name['name']
    return name_japanese

def extract_attributes(pokemon_data, species_data):

    attributes = [
        {
            'name': "height",
            'value': str(float(pokemon_data['height'])/10) + " m"
        },
        {
            'name': "weight",
            'value': str(float(pokemon_data['weight'])/10) + " kg"
        },
        {
            'name': "base exp",
            'value': str(pokemon_data['base_experience'])
        },
        {
            'name': "growth rate",
            'value': str(species_data['growth_rate']['name'])
        },
        {
            'name': "legendary",
            'value': "yes" if species_data['is_legendary'] else "no"
        },
        {
            'name': "mythical",
            'value': "yes" if species_data['is_mythical'] else "no"
        }
    ]
    return attributes

if __name__ == '__main__':
    filter_argparse = argparse.ArgumentParser()
    filter_argparse.add_argument('-s', '--setup', action='store_true')
    args = filter_argparse.parse_args()
    if(args.setup):
        if not os.path.exists(LOCAL_DETAIL_BASE_PATH):
            os.makedirs(LOCAL_DETAIL_BASE_PATH)
            with multiprocessing.Pool(initializer=set_global_session) as pool:
                pool.map(build_detail_data, ALL_REGIONS_ID_RANGE)
        else :
            print("Detail data folder already exists. Maybe it's not empty?")