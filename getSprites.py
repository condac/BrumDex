

import os
import requests
import json

# Load the Pokémon data
with open('pokemon.json', 'r', encoding='utf-8') as file:
    pokemon_data = json.load(file)

# Create a folder to store the sprites
output_folder = 'sprites'
os.makedirs(output_folder, exist_ok=True)

# Base URL for the sprite images
base_url = "https://cobblemon.tools/pokedex/pokemon/{}/sprite.png" # https://cobblemon.tools/pokedex/pokemon/bulbasaur/sprite.png

# Loop through each Pokémon and download its sprite
for pokemon in pokemon_data:
    name = pokemon['name']['en'].lower().replace("♀", "f").replace("♂", "m").replace("'", "").replace(" ", "").replace(".", "").replace("é", "e").replace("-", "")
    sprite_url = base_url.format(name)
    output_path = os.path.join(output_folder, f"{name}.png")
    if os.path.exists(output_path):
        continue
        
    try:
        # Fetch the sprite
        response = requests.get(sprite_url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        # Save the sprite
        with open(output_path, 'wb') as sprite_file:
            sprite_file.write(response.content)
        print(f"Downloaded: {name}")

    except requests.RequestException as e:
        print(f"Failed to download {name}: {e}")

print("Download complete!")


