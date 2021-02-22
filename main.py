from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageChops
import serial
import time

def main():
    
    image = Image.open('test.jpg')
    image = image.convert("L")
    image = ImageOps.colorize(image, 'black', 'white', mid=None, blackpoint=0, whitepoint=255, midpoint = 127)
    image = image.filter(ImageFilter.FIND_EDGES)
    image = ImageChops.invert(image)
    image.save('imagef.jpg')
    
    nodeMCU = serial.Serial('/dev/ttyUSB0', 9600)
    time.sleep(2)

    while(1):
        var=input()

        if(var == '1'):
            nodeMCU.write('1'.encode())
            time.sleep(1)

        if(var == '0'):
            nodeMCU.write('0'.encode())
            time.sleep(1)

if __name__ == "__main__":
    main()
