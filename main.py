from PIL import Image, ImageOps, ImageEnhance, ImageFilter, ImageChops

def main():
    
    image = Image.open('test.jpg')
    image = image.convert("L")
    image = ImageOps.colorize(image, 'black', 'white', mid=None, blackpoint=0, whitepoint=255, midpoint = 127)
    image = image.filter(ImageFilter.FIND_EDGES)
    image = ImageChops.invert(image)
    image.save('imagef.jpg')


if __name__ == "__main__":
    main()
