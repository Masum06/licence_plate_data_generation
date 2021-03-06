import xml.etree.ElementTree as ET
import collections
import glob
import os

source_path = "plates"
dest_path = "plates_updated"
os.chdir(source_path)
files = glob.glob('*.xml')

for file in files:
	print(file)
	tree = ET.parse(file)
	root = tree.getroot()

	accepted_list = ["{}".format(i) for i in range(10)]

	position_to_number = {}
	for child in root.findall('object'):
		text = child.find('name').text
		if text in accepted_list:
			#root.remove(child)
			x_pos = int(float(child.find('bndbox').find('xmin').text))
			position_to_number[x_pos] = text

	position_to_number_sorted = collections.OrderedDict(sorted(position_to_number.items()))
	plate_number = "number_"

	for key in position_to_number_sorted:
		plate_number+=position_to_number_sorted[key]

	for child in root.findall('object'):
		name = child.find('name')
		text = name.text
		if text == 'number':
			# REPLACE number with number_123456
			name.text = plate_number
			break

	#print(ET.tostring(root, encoding='utf8').decode('utf8'))

	tree.write('../'+dest_path+'/'+file)