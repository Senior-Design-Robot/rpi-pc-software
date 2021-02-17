from PIL import Image, ImageFilter

def main():
    
    image = Image.open('test.jpg')
    image = image.filter(ImageFilter.FIND_EDGES)
    image.save('imagef.jpg')


if __name__ == "__main__":
    main()
