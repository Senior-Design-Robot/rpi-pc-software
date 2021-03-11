from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageChops
import serial
import time
import numpy
import cv2
import math

def main():

    temp = cv2.imread('teest2.jpg', cv2.IMREAD_UNCHANGED)
    blur = cv2.blur(temp, (5, 5))
    canny = cv2.Canny(blur, 30, 150)
    contours, _ = cv2.findContours(canny, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(canny, contours, -1, 255, 2)
    canny = 255 - canny

    cv2.imshow('Contours', canny)
    cv2.waitKey(0)
    cv2.imwrite('out.jpg', canny)

    averages = []
    moves = []

    for contour in contours:
        averages.append(cv2.mean(contour))

    currentMove = 0
    for point in averages:
        distances = []
        for point2 in averages:
            if point != point2:
                distances.append(distance(point2, point))
        while numpy.argmin(distances) in moves:
            distances.remove(distances[numpy.argmin(distances)])
        moves.append(numpy.argmin(distances))

    order = []
    order.append(0)
    currentContour=0

    for m in moves:
        order.append(moves[currentContour])
        currentContour = moves[currentContour]

    print(order)

def distance(p2, p1):
    return math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)

if __name__ == "__main__":
    main()
