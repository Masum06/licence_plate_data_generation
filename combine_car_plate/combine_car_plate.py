# How to run:
# python combine_plates_batch.py $number_of_output_image

import xml.etree.ElementTree as ET
import collections
import cv2
import numpy as np
import pandas as pd
import sys
import glob
import os
from random import randint
import time

df_first = pd.read_csv("./mapping_first_text_to_id.csv")
df_second = pd.read_csv("./mapping_second_text_to_id.csv")

accepted_city_list = df_first['text'].tolist()
accepted_char_list = df_second['text'].tolist()
accepted_char_list = [x.lower() for x in accepted_char_list if str(x)!='nan']
accepted_city_list = [x.lower() for x in accepted_city_list if str(x)!='nan']

#accepted_char_list = ['au', 'ba', 'bha', 'caa', 'cha', 'da', 'daw', 'dha', 'e', 'fa', 'ga', 'gha', 'ha', 'ja', 'jha', 'ka', 'kha', 'la', 'ma', 'pa', 'ra', 'sa', 'sha', 'ta', 'taw', 'tha', 'u', 'wua', 'za']
#accepted_city_list = ['b.baria', 'bagerhat', 'bandarban', 'barguna', 'barisal', 'barisal metro', 'bhola', 'bogra', 'chandpur', 'chatta-metro', 'chatta metro', 'chittagong', 'chuadanga', 'comilla', 'coxsbazar', 'dhaka', 'dhaka-metro', 'dhaka metro', 'dinajpur', 'faridpur', 'feni', 'gaibanda', 'gaibandha', 'gazipur', 'gopalganj', 'habigong', 'jaipurhat', 'jessore', 'jhalakati', 'jhenidah', 'jhenidha', 'khagrachari', 'khulna', 'khulna-metro', 'khulna metro', 'kishoreganj', 'kurigram', 'kushtia', 'lakshmipur', 'laxmipur', 'lalmonirhat', 'madaripur', 'magura', 'manikganj', 'meherpur', 'moulavibazar', 'moulvibazar', 'munshiganj', 'mymensingh', 'naogaon', 'narail', 'narayanganj', 'narsingdi', 'nator', 'natore', 'nawabganj', 'netrakona', 'nilphamari', 'noakhali', 'pabna', 'panchagar', 'patuakhali', 'potuakhali', 'pirojpur', 'rajbari', 'raj-metro', 'raj metro', 'rajshahi', 'rangamati', 'rangpur', 'satkhira', 'shariatpur', 'sherpur', 'sirajgong', 'sirajgonj', 'sunamgonj', 'sylhet', 'sylhet-metro', 'sylhet metro', 'tangail', 'thakurgaon']


plate_path = "plates"
car_path = "cars"
dest_path = "merged_images"


dirlist = os.listdir("./")
if dest_path not in dirlist:
	os.mkdir(dest_path)

os.chdir(car_path)
car_images = glob.glob('*.jpg')
car_xmls = glob.glob('*.xml')
os.chdir("..")
os.chdir(plate_path)
plate_images = glob.glob('*.jpg')
plate_xmls = glob.glob('*.xml')
os.chdir("..")

car_images = [file[:-4] for file in car_images]
plate_images = [file[:-4] for file in plate_images]
car_xmls = [file[:-4] for file in car_xmls]
plate_xmls = [file[:-4] for file in plate_xmls]

car_images = list(set(car_images) & set(car_xmls))
plate_images = list(set(plate_images) & set(plate_xmls))
number_of_cars = len(car_images)
number_of_plates = len(plate_images)

number_of_new_image = int(sys.argv[1])


