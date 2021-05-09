"""
Pokemon sprites filter
"""

# Author:
# Lajos Neto <lajosneto@gmail.com>

import argparse
import os
from shutil import copyfile

import requests
import json

FILE_EXTENSION = ".png"
BASE_FOLDER = "original-source/"
BASE_API_URL = "https://pokeapi.co/api/v2/pokemon/"

ID_NAME_MAP_FILE = "name_id_map"

REGIONS = [
    "KANTO", 
    "JOHTO", 
    "HOENN", 
    "SINNOH", 
    "UNOVA", 
    "KALOS", 
    "ALOLA", 
    "GALAR"]

REGIONS_ID_RANGE = [
    range(1, 152), 
    range(152, 252), 
    range(252, 387), 
    range(387, 494), 
    range(494, 650), 
    range(650, 722), 
    range(722, 810), 
    range(810, 898)]

ALL_REGIONS_ID_RANGE = range(1, 899)

REGION_FOLDERS = [
    "filtered_sprites/kanto-pokedex/",
    "filtered_sprites/johto-pokedex/",
    "filtered_sprites/hoenn-pokedex/",
    "filtered_sprites/sinnoh-pokedex/",
    "filtered_sprites/unova-pokedex/",
    "filtered_sprites/kalos-pokedex/",
    "filtered_sprites/alola-pokedex/",
    "filtered_sprites/galar-pokedex/"
]

def build_id_name_map():
    id_name_map = dict()
    for index, region in enumerate(REGIONS):
        print(f"Building id map for {region} region...")
        for id in REGIONS_ID_RANGE[index]:
            pokemon_data = requests.get(BASE_API_URL + str(id))
            pokemon_data = dict(pokemon_data.json())
            pokemon_name = pokemon_data['name']
            id_name_map[id] = pokemon_name
    with open(ID_NAME_MAP_FILE, 'w') as outfile:
        json.dump(id_name_map, outfile)


def filter_sprites():
    with open('name_id_map') as name_id_map:
        name_id_map = json.load(name_id_map)
        for index, region in enumerate(REGIONS):
            print(f"Filtering sprites for {region} region...")
            region_folder = REGION_FOLDERS[index]
            if not os.path.exists(region_folder):
                os.makedirs(region_folder)
                for id in REGIONS_ID_RANGE[index]:
                    copyfile(
                        BASE_FOLDER + str(id) + FILE_EXTENSION, 
                        region_folder + name_id_map[str(id)] + FILE_EXTENSION)
            else :
                print("Kanto folder already exists. Maybe it's not empty?")
    

if __name__ == '__main__':
    filter_argparse = argparse.ArgumentParser()
    filter_argparse.add_argument('-s', '--setup', action='store_true')
    filter_argparse.add_argument('-spt', '--sprites', action='store_true')
    filter_argparse.add_argument('-m', '--map', action='store_true')
    args = filter_argparse.parse_args()
    args = filter_argparse.parse_args()
    if(args.sprites):
        filter_sprites()
    if(args.map):
        build_id_name_map()
    if(args.setup):
        build_id_name_map()
        filter_sprites()