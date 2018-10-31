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
        self.xml_element = xml_element

    @property
    def fieldname(self):
        return(self.xml_element.attrib.get('fieldname', '__NOT FOUND__'))

    @property
    def fieldlabel(self):
        return(self.xml_element.attrib.get('fieldlabel', '__NOT FOUND__'))

    def summarize(self):
        print("-"*48)
        print("Field: {0} ({1})".format(self.fieldname, self.fieldlabel))


class CodeBookFieldDiscrete(CodeBookField):

    def __init__(self, xml_element):
        if not (xml_element.attrib['format'] == 'numeric') and (xml_element.attrib['type'] == 'discrete'):
            raise ValueError(
                "Attempted to construct discrete field type from non-discrete or non-numeric xml element ({0})".format(xml_element.attrib['fieldname']))

        super(CodeBookFieldDiscrete, self).__init__(xml_element)

    @property
    def minvalue(self):
        return(int(self.xml_element.attrib.get('minvalue', 0)))

    @property
    def maxvalue(self):
        return(int(self.xml_element.attrib.get('maxvalue', 0)))

    @property
    def formatname(self):
        return(self.xml_element.attrib.get('formatname', None))

    @property
    def nummiss(self):
        try:
            ret_val = int(self.xml_element.attrib['nummiss'])
        except KeyError:
            ret_val = None

        return(ret_val)

    @property
    def valueCounts(self):
        count_dict = dict()
        counts_elem = self.xml_element.find('DataCounts')
        if counts_elem:
            for data_count in list(counts_elem):
                count_dict[data_count.attrib['datavalue']
                           ] = data_count.attrib['datafreq']
        else:
            return({"ERROR": "NO DATACOUNTS FOUND"})

        return(count_dict)

    def summarize(self):
        print("-"*48)
        print("Field: {0} ({1})".format(self.fieldname, self.fieldlabel))
        print("Min: {0}".format(self.minvalue))
        print("Max: {0}".format(self.maxvalue))
        print("Missing: {0}".format(self.nummiss))
        print("Counts:")
        for c in self.valueCounts:
            print("    {0}: {1}".format(c, self.valueCounts[c]))


class CodeBookFieldContinuous(CodeBookField):
    def __init__(self, xml_element):
        if not (xml_element.attrib['format'] == 'numeric') and (xml_element.attrib['type'] == 'continuous'):
            raise ValueError(
                "Attempted to construct continuous field type from non-continuous or non-numeric xml element ({0})".format(xml_element.attrib['fieldname']))

        super(CodeBookFieldContinuous, self).__init__(xml_element)

    @property
    def minvalue(self):
        return(float(self.xml_element.attrib.get('minvalue', 0)))

    @property
    def maxvalue(self):
        return(float(self.xml_element.attrib.get('maxvalue', 0)))

    @property
    def mean(self):
        return(float(self.xml_element.attrib.get('mean', 0)))

    @property
    def stddev(self):
        return(float(self.xml_element.attrib.get('stddev', 0)))

    @property
    def formatname(self):
        return(self.xml_element.attrib.get('formatname', None))

    @property
    def validn(self):
        try:
            ret_val = int(self.xml_element.attrib['validn'])
        except KeyError:
            ret_val = None

        return(ret_val)

    def summarize(self):
        print("-"*48)
        print("Field: {0} ({1})".format(self.fieldname, self.fieldlabel))
        print("Min: {0}".format(self.minvalue))
        print("Max: {0}".format(self.maxvalue))
        print("Mean: {0}".format(self.mean))
        print("Std Dev: {0}".format(self.stddev))
        print("Valid N: {0}".format(self.validn))

myFields = list()

for field in fieldList:
    if (field.attrib['format'] == 'numeric'):
        if (field.attrib['type'] == 'discrete'):
            new_field = CodeBookFieldDiscrete(field)
        else:
            new_field = CodeBookFieldContinuous(field)
    else:
        new_field = CodeBookField(field)

    myFields.append(new_field)
    new_field.summarize()

print('Done')
