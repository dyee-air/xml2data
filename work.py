from xml.etree import ElementTree

file_path = "R:\\project\\DSY\\XML Codebook\\M48NT2AT.xml"

my_tree = ElementTree.parse(file_path)
root = my_tree.getroot()

fieldList = list(root.find('DataFields'))


def listUniqueAttrVals(xml_element_list, attr_name):
    attr_list = list()
    for xml_element in xml_element_list:
        attr_list = list(
            set(attr_list + [xml_element.attrib.get(attr_name, None)]))

    return(attr_list)


class CodeBookField(object):

    def __init__(self, xml_element):
        self._xml_element = xml_element

    @property
    def xml_element(self):
        return(self._xml_element)

    @property
    def dataCounts(self):
        """
        Returns DataCounts for this DataField as a dict (empty if DataCounts does not exist)
        
        """

        data_count_dict = dict()

        if self.xml_element.find('DataCounts'):

            for data_count in list(self.xml_element.find('DataCounts')):
                data_count_dict[int(data_count.attrib['datavalue'])] = int(
                    data_count.attrib['datafreq'])

        return(data_count_dict)

    def get(self, attr_name):
        return(getattr(self, attr_name))

    def __getattr__(self, attr_name):
        return(self.xml_element.attrib[attr_name])


print('Done')
