from xml.etree import ElementTree
from classes import XmlCodebook

file_path = "R:\\project\\DSY\\XML Codebook\\M48NT2AT.xml"

my_tree = ElementTree.parse(file_path)

myCB = XmlCodebook(my_tree)

def listUniqueAttrVals(xml_element_list, attr_name):
    attr_list = list()
    for xml_element in xml_element_list:
        attr_list = list(
            set(attr_list + [xml_element.attrib.get(attr_name, None)]))

    return(attr_list)


myCB.getRows('fieldname')

print('Done')
