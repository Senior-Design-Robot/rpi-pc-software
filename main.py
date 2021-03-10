from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageChops
import serial
import time
import numpy
import cv2

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

if __name__ == "__main__":
    main()
