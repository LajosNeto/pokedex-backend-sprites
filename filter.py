"""
Pokemon sprites filter
"""

# Author:
# Lajos Neto <lajosneto@gmail.com>

import argparse
import os
from shutil import copyfile
import requests

FILE_EXTENSION = ".png"
BASE_FOLDER = "original-source/"
BASE_API_URL = "https://pokeapi.co/api/v2/pokemon/"

KANTO_FOLDER = "kanto-pokedex/"
KANTO_IDS = range(1, 152)

def filter_kanto():
    if not os.path.exists(KANTO_FOLDER):
        os.makedirs(KANTO_FOLDER)
        for id in KANTO_IDS:
            pokemon_data = requests.get(BASE_API_URL + str(id))
            pokemon_data = dict(pokemon_data.json())
            copyfile(
                BASE_FOLDER + str(id) + FILE_EXTENSION, 
                KANTO_FOLDER + pokemon_data['name'] + FILE_EXTENSION)
    else :
        print("Kanto folder already exists. Maybe it's not empty?")
    

if __name__ == '__main__':
    filter_argparse = argparse.ArgumentParser()
    filter_argparse.add_argument('-k', '--kanto', action='store_true')
    args = filter_argparse.parse_args()
    if(args.kanto):
        filter_kanto()