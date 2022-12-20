import PIL
from PIL import Image, ImageEnhance, ImageFilter
import math
import random
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import wand
import cv2

def compute_diagonal(w,h):
    return math.sqrt(w**2 + h**2)

def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.

    The angle should be given in radians.

    Arguments:
        origin: The origin which is assumed
        point: a tuple containing x and y coordinates
        angle: rotate by angle in radian
    Returns:
        The tuple containing (x,y) which are transformed according to the angle given.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)

    return qx, qy


def add_margin(pil_img,
               points,
               color):
    """
    Adds margin around an image to have each image in a specific format.

    Arguments:
        pil_img: PIL image
        points: List containing the top,left, bottom and right boundaries
        color: fill the background by this color
    Returns:
        PIL Image
    """

    width, height = pil_img.size
    top, right, bottom, left = points[0], points[1], points[2], points[3]
    new_width = width + right + left
    new_height = height + top + bottom

    result = PIL.Image.new(pil_img.mode, (new_width, new_height), color)
    result.paste(pil_img, (left, top))
    return result


def paste_image(foreground,
                background,
                corner,
                rotateby,
                annotationspath,
                newannotationspath,
                image_output,
                flip="False"):
    """
        Function to paste an image on another image and change the annotations according to the new dimensions.

        Arguments:
            foreground - The foreground image
            background - The background image
            corner - position of the image [bottomright, bottomleft, topright, topleft, centre, random]
            rotateby - rotateby angle in radian
            annotationspath - path of annotations
            newannotationspath - path to where the annotations will be saved
            image_output,
            flip="False"
        Returns:
            Saves image to image_output path
    """
    f = open(annotationspath, "r")
    x_cord = []
    y_cord = []
    flag = []
    frontImage = PIL.Image.open(foreground)

    # for padding the image on top and bottom
    h1 = frontImage.height
    w1 = frontImage.width

    d = compute_diagonal(w1, h1)

    top = int((d - h1) // 2)
    bottom = int((d - h1) // 2)
    left = int((d - w1) // 2)
    right = int((d - w1) // 2)

    frontImage = add_margin(frontImage, [top, right, bottom, left], (0, 0, 0, 0))

    h1 = frontImage.height
    w1 = frontImage.width

    # Reading the coordinates
    for x in f:
        coordinates = x.split(" ")
        x_cord.append(coordinates[0])
        y_cord.append(coordinates[1])
        if len(coordinates) == 3:
            flag.append(coordinates[2])

    for j in range(len(x_cord)):
        x_cord[j] = int(x_cord[j].split(".")[0])
        y_cord[j] = int(y_cord[j].split(".")[0])

    if flip == "True":
        frontImage = frontImage.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        for u in range(len(x_cord)):
            ## for offsetting the new padding
            x_cord[u] = w1 - x_cord[u]

    origin = (w1 / 2, h1 / 2)
    for u in range(len(x_cord)):
        ## for offsetting the new padding
        x_cord[u] = x_cord[u] - right
        y_cord[u] = y_cord[u] + top

        ## To bring the y-axis from bottom to top
        x_cord[u] = x_cord[u]
        y_cord[u] = h1 - y_cord[u]

        ## rotating
        point = (x_cord[u], y_cord[u])
        x_cord[u], y_cord[u] = rotate(origin, point, math.radians(rotateby))

        ## forbringing the y axis to start from top to bottom
        x_cord[u] = x_cord[u]
        y_cord[u] = h1 - y_cord[u]

    # Open Background Image
    background = PIL.Image.open(background)

    # Convert image to RGBA
    frontImage = frontImage.convert("RGBA")
    frontImage = frontImage.rotate(rotateby)

    # Convert image to RGBA
    background = background.convert("RGBA")

    if frontImage.size[0]>background.size[0]:
        bgheight = background.size[1]

        oldsize = frontImage.size
        frontImage.thumbnail((bgheight-10, bgheight-10))
        newsize = frontImage.size
        print(oldsize,newsize)
        wratio = newsize[0] / oldsize[0]
        hratio = newsize[1] / oldsize[1]

        for u in range(len(x_cord)):
            ## for offsetting the new padding
            x_cord[u] = x_cord[u]*wratio
            y_cord[u] = y_cord[u]*hratio

    if corner == "bottomright":
        width = (background.width - frontImage.width)
        height = (background.height - frontImage.height)
    elif corner == "bottomleft":
        width = 0
        height = (background.height - frontImage.height)
    elif corner == "topright":
        width = (background.width - frontImage.width)
        height = 0
    elif corner == "topleft":
        width = 0
        height = 0
    elif corner == "centre":
        width = (background.width - frontImage.width) // 2
        height = (background.height - frontImage.height) // 2
    elif corner == "random":
        width = random.randint(0, (background.width - frontImage.width))
        height = random.randint(0, (background.height - frontImage.height))

    # Paste the frontImage at (width, height)
    background.paste(frontImage, (width, height), frontImage)

    x_ = []
    y_ = []
    for k in range(len(x_cord)):
        x_.append(x_cord[k] + width)
        y_.append(y_cord[k] + height)
    final = ""
    for z in range(18):
        final = final + str(x_[z]) + " " + str(y_[z]) + " " + str(flag[z])

    with open(newannotationspath, 'w') as f:
        f.write(final)

    # Save this image
    background.save(image_output, format="png")
    # background.show()


def plot_image(imagepath, annotationspath_):
    """
            Plots the annotations on the image.

            Arguments:
                Path to the image and annotations
            Returns:
                Shows a plot
        """
    f = open(annotationspath_, "r")
    x_cord = []
    y_cord = []
    for x in f:
        coordinates = x.split(" ")
        if len(coordinates) == 3 and coordinates[2] != "\n" and coordinates[2] == "1\n":
            x_cord.append(coordinates[0])
            y_cord.append(coordinates[1])
        for j in range(len(x_cord)):
            x_cord[j] = int(str(x_cord[j]).split(".")[0])
            y_cord[j] = int(str(y_cord[j]).split(".")[0])
    im = mpimg.imread(imagepath)
    implot = plt.imshow(im)
    plt.scatter([x_cord], [y_cord], c="yellow")
    # plt.savefig("/Users/aryan/Desktop/fd_dataset_creation/Yolov5/newtest.png")
    plt.show()


def rename_files(PROJECT_PATH,
                 foldername
                 ):
    folder_path = PROJECT_PATH + str(foldername)
    for filepath in os.listdir(folder_path):
        old_path = folder_path + "/" + str(filepath)
        new_path = folder_path + "/" + str(filepath[0:6]) + ".png"
        os.rename(old_path, new_path)

def inject_noise(filename, dest):
    with wand.image.Image(filename=filename) as img:
        img.noise("poisson", attenuate=0.99)
        img.save(filename=dest)

def color_transformation(filename, dest, color):
    if color == "yellow":
        nemo = cv2.imread(filename)
        nemo[..., 0] = 0
        cv2.imwrite(dest, nemo)
    if color == "blue":
        nemo = cv2.imread(filename)
        nemo[..., 1] = 0
        cv2.imwrite(dest, nemo)
    if color == "red":
        nemo = cv2.imread(filename)
        nemo[..., 2] = 0
        cv2.imwrite(dest, nemo)

def brighten_image(filename, dest):
    im = PIL.Image.open(filename)
    im = ImageEnhance.Brightness(im)
    im = im.enhance(2.0)
    im.save(dest)

def contrast_image(filename, dest):
    im = PIL.Image.open(filename)
    im = ImageEnhance.Contrast(im)
    im = im.enhance(2.0)
    im.save(dest)

def sharpen_image(filename, dest):
    im = PIL.Image.open(filename)
    im = ImageEnhance.Sharpness(im)
    im = im.enhance(2.0)
    im.save(dest)

def blur_image(filename, dest):
    im = PIL.Image.open(filename)
    im = im.filter(ImageFilter.BLUR)
    im.save(dest)