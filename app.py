from flask import Flask, request, render_template
from dotenv import load_dotenv
from pprint import PrettyPrinter
import os
import requests

load_dotenv()

app = Flask(__name__, template_folder="templates", static_folder="static")
pp = PrettyPrinter(indent=4)

base = os.getenv('BASE_URL')
people = os.getenv('PEOPLE_ENDPOINT')

@app.route('/')
def homepage():
    """Star Wars API Landing page"""
    return render_template('index.html')


@app.route('/character', methods=['GET', 'POST'])
def show_character_details():
    """Shows the user the details of the character they chose."""
    if request.method == 'POST':
        character = request.form.get('character-id')
        full_url = people + character

        #concatenate url based on user input
        response = requests.get(full_url)
        
        #check status code and pass through error to template if not 200 OK
        if response.status_code != 200:
            context = {
                'status': response.status_code,
            }
        #otherwise we can gather our character information
        else:
            details = response.json()

        #set up and loop through film list url to get all film titles for character
            film_list = []
            for url in details['films']:
                film_response = requests.get(url)
                if film_response.status_code == 200:
                    film_details = film_response.json()
                    film_title = film_details['title']
                    #push each result into film list
                    film_list.append(film_title)
                else:
                    film_list = 'Error retrieving film list.'

            #grab homeworld url from response
            homeworld_url = details['homeworld']
            print(homeworld_url)

            #look up homeworld via API
            homeworld_response = requests.get(homeworld_url)
            print(homeworld_response)
            homeworld = ''
            homeworld_population = 0
            if homeworld_response.status_code == 200:
                homeworld_details = homeworld_response.json()
                homeworld = homeworld_details['name']
                homeworld_population = homeworld_details['population']
            else:
                homeworld = 'Error retrieving homeworld information.'

            #send all information through as context
            context = {
                'status': response.status_code,
                'name': details['name'],
                'height': details['height'],
                'mass': details['mass'],
                'hair': details['hair_color'],
                'eyes': details['eye_color'],
                'films': film_list,
                'homeworld': [homeworld, homeworld_population],
            }

    return render_template('character.html', **context)


if __name__ == '__main__':
    app.config['ENV'] = 'development'
    app.run(debug=True)
