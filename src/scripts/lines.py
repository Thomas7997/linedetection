import cv2
import numpy as np
import sys
from . import nearest
from .lib import test, logger
import json
from .lib.convertDistances import convert

# Some basic parameters
MIN_Y_POSITION = 500
MIN_Y_RATE = 0.3

# For relative filenames
from pathlib import Path
source_path = Path(__file__).resolve()
basefolder = source_path.parent

def lowerLuminosity(image, gamma):
    inv_gamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
    return cv2.LUT(image, table)

def detect_line(img, filterType, minLength):
    # Get the size
    h, w, c = img.shape

    # Convert the image
    lum = lowerLuminosity(img, 0.45)
    grey = cv2.cvtColor(lum, cv2.COLOR_BGR2GRAY)
    vague = cv2.GaussianBlur(grey, (5, 5), 0)

    # Apply Canny
    contours = cv2.Canny(vague, 50, 150)

    # Detect the lines
    lines = cv2.HoughLinesP(contours, 1, np.pi / 180, 100, minLineLength=100, maxLineGap=10)

    finalLine = None

    # Draw the lines
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)

        nls = nearest.findNearest((h,w), lines, filterType, minLength)
        nls2 = list(nls)
        nls2.sort(key=lambda x : x['id'],reverse=False)

        if len(nls) > 0 :
            nl = nls[0]
            finalLine = nl
            nlps = nl['position']
            x1, y1, x2, y2 = nlps
            pt1 = nlps[0:2]
            pt2 = nlps[2:]
            cv2.line(img, pt1, pt2, (0, 0, 255), 3)

    if finalLine is not None :
        moves = finalLine['moves']
        mx = moves['horizontalMove']
        my1 = moves['firstVerticalDistance']
        my2 = moves['verticalDestination']

        # Store the result
        return (img, finalLine, (finalLine['xDirection']*convert(np.abs(mx), (w, 0)), convert(my1, (h, 1)), convert(my2, (h, 1))))
    else :
        return (img, finalLine, (0))