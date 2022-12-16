from main import DatasetGeneration
from main import *
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






