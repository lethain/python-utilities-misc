#!/usr/bin/python
# Scrapbook.py is a simple tool for taking images and generating
# scrapbook like images from them.
__VERSION__ = 0.1
__AUTHOR__ = "Will Larson <lethain@gmail.com> [lethain.com]"

from optparse import OptionParser
import Image, random, math

def border(img, borders=[(2, "White"), (8, "Black"), (1, "Grey")]):
    x,y = img.size
    width = sum([ z[0] for z in borders ])
    bordered = Image.new("RGB", (x+(2*width), y+(2*width)), "Grey")
    offset = 0
    for b_width, b_color in borders:
        bordered.paste(Image.new("RGB", (x+2*(width-offset), y+2*(width-offset)), b_color), (offset, offset))
        offset = offset + b_width
    bordered.paste(img, (offset, offset))
    return bordered

def mirror(img, n=2):
    x,y = img.size
    mirror_img = Image.new("RGB", (x*n,y), "White")
    for i in range(0, n):
        mirror_img.paste(img, (i*x,0))
    return mirror_img

def rotate(img, min=0, max=25):
    return img.copy().rotate(random.randint(min, max))
    
def normalize(imgs):
    "Normalize height for all images to shortest image."
    shortest = min([ x.size[1] for x in imgs ])
    resized = []
    for img in imgs:
        height_ratio = float(img.size[1]) / shortest
        new_width = img.size[0] * height_ratio
        img2 = img.resize((new_width, shortest), Image.ANTIALIAS)
        resized.append(img2)
    return resized
   
def chunk(imgs):
    "Break images into chunks equal to size of smallest image."
    smallest = min([ x.size[0] for x in imgs ])
    height = imgs[0].size[1]
    chunked_imgs = []
    for img in imgs:
        parts = math.ceil((img.size[0] * 1.0) / smallest)
        for i in xrange(0, parts):
            box = (i*smallest, 0, (i+1)*smallest, height)
            img2 = img.crop(box)
            img2.load()
            chunked_imgs.append(img2)
    return chunked_imgs

def merge(imgs, per_row=4):
    "Format equally sized images into rows and columns."
    width = imgs[0].size[0]
    height = imgs[0].size[1]
    page_width = width * per_row
    page_height = height * math.ceil((1.0*len(imgs)) / 4)
    page = Image.new("RGB", (page_width, page_height), "White")
    column = 0
    row = 0
    for img in imgs:
        if column != 0 and column % per_row == 0:
            row = row + 1
            column = 0
        pos = (width*column, height*row)
        page.paste(img, pos)
        column = column + 1
    return page

def album(imgs):
    imgs = normalize(imgs)
    imgs = chunk(imgs)
    imgs = [ border(x) for x in imgs ]
    return merge(imgs)

def main():
    p = OptionParser("usage: scrapbook.py image1.png image2.png image3.png")
    p.add_option('-w', '--width', dest='width', help='WIDTH of output', metavar='WIDTH')
    p.add_option('-h', '--height', dest='height', help='HEIGHT of output', metavar='HEIGHT')

if __name__ == '__main__':
    sys.exit(main())
