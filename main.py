from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageChops
import serial
import time
import numpy
import cv2

def main():

    image = Image.open('test.png')
    width, height = image.size
    image = image.convert("L")
    image = ImageOps.colorize(image, 'black', 'white', mid=None, blackpoint=0, whitepoint=255, midpoint = 127)
    image = image.filter(ImageFilter.GaussianBlur(2))
    image = image.filter(ImageFilter.FIND_EDGES)
    image = ImageChops.invert(image)
    image.save('imagef.jpg')
    temp = cv2.imread('test.png', 0)
    edges = cv2.Canny(temp, 1178, 1600)
    indecies = numpy.where(temp != [0])
    edgeCoords = list(zip(indecies[0], indecies[1]))
    print(coords)

if __name__ == "__main__":
    main()
