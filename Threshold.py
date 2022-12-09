from PIL import Image, ImageFilter
import math
import numpy as np
import time

def getGray(image):
        #grescale
    r,g,b,o = image.split()
    width = image.size[0]
    height = image.size[1]
    maxVal = 255

    # grayImage = Image.new( 'RGB', (width,height))
    # redChannelImage = Image.new( 'RGB', (width,height))
    greenChannelImage = Image.new( 'RGB', (width,height))
    # blueChannelImage = Image.new( 'RGB', (width,height))
    for x in range(0,width):
        for y in range(0,height):
            red = maxVal - r.getpixel((x, y))
            green = maxVal - g.getpixel((x, y))
            blue = maxVal - b.getpixel((x, y))
            gray = math.floor((red+green+blue)/3)
            # grayImage.putpixel((x,y), (gray, gray, gray))
            # redChannelImage.putpixel((x,y), (red, red, red))
            greenChannelImage.putpixel((x,y), (green, green, green))
            # blueChannelImage.putpixel((x,y), (blue, blue, blue))

    # grayImage.show()
    # redChannelImage.show()
    greenChannelImage.show()
    # blueChannelImage.show()
    return greenChannelImage


def getEdge(image):
    r,g,b,o = image.split()
    width = image.size[0]
    height = image.size[1]
    maxVal = 255
    wCut = 12
    hCut = 3

    grayImage = getGray(image)

    #Gaussian Filter
    grayGausImage = grayImage.filter(ImageFilter.GaussianBlur)
    grayGausImage.show()

    pix = np.array(grayGausImage)
    red = pix[:,:,0].astype(float)
    thresholdValue = 150 # getThreshold(red) 

    binaryImage = np.zeros(red.shape,dtype=int)

    for x in range(0,hCut):
        for y in range(0,wCut):
            thresholdValue = 0
            for i in range((int) (y * binaryImage.shape[0] / wCut), (int) ((y + 1) * binaryImage.shape[0] / wCut)):
                for j in range((int) (x * binaryImage.shape[1] / hCut), (int) ((x + 1) * binaryImage.shape[1] / hCut)):
                    thresholdValue += red[i,j]
            thresholdValue = (thresholdValue / (binaryImage.shape[0] * binaryImage.shape[1] / (wCut * hCut)))
            for i in range((int) (y * binaryImage.shape[0] / wCut), (int) ((y + 1) * binaryImage.shape[0] / wCut)):
                for j in range((int) (x * binaryImage.shape[1] / hCut), (int) ((x + 1) * binaryImage.shape[1] / hCut)):
                    if red[i,j] <= thresholdValue:
                        binaryImage[i,j] = 255
                    else:
                        binaryImage[i,j] = 0

    binaryImage = Image.fromarray(binaryImage).convert("L")
    binaryImage.show()

    edgeImage = binaryImage.filter(ImageFilter.Kernel((3, 3), (-1, -2, -1, -2, 12,
                                            -2, -1, -2, -1), 1, 0))
    
    edgeImage.show()
    return edgeImage


# prettyImage = Image.open(r"Coastline Segmentation\greyIsland.png")
# image = Image.open(r"Coastline Segmentation\map-view (2).png")
# grayClean = getGray(Image.open(r"Coastline Segmentation\Timelapse\red2021.png"))
grayClean = getGray(Image.open(r"Coastline Segmentation\Timelapse\red2009.png"))
prettyImage = grayClean
st = time.time()
lt = st
times = []

# for year in range(2001, 2022):
for year in range(2009, 2010):
    filename = "Coastline Segmentation\Timelapse\\red"
    filename += str(year)
    filename += ".png"
    print(filename)
    image = Image.open(filename)
    grayClean = getGray(Image.open(filename))
    grayClean.save("Coastline Segmentation\BinaryTimelapse\\"+str(year)+".png")


    r,g,b,o = image.split()
    width = image.size[0]
    height = image.size[1]
    maxVal = int((year-1994)/(2022-1994)*255)
    # print("maxVal: ", maxVal)

    edgeImage = getEdge(image)

    widthCut = 40
    widthAdd = 16
    heightCut = 20
    heightAdd = 12

    smallImage = Image.new( 'RGB', ((int)(width/widthCut),(int)(height/heightCut)))
    smallGray = Image.new( 'RGB', ((int)(width/widthCut),(int)(height/heightCut)))
    startX = -1
    startY = -1

    for x in range(0, (int)(width/widthCut)):
        for y in range(0, (int)(height/heightCut)):
            smallImage.putpixel((x, y), edgeImage.getpixel((x + (int)(width/widthCut*widthAdd), y + (int)(height/heightCut*heightAdd))))
            smallGray.putpixel((x, y), grayClean.getpixel((x + (int)(width/widthCut*widthAdd), y + (int)(height/heightCut*heightAdd))))
            if edgeImage.getpixel((x + (int)(width/widthCut*widthAdd), y + (int)(height/heightCut*heightAdd))) == 255:
                smallGray.putpixel((x, y), smallImage.getpixel((x, y)))
                startX = x + (int)(width/widthCut*widthAdd)
                startY = y + (int)(height/heightCut*heightAdd)


    if startX != -1 and startY != -1:
        worklist = [(startX, startY)]
        visited = []
        while len(worklist) > 0:
            (newX, newY) = worklist.pop()
            visited.append((newX, newY))
            for x in range(max(0, newX-1), min(newX+2, width)):
                for y in range(max(0, newY-1), min(newY+2, height)):
                    if not (x, y) in visited:
                        if edgeImage.getpixel((x, y)) == 255:
                            prettyImage.putpixel((x, y), maxVal)
                            grayClean.putpixel((x, y), 255)
                            if not (x, y) in worklist:
                                worklist.append((x, y))
        # prettyImage.show()
        grayClean.save("Coastline Segmentation\TimeTest\\"+str(year)+".png")
    else:
        print("Error: Edge not found in selected area")
        # edgeImage.show()
    # smallGray.show()
    et = time.time()
    print(year, " completed in ", et-lt, " seconds")
    times.append(et-lt)
    lt = et
prettyImage.show()
prettyImage.save("Coastline Segmentation\TimeTest\\timelapseLetsgo.png")

# print("Average time: ", sum(times)/len(times))



# saveImg = Image.new( 'RGB', (width,height))
# for i in range(0,width):
#     for j in range(0,height):
#         saveImg.putpixel((i,j), ((int)(binaryImage[j][i]), (int)(binaryImage[j][i]), (int)(binaryImage[j][i])))
# saveImg.show()
# grayImage.save("Coastline Segmentation/edgeIsland.png")





