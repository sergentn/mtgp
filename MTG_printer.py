# Needs Python 3.6 at least
#
# Improvements TODO:
#   - allow cards with different pixel sizes (using bin packing / knapsack solving algos ?)
#   - refactor to remove global variables and make pure functions (use some classes ?)

# Bugs TODO:
#


#  ---------- Imports

import argparse
import re
import os
import threading

from PIL import Image

import Utilities


# ---------- Functions

#  used once to determine the sheets dimensions from a sample imput card
def getPxSheetDimensions(input_dir):

    directory = os.fsencode(input_dir)

    # get the width of the first card in the directory
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        filepath = os.path.join(input_dir, filename)

        with Image.open(filepath) as img:
            card_width_px, card_height_px = img.size  # height is unused atm
        break

    # use it to define sheet dimensions in pixels
    sheet_width_px = card_width_px * 100 / card_width_perc
    sheet_height_px = sheet_height_mm * sheet_width_px / sheet_width_mm
    
    return (sheet_width_px, sheet_height_px)


# create a new blank sheet with previously determined resolution
def createBlankSheet():

    blankSheet = Image.new('RGB', (int(sheet_width_px), int(sheet_height_px)), (255, 255, 255))  # white sheet
    return blankSheet


# save the sheet on the filesystem
def saveSheet(sheet, sheet_name):
    
    global swapped_dimensions
    
    if swapped_dimensions:
        sheet = sheet.rotate(90, expand=True)
    sheet.save(os.path.join(args.outputdir, sheet_name + '.png'), "PNG")


# return a tuple (x, y) indicating the line and column of the next card
def getLineAndColumnIndexes(current_card_idx, number_of_cards_per_line):
    
    line = int(current_card_idx / number_of_cards_per_line)
    column = int(current_card_idx % number_of_cards_per_line)

    return (line, column)


# print a sheet from a cardlist (thread function)
def printSheet(sheet_cardlist, sheet_name):
    
    current_card_idx = 0
    current_sheet = createBlankSheet()
    for card_path, number_of_copies in sheet_cardlist.items():
        current_card_idx = addCardsToSheet(current_sheet, card_path, number_of_copies, current_card_idx)
    saveSheet(current_sheet, sheet_name)


#  add the desired number of a same card to the sheets
def addCardsToSheet(sheet, card_path, number_of_copies, current_card_idx):
    
    global number_of_cards_per_line

    print(f'Printing {str(number_of_copies)} copies of {card_path}')
    card_image = Image.open(card_path)

    for i in range(number_of_copies):
        
        line_index, column_index = getLineAndColumnIndexes(current_card_idx, number_of_cards_per_line)
        current_card_idx += 1
        
        leftPosPx, topPosPx = getCardCoordinates(line_index, column_index)
        
        # the image position is determined by its upper left corner
        sheet.paste(card_image, (leftPosPx, topPosPx))
            
    return current_card_idx


# place one card on the sheet
def getCardCoordinates(line_index, column_index):

    global space_btw_lines_perc
    global space_btw_columns_perc
    global card_width_perc
    global sheet_width_px
    global card_height_perc
    global sheet_height_px

    leftPosPx = int(((space_btw_columns_perc * sheet_width_px / 100) + column_index *
                    ((space_btw_columns_perc * sheet_width_px / 100) + (card_width_perc * sheet_width_px / 100))))
    topPosPx = int(((space_btw_lines_perc * sheet_height_px / 100) + line_index *
                   ((space_btw_lines_perc * sheet_height_px / 100) + (card_height_perc * sheet_height_px / 100))))
    
    return (leftPosPx, topPosPx)


# ---------- Argument parser

parser = argparse.ArgumentParser()

# Mandatory args
parser.add_argument('inputdir', type=str,
                    help='Path to the input directory containing image files prefixed with their number of copies.')
parser.add_argument('outputdir', type=str,
                    help='Path to the output directory where printable sheets will be written.')
args = parser.parse_args()


# ---------- Main script

# Parameters
config = Utilities.IniLoader('settings.ini')

card_width_mm = int(config.getParam('dimensions', 'card_width_mm', 63))
card_height_mm = int(config.getParam('dimensions', 'card_height_mm', 88))

