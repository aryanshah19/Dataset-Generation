import math
import PIL
from PIL import Image, ImageEnhance, ImageFilter
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import random
import os
import wand
import cv2
import yaml

with open("config.yaml", "r") as stream:
    try:
        string = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)

data = {}
for i in string["parameters"]:
    value = list(i.keys())[0]
    keys = list(i.values())[0]
    data[value] = keys

PROJECT_PATH = data["PROJECT_PATH"]
image_input_folder = data["image_input_folder"]
image_output_folder = data["image_output_folder"]
annotations_input_folder = data["annotations_input_folder"]
annotations_output_folder = data["annotations_output_folder"]
positionlist = data["positionlist"]
fliplist = data["fliplist"]
angle_boundaries = data["angle_boundaries"]
transformation = data["transformation"]
color = data["color"]
augmented_output_folder = data["augmented_output_folder"]
background = data["background"]


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
    top = (w1 - h1) // 2
    bottom = (w1 - h1) // 2
    frontImage = add_margin(frontImage, [top, 0, bottom, 0], (0, 0, 0, 0))
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
        x_cord[u] = x_cord[u]
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
                 foldername):
    folder_path = PROJECT_PATH + str(foldername)
    for filepath in os.listdir(folder_path):
        old_path = folder_path + "/" + str(filepath)
        new_path = folder_path + "/" + str(filepath[0:6]) + ".png"
        os.rename(old_path, new_path)


def generate_images(PROJECT_PATH = PROJECT_PATH,
                    image_input_folder = image_input_folder,
                    image_output_folder = image_output_folder,
                    annotations_input_folder = annotations_input_folder,
                    annotations_output_folder = annotations_output_folder,
                    positionlist = positionlist,
                    fliplist = fliplist,
                    angle_boundaries = angle_boundaries,
                    background = background,
                    number_of_images=5
                    ):
    """
       Generate augmented images

                Arguments:
                    PROJECT_PATH
                    image_input_folder,
                    image_output_folder,
                    annotations_input_folder,
                    annotations_output_folder,
                    positionlist - The list of positions
                    fliplist - The list of flips to be done {True, False}
                    angle_boundaries - List of lower bounds and upper
                                        bounds in angle in the form of a tuple
                    background - the background image
                    number_of_images - For testing purposes
                Returns:
                    Saves the images and annotations to the designated folders
            """
    position_shortnames = {"centre": "cent",
                           "topleft": "tole",
                           "topright": "tori",
                           "bottomleft": "bole",
                           "bottomright": "bori",
                           "random": "rand"}

    image_input_path = PROJECT_PATH + str(image_input_folder)

    q = 0
    for filepath in sorted(os.listdir(image_input_path)):

        if q != number_of_images:

            foreground = image_input_path + "/" + str(filepath)
            old_annotations_path = PROJECT_PATH + str(annotations_input_folder) + "/" + filepath[-10:-4] + ".txt"

            if filepath[-4:] == ".png":
                q = q + 1
                for angle in range(angle_boundaries[0], angle_boundaries[1], 15):
                    for position in positionlist:
                        for flip in fliplist:
                            image_output_path = PROJECT_PATH + str(image_output_folder) + "/"
                            annotations_output_path = PROJECT_PATH + str(annotations_output_folder) + "/"

                            uniquename = str(filepath[-10:-4]) + "_" + str(angle) + "_" + str(
                                position_shortnames[position]) + "_" + str(flip[0])

                            image_output_path = image_output_path + uniquename + ".png"
                            annotations_output_path = annotations_output_path + uniquename + ".txt"

                            paste_image(foreground,
                                        background,
                                        position,
                                        angle,
                                        old_annotations_path,
                                        annotations_output_path,
                                        image_output_path,
                                        flip=flip)


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


def augment_images(PROJECT_PATH,
                   image_input_folder,
                   image_output_folder,
                   transformation,
                   color=None
                   ):

    """
       Augment images with noise, blur, sharpening and contrasting

                Arguments:
                    PROJECT_PATH,
                   image_input_folder,
                   image_output_folder,
                   transformation - list of transformations
                   color - list of colors
                Returns:
                    Saves the images and annotations to the designated folders
     """

    image_input_path = PROJECT_PATH + str(image_input_folder)
    image_output_path = PROJECT_PATH + str(image_output_folder)
    # print(image_output_path)
    for filepath in sorted(os.listdir(image_input_path)):
        if filepath[-4:] == ".png":
            image_path = image_input_path + "/" + str(filepath)

            if transformation == "noise":
                output_path = image_output_path + "/" + str(transformation) + "_" + str(filepath)
                inject_noise(image_path, output_path)

            if transformation == "color":
                output_path = image_output_path + "/" + str(color[0]) + "_" + str(filepath)
                color_transformation(image_path, output_path, color)

            if transformation == "brightness":
                output_path = image_output_path + "/" + str(transformation[0:4]) + "_" + str(filepath)
                brighten_image(image_path, output_path)

            if transformation == "contrast":
                output_path = image_output_path + "/" + str(transformation[0:4]) + "_" + str(filepath)
                contrast_image(image_path, output_path)

            if transformation == "sharpness":
                output_path = image_output_path + "/" + str(transformation[0:4]) + "_" + str(filepath)
                sharpen_image(image_path, output_path)

            if transformation == "blur":
                output_path = image_output_path + "/" + str(transformation[0:4]) + "_" + str(filepath)
                blur_image(image_path, output_path)


class DatasetGeneration:
    def __init__(self, projectpath):
        self.projectpath = projectpath

    def PROJECT_PATH(self):
        return self.projectpath


if __name__ == '__main__':
    generate_images(number_of_images=4)
    # file = "im0059_75_rand_T"
    # imagepath = "/Users/aryan/Desktop/fd_dataset_creation/Yolov5/testimages/" + file + ".png"
    # test_anno = "/Users/aryan/Desktop/fd_dataset_creation/Yolov5/testannotations/" + file + ".txt"
    # plot_image(imagepath, test_anno)



