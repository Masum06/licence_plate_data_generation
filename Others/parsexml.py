import xml.etree.ElementTree as ET

tree = ET.parse('2007_000032.xml')
root = tree.getroot()

accepted_list = ["person", "car", "bus"]

for child in root.findall('object'):
	if child.find('name').text not in accepted_list:
		root.remove(child)

#print(ET.tostring(root, encoding='utf8').decode('utf8'))

tree.write('output.xml')