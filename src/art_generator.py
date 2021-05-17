"""
Pokemon art images assets generator.
"""

# Author:
# Lajos Neto <lajosneto@gmail.com>

import argparse
import os

import json
import requests
import bs4 as bs

ID_ART_MAP_PATH = "../resources/id_art_maptemp"
NAME_ID_MAP_PATH = "../resources/name_id_map"
ALL_REGIONS_ID_RANGE = range(1, 10)
POKEMON_ART_BULBA_BASE_URL = "https://bulbapedia.bulbagarden.net/wiki/File:"
ART_FILE_EXTENSION = ".png"
POKEMON_ID_FULL_MASK_SIZE = 3

def build_art_assets():
    art_assets = dict()
    with open(NAME_ID_MAP_PATH) as name_id_map:
        name_id_map = json.load(name_id_map)
    for id in ALL_REGIONS_ID_RANGE:
        print(f"Building art asset for id {id} of 898")
        full_id = format_id(str(id))
        pokemon_name = name_id_map[str(id)]
        pokemon_name = pokemon_name[0].capitalize() + pokemon_name[1:]
        
        art_page = requests.get(POKEMON_ART_BULBA_BASE_URL + full_id + pokemon_name + ART_FILE_EXTENSION)
        soup = bs.BeautifulSoup(art_page.content, 'html.parser')
        art_div = soup.find(id='file')
        art_url = art_div.find('a')['href']

        art_assets[str(id)] = "https:" + art_url
        
    with open(ID_ART_MAP_PATH, 'w') as fout:
        json.dump(art_assets , fout, ensure_ascii=False, indent=4)

def format_id(raw_id):
    size_diff = POKEMON_ID_FULL_MASK_SIZE - len(raw_id)
    return ("0" * size_diff) + raw_id

if __name__ == '__main__':
    filter_argparse = argparse.ArgumentParser()
    filter_argparse.add_argument('-s', '--setup', action='store_true')
    args = filter_argparse.parse_args()
    if(args.setup):
        build_art_assets()

