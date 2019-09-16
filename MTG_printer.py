# Needs Python 3.6 at least
#
#
#  ---------- Imports

import argparse
import re

from PIL import Image

import os

# ---------- Functions

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))

sheetWidthPx = -1
sheetHeightPx = -1
cardWidthPx = -1

posCounter = 1
sheetNb = 1

cardWidthmm = 63
cardHeightmm = 88

sheetWidthmm = 210
sheetHeightmm = 297

cardWidthPerc = cardWidthmm * 100 / sheetWidthmm
cardHeightPerc = cardHeightmm * 100 / sheetHeightmm

externalMarginWidthPerc = 3
internalMarginWidthPerc = 2

topMarginHeightPerc = 3
middleMarginHeightPerc = 2

# number followed by space
NumberOfCopiesREGEX = r'(\d+)\s.+'

globalSheetCounter = 1


def getA4SheetDimensions(inputDir):

    directory = os.fsencode(inputDir)

    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        filepath = os.path.join(inputDir, filename)

        with Image.open(filepath) as img:
            cardWidthPx, cardHeightPx = img.size  # cardHeighPx unused

        break

    # TODO: change globals

    # cardWidthPerc = 30% for A4
    global sheetWidthPx 
    sheetWidthPx = cardWidthPx * 100 / cardWidthPerc
    global sheetHeightPx
    sheetHeightPx = sheetHeightmm * sheetWidthPx / sheetWidthmm
    print('Defined sheet dimensions :', sheetWidthPx, sheetHeightPx)

def createBlankA4Sheet():

    #print("Sheet width height: ", sheetWidthPx, sheetHeightPx)

    # convert -size "$sheetWidthPx"x"$sheetHeightPx" canvas:white -density 300 $TEMP_FOLDER/tempSheet.png
    blankA4Sheet = Image.new('RGB', (int(sheetWidthPx), int(sheetHeightPx)), (255, 255, 255)) # white sheet
    #blankA4Sheet.save("image.png", "PNG")
    return blankA4Sheet


def getNextLineColumn():

    global globalSheetCounter
    global currentCardIdx
    global currentA4Sheet

    if currentCardIdx == 9:
        currentCardIdx = 0
        #print("Write sheet now!")
        currentA4Sheet.save(os.path.join(args.outputdir, 'sheet_' + str(globalSheetCounter) + '.png'), "PNG")
        globalSheetCounter += 1
        currentA4Sheet = createBlankA4Sheet()
        

    line = int ( ( currentCardIdx / 3 ) )
    column = int(currentCardIdx % 3)

    #print('Next line column are:', currentCardIdx, line, column)

    currentCardIdx += 1

    return (line, column)

def addCards(cardFile, numberOfCopies):

    print("Cardfile: ", cardFile, 'Number of copies: ', numberOfCopies)

    cardImg = Image.open(cardFile)

    for i in range(int(numberOfCopies)):

        (line, column) = getNextLineColumn()
        placeCardOnA4Sheet(currentA4Sheet, cardImg, line, column)



def placeCardOnA4Sheet(A4Sheet, cardImage, lineIdx, columnIdx):

    line = lineIdx 
    column = columnIdx 
    global currentA4Sheet
    #print('Line, Column:', line, column)
    
    leftPosPx = int( ((externalMarginWidthPerc * sheetWidthPx / 100) + line * ((internalMarginWidthPerc * sheetWidthPx / 100) + (cardWidthPerc * sheetWidthPx / 100))) )
    topPosPx = int ( ((topMarginHeightPerc * sheetHeightPx / 100) + column * ((middleMarginHeightPerc * sheetHeightPx / 100) + (cardHeightPerc * sheetHeightPx / 100))) )

    currentA4Sheet.paste(cardImage, (leftPosPx, topPosPx) )


# ---------- Argument parser
parser = argparse.ArgumentParser()

# Mandatory args
parser.add_argument('inputdir', type=str,
                    help='Path to the folder containing image files (prefixed with their number of copies).')
parser.add_argument('outputdir', type=str,
                    help='Path to output directory for printable sheets.')
args = parser.parse_args()


# ---------- Main script

currentCardIdx = 0

# Also executes and set globals
print(getA4SheetDimensions(args.inputdir))

currentA4Sheet = createBlankA4Sheet()


for cardFile in os.listdir(args.inputdir):

    filename = os.fsdecode(cardFile)
    numberOfCopies = re.match(NumberOfCopiesREGEX, filename).group(1)

    filepath = os.path.join(THIS_FOLDER, args.inputdir, cardFile)
    
    addCards(filepath, numberOfCopies)

# Last sheet
currentA4Sheet.save(os.path.join(args.outputdir, 'sheet_' + str(globalSheetCounter) + '.png'), "PNG")