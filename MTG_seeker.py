# ---------- Imports

import argparse
import re
import requests
import os

# ---------- Functions

MTGAFormatRegex = r'(\d+)\s(.+)(?:\s\()(.+)(?:\))\s(\d+)'
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))


def readListFile(path):
    print('Loading ' + path + ' ...')
    f = open(path, 'r')
    return re.findall(MTGAFormatRegex, f.read())


# ---------- Argument parser

parser = argparse.ArgumentParser()

# Mandatory args
parser.add_argument('deckfile', type=str,
                    help='Path to the deck file (MTGA format).')
parser.add_argument('outputdir', type=str,
                    help='Path to output directory.')
args = parser.parse_args()


# ---------- Main script

URL = "https://api.scryfall.com/cards/named"

if not os.path.exists(args.outputdir):
    print("Folder " + args.outputdir + " does not exist: creating it...")
    os.makedirs(args.outputdir)

for line in readListFile(args.deckfile):
    number_of_copies = line[0]
    cardname = line[1]
    set_name = line[2]
    set_id = line[3] # unused atm as set_id can't be used with the API endpoint
    
    print("Fetch " + str(number_of_copies) + " copies of '" + cardname + "' from " + set_name + " (id = " + set_id + ")")

    request_params = {
        'exact': cardname,
        'version': 'png',
        'set': set_name,
    }

    # sending get request and saving the response in json format
    request_result = requests.get(url=URL, params=request_params).json()

    if 'image_uris' in request_result.keys():
        imageUrl = request_result['image_uris']['png']
        r = requests.get(imageUrl)
        with open(os.path.join(THIS_FOLDER, args.outputdir, str(number_of_copies) + ' ' + cardname + '.png'), 'wb') as f:
            f.write(r.content)
        
    elif 'card_faces' in request_result.keys():
        print("This is a double-faced card: printing both faces !")
        
        # print first face
        imageUrl = request_result['card_faces'][0]['image_uris']['png']
        r = requests.get(imageUrl)
        with open(os.path.join(THIS_FOLDER, args.outputdir, str(number_of_copies) + ' ' + cardname + ' ' + 'Face 1.png'), 'wb') as f:
            f.write(r.content)
        
        # print second face
        imageUrl = request_result['card_faces'][1]['image_uris']['png']
        r = requests.get(imageUrl)
        with open(os.path.join(THIS_FOLDER, args.outputdir, str(number_of_copies) + ' ' + cardname + ' ' + 'Face 2.png'), 'wb') as f:
            f.write(r.content)
        
    else:
        print("=> " + cardname + " not found ! Please get the card manually.")


# Retrieve HTTP meta-data
# print(r.status_code)
# print(r.headers['content-type'])
# print(r.encoding)
