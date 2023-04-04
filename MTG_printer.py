# Needs Python 3.6 at least
#
# Improvements TODO:
#   - multi-threading
#   - read desired cards and sheets dimensions from a parameters file (ini file)
#   - allow cards with different pixel sizes (using bin packing / knapsack solving algos ?)
#   - refactor to remove global variables and make pure functions

# Bugs TODO:
#


#  ---------- Imports

import argparse
import re
import os

from PIL import Image


# ---------- Parameters

#  TODO: read from a parameters file

card_width_mm = 63
card_height_mm = 88

sheet_width_mm = 210
sheet_height_mm = 297


#  ---------- Global variables

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

# we expect a number followed by a space in the card filename
number_of_copies_REGEX = r'(\d+)\s.+'


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
def saveSheet(sheet):
    
    global global_sheet_counter
    
    if swapped_dimensions:
        sheet = sheet.rotate(90, expand=True)
    sheet.save(os.path.join(args.outputdir, 'sheet_' + str(global_sheet_counter) + '.png'), "PNG")
    global_sheet_counter += 1


# return a tuple (x, y) indicating the line and column of the next card
def getLineAndColumnIndexes(current_card_idx, number_of_cards_per_line):
    
    line = int((current_card_idx / number_of_cards_per_line))
    column = int(current_card_idx % number_of_cards_per_line)

    return (line, column)


#  add the desired number of a same card to the sheets
def addCards(card_path, number_of_copies, current_card_idx):
    
    global number_of_cards_per_line
    global number_of_cards_per_sheet
    global current_sheet

    print("Printing " + number_of_copies + " copies of ", card_path)
    card_image = Image.open(card_path)

    for i in range(int(number_of_copies)):
        
        line_index, column_index = getLineAndColumnIndexes(current_card_idx, number_of_cards_per_line)
        current_card_idx += 1
        
        leftPosPx, topPosPx = getCardCoordinates(line_index, column_index)
        
        # the image position is determined by its upper left corner
        current_sheet.paste(card_image, (leftPosPx, topPosPx))
        
        # we have placed all the cards we could on this sheet : save it and start a new one
        if current_card_idx == number_of_cards_per_sheet:
            current_card_idx = 0
            saveSheet(current_sheet)
            current_sheet = createBlankSheet()
            
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

#  Create the output folder if it does not exist already
if not os.path.exists(args.outputdir):
    print("Folder " + args.outputdir + " does not exist: creating it...")
    os.makedirs(args.outputdir)
    
# Sheets counter
global_sheet_counter = 1
    
# Create the first sheet
current_card_idx = 0
current_sheet = createBlankSheet()

# Print all cards
for cardFile in os.listdir(args.inputdir):

    filename = os.fsdecode(cardFile)
    
    filename_regex_result = re.match(number_of_copies_REGEX, filename)
    if (filename_regex_result != None):
        number_of_copies = filename_regex_result.group(1)
    else:
        print("No number of copies for " + filename + ", printing just one!")
        number_of_copies = "1"

    card_path = os.path.join(THIS_FOLDER, args.inputdir, cardFile)
    current_card_idx = addCards(card_path, number_of_copies, current_card_idx)

# Save last sheet
saveSheet(current_sheet)