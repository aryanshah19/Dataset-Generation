import os
import yaml
from helperfunctions import *

def read_config(filename):
    with open(filename, "r") as stream:
        try:
            string = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)

    data = {}
    for i in string["parameters"]:
        value = list(i.keys())[0]
        keys = list(i.values())[0]
        data[value] = keys

    if len(data)>0:
        print("Read the config file and saved successfully!\n\n")

    return data



class DatasetGeneration:

    def __init__(self,
                 data
                 # PROJECT_PATH = None,
                 # image_input_folder = None,
                 # image_output_folder = None,
                 # annotations_input_folder = None,
                 # annotations_output_folder = None,
                 # positionlist = [],
                 # fliplist = [],
                 # angle_boundaries = [],
                 # transformation = None,
                 # color = None,
                 # augmented_output_folder = None,
                 # background = None,
    ):
        self.PROJECT_PATH = data["PROJECT_PATH"]
        self.image_input_folder = str(data["image_input_folder"])
        self.image_output_folder = data["image_output_folder"]
        self.annotations_input_folder = data["annotations_input_folder"]
        self.annotations_output_folder = data["annotations_output_folder"]
        self.positionlist = data["positionlist"]
        self.fliplist = data["fliplist"]
        self.angle_boundaries = data["angle_boundaries"]
        self.transformation = data["transformation"]
        self.color = data["color"]
        self.augmented_output_folder = data["augmented_output_folder"]
        self.background = data["background"]

    def printvariables(self):
        print(
            self.PROJECT_PATH,
            self.image_input_folder,
            self.image_output_folder,
            self.annotations_input_folder,
            self.annotations_output_folder,
            self.positionlist,
            self.fliplist,
            self.angle_boundaries,
            self.transformation,
            self.color,
            self.augmented_output_folder,
            self.background
        )

    def generate_images(self,
                        PROJECT_PATH=None,
                        image_input_folder = None,
                        image_output_folder = None,
                        annotations_input_folder = None,
                        annotations_output_folder = None,
                        positionlist = None,
                        fliplist = None,
                        angle_boundaries = None,
                        background=None,
                        number_of_images = 5
                        ):
        PROJECT_PATH = self.PROJECT_PATH
        image_input_folder = self.image_input_folder
        image_output_folder = self.image_output_folder
        annotations_input_folder = self.annotations_input_folder
        annotations_output_folder = self.annotations_output_folder
        positionlist = self.positionlist
        fliplist = self.fliplist
        angle_boundaries = self.angle_boundaries
        background = self.background
        number_of_images = 5
        countangle = 0
        counttest = 0
        for i in range(angle_boundaries[0],angle_boundaries[1]):
            if i%15 == 0:
                countangle = countangle + 1
        totalimages = number_of_images * len(positionlist) * len(fliplist) * countangle
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
        print("Generating", totalimages, "images.....!\n\n")
        image_input_path = PROJECT_PATH + image_input_folder

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
                                stringangle = "["+ str(counttest + 1) +"/"+str(totalimages)+"] "
                                print(stringangle,"Generating",str(filepath[-10:-4]),"rotated by an angle of",
                                      angle, "positioned at",position+".")
                                counttest = counttest + 1
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
        print("Image generation complete!\n\n")




    def augment_images(self,
                       PROJECT_PATH = None,
                       image_input_folder = None,
                       image_output_folder = None,
                       transformation = None,
                       color=None
                       ):
        PROJECT_PATH = self.PROJECT_PATH
        image_input_folder = self.image_output_folder
        image_output_folder = self.augmented_output_folder
        transformation = self.transformation
        color = self.color

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
        print("Starting image augmentation!\n")

        image_input_path = PROJECT_PATH + str(image_input_folder)
        image_output_path = PROJECT_PATH + str(image_output_folder)
        # print(image_output_path)
        for filepath in sorted(os.listdir(image_input_path)):
            if filepath[-4:] == ".png":
                image_path = image_input_path + "/" + str(filepath)

                print("Augmenting", filepath[:6],"by introducing", transformation+".")

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
        print("Image Augmentation Complete!")


if __name__ == '__main__':


    ## Reading the configuration data
    configdata = read_config("config.yaml")

    ## Creating a class object
    newtest = DatasetGeneration(configdata)
    #newtest.printvariables()

    ## Generating the dataset
    newtest.generate_images(number_of_images=20)

    ## Augmenting the photos
    #newtest.augment_images()

    # Plotting the images to test
    # file = "im0056_15_bori_T"
    # imagepath = "/Users/aryan/Desktop/fd_dataset_creation/Yolov5/testimages/" + file + ".png"
    # test_anno = "/Users/aryan/Desktop/fd_dataset_creation/Yolov5/testannotations/" + file + ".txt"
    # plot_image(imagepath, test_anno)




