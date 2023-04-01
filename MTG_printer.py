# Needs Python 3.6 at least
#
# Improvements TODO:
#   - read desired cards and sheets dimensions from a parameters file
#   - allow cards with different pixel sizes
#   - allow sheets of any format, other than A4
#   - refactor to remove global variables

# Bugs TODO:
#   - an incorrectly named card stops the script (regex error)


#  ---------- Imports

import argparse
import re
import os

from PIL import Image


# ---------- Global variables

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

sheet_width_px = -1
sheet_height_px = -1
card_width_px = -1

posCounter = 1
sheetNb = 1

#  TODO: read from a parameters file

card_width_mm = 63
card_height_mm = 88

sheet_width_mm = 210
sheet_height_mm = 297

# card_width_perc = 30% for A4
card_width_perc = card_width_mm * 100 / sheet_width_mm
card_height_perc = card_height_mm * 100 / sheet_height_mm

external_margin_width_perc = 3
internal_margin_width_perc = 2

top_margin_height_perc = 3
middle_margin_height_perc = 2

# number followed by a space
number_of_copies_REGEX = r'(\d+)\s.+'

global_sheet_counter = 1


# ---------- Functions

# used once to determine the sheets dimensions from a sample imput card
def setA4SheetDimensions(inputDir):

    directory = os.fsencode(inputDir)

    # get the width of the first card in the directory
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        filepath = os.path.join(inputDir, filename)

        with Image.open(filepath) as img:
            card_width_px, card_height_px = img.size  # height is unused atm

        break

    # use it to define sheet dimensions in pixels
    global sheet_width_px
    sheet_width_px = card_width_px * 100 / card_width_perc
    global sheet_height_px
    sheet_height_px = sheet_height_mm * sheet_width_px / sheet_width_mm

    print('Defined sheet dimensions :', sheet_width_px, sheet_height_px)


# create a new blank sheet with previously determined resolution
def createBlankA4Sheet():

    blankA4Sheet = Image.new('RGB', (int(sheet_width_px), int(sheet_height_px)), (255, 255, 255))  # white sheet
    return blankA4Sheet


# return a tuple (x, y) indicating the line and column of the next card
def getNextLineAndColumnIndexes():

    global global_sheet_counter
    global currentCardIdx
    global current_A4_sheet

    # we have placed 9 cards : save the sheet and create a new blank one
    if currentCardIdx == 9:
        currentCardIdx = 0
        current_A4_sheet.save(os.path.join(
            args.outputdir, 'sheet_' + str(global_sheet_counter) + '.png'), "PNG")
        global_sheet_counter += 1
        current_A4_sheet = createBlankA4Sheet()

    line = int((currentCardIdx / 3))
    column = int(currentCardIdx % 3)

    currentCardIdx += 1

    return (line, column)


# add the desired number of a same card to the sheets
def addCards(card_path, number_of_copies):

    print("Cardfile: ", card_path, '\t-> Number of copies: ', number_of_copies)
    card_image = Image.open(card_path)

    for i in range(int(number_of_copies)):
        (line_index, column_index) = getNextLineAndColumnIndexes()
        placeCardOnA4Sheet(current_A4_sheet, card_image, line_index, column_index)


# place one card on the sheet
def placeCardOnA4Sheet(A4_sheet, card_image, line_index, column_index):

    line = line_index
    column = column_index
    global current_A4_sheet

    leftPosPx = int(((external_margin_width_perc * sheet_width_px / 100) + line *
                    ((internal_margin_width_perc * sheet_width_px / 100) + (card_width_perc * sheet_width_px / 100))))
    topPosPx = int(((top_margin_height_perc * sheet_height_px / 100) + column *
                   ((middle_margin_height_perc * sheet_height_px / 100) + (card_height_perc * sheet_height_px / 100))))
    
    # the image position is determined by its upper left corner
    A4_sheet.paste(card_image, (leftPosPx, topPosPx))


# ---------- Argument parser
parser = argparse.ArgumentParser()

# Mandatory args
parser.add_argument('inputdir', type=str,
                    help='Path to the input directory containing image files prefixed with their number of copies.')
parser.add_argument('outputdir', type=str,
                    help='Path to the output directory where printable sheets will be written.')
args = parser.parse_args()


# ---------- Main script
currentCardIdx = 0

if not os.path.exists(args.outputdir):
    print("Folder " + args.outputdir + " does not exist: creating it...")
    os.makedirs(args.outputdir)

# Set globals based on the first image resolution
setA4SheetDimensions(args.inputdir)

# Create the first sheet
current_A4_sheet = createBlankA4Sheet()

# Print all cards
for cardFile in os.listdir(args.inputdir):

    filename = os.fsdecode(cardFile)
    number_of_copies = re.match(number_of_copies_REGEX, filename).group(1)
    card_path = os.path.join(THIS_FOLDER, args.inputdir, cardFile)
    addCards(card_path, number_of_copies)

# Save last sheet
current_A4_sheet.save(os.path.join(args.outputdir, 'sheet_' +
                    str(global_sheet_counter) + '.png'), "PNG")
