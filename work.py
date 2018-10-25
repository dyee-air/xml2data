from xml.etree import ElementTree

file_path = "R:\\project\\DSY\\XML Codebook\\M48NT2AT.xml"

my_tree = ElementTree.parse(file_path)
root = my_tree.getroot()

for df in root.iter('DataField'):
    print('-----------------')
    for d in df.attrib:
        print('{0}: {1} (type: {2})'.format(d, df.attrib[d], type(df.attrib[d])))

        