for i in range(number_of_new_image):
	np.random.seed(10+i)
	car_name = car_images[np.random.randint(0, number_of_cars)]
	plate_name = plate_images[np.random.randint(0, number_of_plates)]

	car_tree = ET.parse("{}/{}.xml".format(car_path, car_name))
	plate_tree = ET.parse("{}/{}.xml".format(plate_path, plate_name))

	car_root = car_tree.getroot()
	plate_root = plate_tree.getroot()

	car_img = cv2.imread(car_path+"/"+car_name+".jpg", 1)
	plate_img = cv2.imread(plate_path+"/"+plate_name+".jpg", 1)

	car_coordinates = {}
	plate_coordinates = {}

	##############################33

	## plates
	for child in car_root.findall('object'):
		name = child.find('name')
		text = name.text.lower()
		if text == "plate":
			xmin = int(child.find('bndbox')[0].text)
			ymin = int(child.find('bndbox')[1].text)
			xmax = int(child.find('bndbox')[2].text)
			ymax = int(child.find('bndbox')[3].text)
			car_coordinates = {"xmin":xmin, "ymin":ymin, "xmax":xmax, "ymax": ymax}

	for child in plate_root.findall('object'):
		name = child.find('name')
		text = name.text.lower()
		if text in accepted_city_list:
			name.text = "city"
			xmin = int(child.find('bndbox')[0].text)
			ymin = int(child.find('bndbox')[1].text)
			xmax = int(child.find('bndbox')[2].text)
			ymax = int(child.find('bndbox')[3].text)
			child.find('bndbox')[0].text = str(xmin+car_coordinates["xmin"])
			child.find('bndbox')[1].text = str(ymin+car_coordinates["ymin"])
			child.find('bndbox')[2].text = str(xmax+car_coordinates["xmax"])
			child.find('bndbox')[3].text = str(ymax+car_coordinates["ymax"])
			# add child to car_root
			car_root.append(child)
			

	for child in plate_root.findall('object'):
		name = child.find('name')
		text = name.text.lower()
		if text in accepted_char_list:
			name.text = "char"
			xmin = int(child.find('bndbox')[0].text)
			ymin = int(child.find('bndbox')[1].text)
			xmax = int(child.find('bndbox')[2].text)
			ymax = int(child.find('bndbox')[3].text)
			child.find('bndbox')[0].text = str(xmin+car_coordinates["xmin"])
			child.find('bndbox')[1].text = str(ymin+car_coordinates["ymin"])
			child.find('bndbox')[2].text = str(xmax+car_coordinates["xmax"])
			child.find('bndbox')[3].text = str(ymax+car_coordinates["ymax"])
			car_root.append(child)

	for child in plate_root.findall('object'):
		name = child.find('name')
		text = name.text.lower()
		if text[:6] == 'number':
			name.text = "number"
			xmin = int(child.find('bndbox')[0].text)
			ymin = int(child.find('bndbox')[1].text)
			xmax = int(child.find('bndbox')[2].text)
			ymax = int(child.find('bndbox')[3].text)
			child.find('bndbox')[0].text = str(xmin+car_coordinates["xmin"])
			child.find('bndbox')[1].text = str(ymin+car_coordinates["ymin"])
			child.find('bndbox')[2].text = str(xmax+car_coordinates["xmax"])
			child.find('bndbox')[3].text = str(ymax+car_coordinates["ymax"])
			car_root.append(child)

	#print(ET.tostring(car_root, encoding='utf8').decode('utf8'))
	#sys.exit(0)

	# if len(source_coordinates)!=3 or len(base_coordinates)!=3:
	# 	i-=1
	# 	continue


	base_shape_width = car_coordinates["xmax"]-car_coordinates["xmin"]
	base_shape_height = car_coordinates["ymax"]-car_coordinates["ymin"]

	plate_converted = cv2.resize(plate_img, (base_shape_width, base_shape_height))
	car_img[car_coordinates["ymin"]:car_coordinates["ymax"], \
			car_coordinates["xmin"]:car_coordinates["xmax"]] \
			= plate_converted


	# display = cv2.resize(car_img, (int(car_img.shape[1]*0.5), int(car_img.shape[0]*0.5)))
	# cv2.imshow('city', display)
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()

	#sys.exit(0)

	# grey = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)
	# binary = cv2.adaptiveThreshold(grey, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
	
	cv2.imwrite("{}/merged_img_{}.jpg".format(dest_path, i), car_img)
	car_tree.write('{}/merged_img_{}.xml'.format(dest_path, i))
