import xml.etree.ElementTree as ET
import collections
import cv2
import numpy as np
import pandas as pd
import sys

fileNames = ['00000-000', '00001-001', '00007-000', '00012-000']
trees = [ET.parse("{}.xml".format(name)) for name in fileNames]
roots = [tree.getroot() for tree in trees]
imgs = [cv2.imread(fileName+".jpg", 1) for fileName in fileNames]
#imgs = [cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2) for img in imgs]
# imgs[0] = base image
# imgs[1] = city name
# imgs[2] = character
# imgs[3] = licence number


df_first = pd.read_csv("./mapping_first_text_to_id.csv")
df_second = pd.read_csv("./mapping_second_text_to_id.csv")

accepted_city_list = df_first['text'].tolist()
accepted_char_list = df_second['text'].tolist()
accepted_char_list = [x.lower() for x in accepted_char_list if str(x)!='nan']
accepted_city_list = [x.lower() for x in accepted_city_list if str(x)!='nan']

#accepted_char_list = ['au', 'ba', 'bha', 'caa', 'cha', 'da', 'daw', 'dha', 'e', 'fa', 'ga', 'gha', 'ha', 'ja', 'jha', 'ka', 'kha', 'la', 'ma', 'pa', 'ra', 'sa', 'sha', 'ta', 'taw', 'tha', 'u', 'wua', 'za']
#accepted_city_list = ['b.baria', 'bagerhat', 'bandarban', 'barguna', 'barisal', 'barisal metro', 'bhola', 'bogra', 'chandpur', 'chatta-metro', 'chatta metro', 'chittagong', 'chuadanga', 'comilla', 'coxsbazar', 'dhaka', 'dhaka-metro', 'dhaka metro', 'dinajpur', 'faridpur', 'feni', 'gaibanda', 'gaibandha', 'gazipur', 'gopalganj', 'habigong', 'jaipurhat', 'jessore', 'jhalakati', 'jhenidah', 'jhenidha', 'khagrachari', 'khulna', 'khulna-metro', 'khulna metro', 'kishoreganj', 'kurigram', 'kushtia', 'lakshmipur', 'laxmipur', 'lalmonirhat', 'madaripur', 'magura', 'manikganj', 'meherpur', 'moulavibazar', 'moulvibazar', 'munshiganj', 'mymensingh', 'naogaon', 'narail', 'narayanganj', 'narsingdi', 'nator', 'natore', 'nawabganj', 'netrakona', 'nilphamari', 'noakhali', 'pabna', 'panchagar', 'patuakhali', 'potuakhali', 'pirojpur', 'rajbari', 'raj-metro', 'raj metro', 'rajshahi', 'rangamati', 'rangpur', 'satkhira', 'shariatpur', 'sherpur', 'sirajgong', 'sirajgonj', 'sunamgonj', 'sylhet', 'sylhet-metro', 'sylhet metro', 'tangail', 'thakurgaon']

print(accepted_char_list)
print(accepted_city_list)

sys.exit(0)

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


city_image = imgs[1][source_coordinates["city"]["ymin"]:source_coordinates["city"]["ymax"], \
					source_coordinates["city"]["xmin"]:source_coordinates["city"]["xmax"]]
char_image = imgs[2][source_coordinates["char"]["ymin"]:source_coordinates["char"]["ymax"], \
					source_coordinates["char"]["xmin"]:source_coordinates["char"]["xmax"]]
number_image = imgs[3][source_coordinates["number"]["ymin"]:source_coordinates["number"]["ymax"], \
					source_coordinates["number"]["xmin"]:source_coordinates["number"]["xmax"]]

cropped_images = {"city": city_image, "char": char_image, "number": number_image}

new_image = imgs[0]

for segment_name in base_coordinates:
	base_shape_width = base_coordinates[segment_name]["xmax"]-base_coordinates[segment_name]["xmin"]
	base_shape_height = base_coordinates[segment_name]["ymax"]-base_coordinates[segment_name]["ymin"]
	
	shape_converted = cv2.resize(cropped_images[segment_name], (base_shape_width, base_shape_height))
	new_image[base_coordinates[segment_name]["ymin"]:base_coordinates[segment_name]["ymax"], \
					base_coordinates[segment_name]["xmin"]:base_coordinates[segment_name]["xmax"]] \
					= shape_converted

cv2.imshow('city', new_image)
cv2.waitKey(0)
cv2.destroyAllWindows()

cv2.imwrite("merged_img.jpg", new_image)

trees[0].write('merged_img.xml')