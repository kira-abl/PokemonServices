from flask import Flask, request, json, Response
import logging as log
import requests
import json
import os

log.basicConfig(level=log.DEBUG, format='%(asctime)s %(levelname)s:\n%(message)s\n')

# Flask constructor takes the name of
# current module (__name__) as argument.
app = Flask(__name__)

def get_list_of_pokemons():
    response = requests.get("https://pokeapi.co/api/v2/pokemon?limit=5&offset=0")
    data = response.json()
    #print(data)
    return data

def get_random_number():
    from random import randint
    random_number = randint(0, 4)
    return random_number

def select_pokemon(data, number):
    basic_info = data['results'][number]
    name = basic_info['name']
    url  = basic_info['url']
    print(name, url, basic_info)
    return name, url, basic_info

def get_pokemon_info_from_api(name):
    url = f"https://pokeapi.co/api/v2/pokemon/{name}"
    response = requests.get(url)
    data = response.json()
    #print(data)
    cries = data['cries']
    weight = data['weight']
    experience = data['base_experience']
    print(cries, weight, experience)
    return cries, weight, experience

crud_ip= os.getenv("CRUD_IP")

def find_pokemon_in_db(name):
    url = f"http://{crud_ip}/mongodb"
    response = requests.get(url, params={"name": name})
    data = response.json()
    print("CRUD returned this:", data)
    return data

def insert_pokemon_into_db(item):
    url = f"http://{crud_ip}/mongodb"
    response = requests.post(
        url,
        json=item
    )
    if response.status_code == 200:
        data = response.json()
        print("Data successfully sent to the API:", data)
        return data
    else:
        print(f"Failed to send data. Status code: {response.status_code}, Response: {response.text}")
        return None

def retrieve_details_and_update(name, crud_response):
    if 'name' not in crud_response or crud_response['name'] != name:
        pokemon_details = get_pokemon_info_from_api(name)
        item = {
        "name": name,
        "cries": pokemon_details[0],
        "experience": pokemon_details[1],
        "weight": pokemon_details[2]
    }

        print("Answer:", item)
        print("Retrieved from the Pokemon API")
        insert_pokemon_into_db(item)
    else:
        item = crud_response
        print("Found in the DB")
    return item

# The route() function of the Flask class is a decorator,
# which tells the application which URL should call
# the associated function.
@app.route('/')
def base():
    return Response(response=json.dumps({"Status": "UP"}),
                    status=200,
                    mimetype='application/json')

@app.route('/pokemon', methods=['GET'])
def draw_pokemon():
    data = get_list_of_pokemons()
    number = get_random_number()
    pokemon_basics = select_pokemon(data, number)
    crud_response = find_pokemon_in_db(pokemon_basics[0])
    print(crud_response)
    pokemon_full_data = retrieve_details_and_update(pokemon_basics[0], crud_response)
    return Response(response=json.dumps(pokemon_full_data),
                    status=200,
                    mimetype='application/json')

# main driver function
if __name__ == '__main__':
    app.run(debug=True, port=5002, host='0.0.0.0')