sheet_width_mm = int(config.getParam('dimensions', 'sheet_width_mm', 210))
sheet_height_mm = int(config.getParam('dimensions', 'sheet_height_mm', 297))

print(f'Printing cards of size: {card_width_mm}mm*{card_height_mm}mm on sheets of size: {sheet_width_mm}mm*{sheet_height_mm}mm (width*height)')

# ~ Determine global parameters

# Try to swap sheet's width and height and see if we can put more cards: if yes, swap
swapped_dimensions = False
if (int(sheet_width_mm / card_width_mm) * int(sheet_height_mm / card_height_mm) < int(sheet_height_mm / card_width_mm) * int(sheet_width_mm / card_height_mm)):
    sheet_width_mm, sheet_height_mm = sheet_height_mm, sheet_width_mm
    swapped_dimensions = True

number_of_cards_per_line = int(sheet_width_mm / card_width_mm)
number_of_cards_per_column = int(sheet_height_mm / card_height_mm)
number_of_cards_per_sheet = number_of_cards_per_line * number_of_cards_per_column

# For example, card_width_perc will be 30% for A4
card_width_perc = card_width_mm * 100 / sheet_width_mm
card_height_perc = card_height_mm * 100 / sheet_height_mm

# Compute spaces percentages
space_btw_lines_perc = (100 - (card_height_perc * number_of_cards_per_column)) / (number_of_cards_per_column + 1)
space_btw_columns_perc = (100 - (card_width_perc * number_of_cards_per_line)) / (number_of_cards_per_line + 1)

# Get sheet pixel size based on the first image resolution
sheet_width_px, sheet_height_px = getPxSheetDimensions(args.inputdir)


# ~ Read cards from filesystem

#  Create the output folder if it does not exist already
if not os.path.exists(args.outputdir):
    print(f'Folder {args.outputdir} does not exist: creating it...')
    os.makedirs(args.outputdir)

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

# we expect a number followed by a space in the card filename
number_of_copies_REGEX = r'(\d+)\s.+'
    
# Create the first sheet
current_card_idx = 0
current_sheet = createBlankSheet()
cards_to_print = {}

# Build the cards_to_print dictionary of (card_path, number_of_copies)
for cardFile in os.listdir(args.inputdir):

    filename = os.fsdecode(cardFile)
    
    filename_regex_result = re.match(number_of_copies_REGEX, filename)
    if (filename_regex_result != None):
        number_of_copies = filename_regex_result.group(1)
    else:
        print(f'No number of copies for {filename}, printing just one!')
        number_of_copies = "1"

    card_path = os.path.join(THIS_FOLDER, args.inputdir, cardFile)
    cards_to_print[card_path] = int(number_of_copies)


# ~ Build an array of sheets

current_number_of_cards = 0
current_sheet = {}
sheets_to_print = []

print(f'There will be {number_of_cards_per_sheet} cards per sheet.')

for card_path, number_of_copies in cards_to_print.items():
   
    if (current_number_of_cards + number_of_copies) <= number_of_cards_per_sheet:
        current_number_of_cards += number_of_copies
        current_sheet[card_path] = number_of_copies
        
    elif (current_number_of_cards + number_of_copies) > number_of_cards_per_sheet:
        difference = number_of_cards_per_sheet - current_number_of_cards
        current_sheet[card_path] = difference
        sheets_to_print.append(current_sheet)
        # start a new sheet with the rest of these cards to print
        current_number_of_cards = 0
        current_sheet = {}
        rest_to_print = cards_to_print[card_path] - difference
        current_sheet[card_path] = rest_to_print
        current_number_of_cards = rest_to_print
        
    if (current_number_of_cards == number_of_cards_per_sheet):
        sheets_to_print.append(current_sheet)
        # reset for next sheet
        current_number_of_cards = 0
        current_sheet = {}
        
# Add the last (incomplete) sheet
sheets_to_print.append(current_sheet)


# ~ Print cards on sheets using one thread per sheet

sheet_number = 0
for sheet in sheets_to_print:
    threading.Thread(target=printSheet, args=(sheet,str(sheet_number),)).start()
    sheet_number += 1