#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from geopy.geocoders import Nominatim
import sys
import geocoder
from deep_translator import MyMemoryTranslator
import argparse


#def translate_text(text, target_language):
#    try:
#        translation = MyMemoryTranslator(source='finnish', target=target_language).translate(text)
#    except:
#        translation = text  # If translation fails, just use the original text
#    return translation

def translate_text(text, target_language):
    try:
        translation = MyMemoryTranslator(source='finnish', target=target_language).translate(text)
        return translation
    except Exception as e:
        print(f"Error in translation: {str(e)}")
        sys.exit()

try:
    parser = argparse.ArgumentParser(description="Get lunch menus from restaurants near a given location, translated into a given language.")
    parser.add_argument('-s', '--street', help='The street name of the location.')
    parser.add_argument('-l', '--language', default='english', help='The language in which you want the menu translated. Defaults to English if not specified.')
    parser.add_argument('-a', '--auto', action='store_true', help='Auto detect location based on IP.')
    parser.add_argument('-d', '--default', action='store_true', help='Run with default settings.')

    args = parser.parse_args()

    if args.default:
        args.auto = True
        args.language = 'english'

    if not args.street and not args.auto:
        parser.print_help()
        sys.exit(0)

    place = args.street if args.street else geocoder.ip('me').latlng  # use the street for place, if provided, else use geolocation based on IP
    target_language = args.language  # use the language provided

    geolocator = Nominatim(user_agent="MyApp")
    location = geolocator.geocode(place)

    url = 'https://www.lounaat.info/ajax/filter?'
    params = {
            'view':'lahella',
            'day':datetime.now().weekday()+1,
            'page':'0',
            'coords[lat]':str(location.latitude),
            'coords[lng]':str(location.longitude),
    }

    headers = {
            'Referer':'https://www.lounaat.info/',
    }

    r = requests.get(url, params=params, headers=headers)
    soup = BeautifulSoup(r.text, 'html.parser')

    print('\n')
    for x in soup:
            print('[!]',x.h3.text.upper(),'\n','-'*30)
            l = x.find_all('p', {'class':'dish'})
            for i in l:
                    # Translate the dish
                    translation = translate_text(i.text, target_language)
                    print(f"{i.text} (translated: {translation})")
            print('\n')

except KeyboardInterrupt:
    print('\nExecution interrupted by user. Goodbye!')
    sys.exit(0)
except Exception as err:
    print(f"Error: An error occurred. {err}")
