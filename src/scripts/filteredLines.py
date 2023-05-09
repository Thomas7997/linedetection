import cv2
import numpy as np
from matplotlib import pyplot as plt
from lib import test
import os
import lib.serial as serial
import nearest

# Setting operations for any type of line detection
HORIZONTAL = 0
VERTICAL = 1

DIST = 10
DIRECTION = VERTICAL

def getFilteredLines () :
	i = 0
	allLineChunks = []
	positions = []

	images = os.listdir("../samples")

	for image in images :
		contours = []
		img = cv2.imread(f'../samples/{image}')
		gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

		lineChunks = []

		# Setting threshold of gray image
		_, threshold = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

		contours, _ = cv2.findContours(threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		
		for contour in contours :
			if i == 0:
				i = 1
				continue

			approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)

			# Positions
			x = -1
			y = -1

			M = cv2.moments(contour)
			if M['m00'] != 0.0:
				x = int(M['m10']/M['m00'])
				y = int(M['m01']/M['m00'])

			# Detecting lines as rectangles
			if len(approx) == 4:
				positions.append([x,y])
				# Keeping the largest line chunks
				newApprox = approx[np.absolute(approx[0][0][DIRECTION]-approx[1][0][DIRECTION]) > DIST] # Depends on the chosen direction
				if (len(newApprox)>0) :
					lineChunks.append(newApprox)
					# Drawing the contour (red)
					print(f"Contour : {contour}")
					cv2.drawContours(img, [contour], 0, (0, 0, 255), 5)
					contours.append(contour)
		
		allLineChunks.append(lineChunks)

		nearest.drawNearest(img, contours)
		test.writeResult(img, 1)

	# Displaying the positions

	n = len(positions)

	if n > 20 :
		n = n // 10

	print(f"Positions : {positions[:n]}")
	print(f"Line chunks ({len(lineChunks)}) : {lineChunks}")

	serial.add(lineChunks)
	r = serial.get()
	print(f"Last record : {r}")