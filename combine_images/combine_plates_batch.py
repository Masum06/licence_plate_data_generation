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


source_path = "good_images"
dest_path = "merged_images"
dest_path2 = "binary_images"

dirlist = os.listdir("./")
if dest_path not in dirlist:
	os.mkdir(dest_path)
	os.mkdir(dest_path2)

os.chdir(source_path)
files = glob.glob('*.jpg')
xml_files = glob.glob('*.xml')
files = [file[:-4] for file in files]
xml_files = [file[:-4] for file in xml_files]
files = list(set(files) & set(xml_files))
number_of_old_image = len(files)

number_of_new_image = int(sys.argv[1])


for i in range(number_of_new_image):
	np.random.seed(10+i) #int(time.time())%100000
	fileNames = [files[np.random.randint(0, number_of_old_image-1)] for j in range(4)]
	trees = [ET.parse("{}.xml".format(name)) for name in fileNames]
	roots = [tree.getroot() for tree in trees]
	imgs = [cv2.imread(fileName+".jpg", 1) for fileName in fileNames]
	grey = [cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) for img in imgs]
	bin_imgs = [cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2) \
					for img in grey]
	# imgs[0] = base image
	# imgs[1] = city name
	# imgs[2] = character
	# imgs[3] = licence number

	base_coordinates = {}
	source_coordinates = {}

	for child in roots[1].findall('object'):
		name = child.find('name')
		text = name.text.lower()
		if text in accepted_city_list:
			city_name = text
			xmin = int(child.find('bndbox')[0].text)
			ymin = int(child.find('bndbox')[1].text)
			xmax = int(child.find('bndbox')[2].text)
			ymax = int(child.find('bndbox')[3].text)
			source_coordinates["city"] = {"xmin":xmin, "ymin":ymin, "xmax":xmax, "ymax": ymax}

	for child in roots[2].findall('object'):
		name = child.find('name')
		text = name.text.lower()
		if text in accepted_char_list:
			char = text
			xmin = int(child.find('bndbox')[0].text)
			ymin = int(child.find('bndbox')[1].text)
			xmax = int(child.find('bndbox')[2].text)
			ymax = int(child.find('bndbox')[3].text)
			source_coordinates["char"] = {"xmin":xmin, "ymin":ymin, "xmax":xmax, "ymax": ymax}

	for child in roots[3].findall('object'):
		name = child.find('name')
		text = name.text.lower()
		if text[:6] == 'number':
			number = text
			xmin = int(child.find('bndbox')[0].text)
			ymin = int(child.find('bndbox')[1].text)
			xmax = int(child.find('bndbox')[2].text)
			ymax = int(child.find('bndbox')[3].text)
			source_coordinates["number"] = {"xmin":xmin, "ymin":ymin, "xmax":xmax, "ymax": ymax}


	for child in roots[0].findall('object'):
		name = child.find('name')
		text = name.text
		if text in accepted_city_list:
			xmin = int(child.find('bndbox')[0].text)
			ymin = int(child.find('bndbox')[1].text)
			xmax = int(child.find('bndbox')[2].text)
			ymax = int(child.find('bndbox')[3].text)
			base_coordinates["city"] = {"xmin":xmin, "ymin":ymin, "xmax":xmax, "ymax": ymax}
			name.text = city_name
		elif text in accepted_char_list:
			xmin = int(child.find('bndbox')[0].text)
			ymin = int(child.find('bndbox')[1].text)
			xmax = int(child.find('bndbox')[2].text)
			ymax = int(child.find('bndbox')[3].text)
			base_coordinates["char"] = {"xmin":xmin, "ymin":ymin, "xmax":xmax, "ymax": ymax}
			name.text = char
		elif text[:6] == 'number':
			xmin = int(child.find('bndbox')[0].text)
			ymin = int(child.find('bndbox')[1].text)
			xmax = int(child.find('bndbox')[2].text)
			ymax = int(child.find('bndbox')[3].text)
			base_coordinates["number"] = {"xmin":xmin, "ymin":ymin, "xmax":xmax, "ymax": ymax}
			name.text = number

	if len(source_coordinates)!=3 or len(base_coordinates)!=3:
		i-=1
		continue

	city_image = imgs[1][source_coordinates["city"]["ymin"]:source_coordinates["city"]["ymax"], \
						source_coordinates["city"]["xmin"]:source_coordinates["city"]["xmax"]]
	char_image = imgs[2][source_coordinates["char"]["ymin"]:source_coordinates["char"]["ymax"], \
						source_coordinates["char"]["xmin"]:source_coordinates["char"]["xmax"]]
	number_image = imgs[3][source_coordinates["number"]["ymin"]:source_coordinates["number"]["ymax"], \
						source_coordinates["number"]["xmin"]:source_coordinates["number"]["xmax"]]


	bin_city_image = bin_imgs[1][source_coordinates["city"]["ymin"]:source_coordinates["city"]["ymax"], \
						source_coordinates["city"]["xmin"]:source_coordinates["city"]["xmax"]]
	bin_char_image = bin_imgs[2][source_coordinates["char"]["ymin"]:source_coordinates["char"]["ymax"], \
						source_coordinates["char"]["xmin"]:source_coordinates["char"]["xmax"]]
	bin_number_image = bin_imgs[3][source_coordinates["number"]["ymin"]:source_coordinates["number"]["ymax"], \
						source_coordinates["number"]["xmin"]:source_coordinates["number"]["xmax"]]

	cropped_images = {"city": city_image, "char": char_image, "number": number_image}
	bin_cropped_images = {"city": bin_city_image, "char": bin_char_image, "number": bin_number_image}

	new_image = imgs[0]
	bin_image = bin_imgs[0]

	for segment_name in base_coordinates:
		base_shape_width = base_coordinates[segment_name]["xmax"]-base_coordinates[segment_name]["xmin"]
		base_shape_height = base_coordinates[segment_name]["ymax"]-base_coordinates[segment_name]["ymin"]
		
		shape_converted = cv2.resize(cropped_images[segment_name], (base_shape_width, base_shape_height))
		new_image[base_coordinates[segment_name]["ymin"]:base_coordinates[segment_name]["ymax"], \
						base_coordinates[segment_name]["xmin"]:base_coordinates[segment_name]["xmax"]] \
						= shape_converted

		bin_shape_converted = cv2.resize(bin_cropped_images[segment_name], (base_shape_width, base_shape_height))
		bin_image[base_coordinates[segment_name]["ymin"]:base_coordinates[segment_name]["ymax"], \
						base_coordinates[segment_name]["xmin"]:base_coordinates[segment_name]["xmax"]] \
						= bin_shape_converted

	# cv2.imshow('city', new_image)
	# cv2.waitKey(0)
	# cv2.destroyAllWindows()

	# grey = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)
	# binary = cv2.adaptiveThreshold(grey, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
	
	cv2.imwrite("../{}/merged_img_{}.jpg".format(dest_path, i), new_image)
	trees[0].write('../{}/merged_img_{}.xml'.format(dest_path, i))

	cv2.imwrite("../{}/bin_merged_{}.jpg".format(dest_path2, i), bin_image)
	trees[0].write('../{}/bin_merged_{}.xml'.format(dest_path2, i))
