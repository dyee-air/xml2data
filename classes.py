from abc import ABC, abstractproperty


class AbstractXmlElement(ABC):

    def __init__(self, xml_element, tag_str=None):

        if xml_element.tag != tag_str:
            raise TypeError(
                "Attempted to construct {0} object from non-{0} XML element.".format(tag_str))

        self._xml_element = xml_element

    @property
    def xml_element(self):
        return(self._xml_element)

    @abstractproperty
    def name(self):
        pass

    def get(self, attr_name):
        return(getattr(self, attr_name))

    def __getattr__(self, attr_name):
        try:
            return(self.xml_element.attrib[attr_name])
        except KeyError:
            return(super().__getattribute__(attr_name))


class DataField(AbstractXmlElement):

    def __init__(self, xml_element, format_dict=None):

        super().__init__(xml_element, tag_str='DataField')

        self.formatDict = format_dict

    @property
    def name(self):
        return(self.fieldname)

    @property
    def isDiscrete(self):
        return(self.type == "discrete")

    @property
    def isNumeric(self):
        return(self.format == "numeric")

    @property
    def dataCounts(self):
        """
        Returns DataCounts for this DataField as a dict (empty if DataCounts does not exist)

        """

        data_count_dict = dict()

        if self.xml_element.find('DataCounts'):

            for data_count in list(self.xml_element.find('DataCounts')):
                val = int(data_count.attrib['datavalue'])
                freq = int(data_count.attrib['datafreq'])
                data_count_dict[val] = freq

        return(data_count_dict)


class DataFormat(AbstractXmlElement):

    def __init__(self, xml_element):

        super().__init__(xml_element, tag_str='DataFormat')

    @property
    def name(self):
        return(self.formatname)

    @property
    def formatDict(self):

        fmt_dict = dict()

        for format_code in list(self.xml_element):
            val = int(format_code.attrib['formatvalue'])
            lbl = format_code.attrib['formatlabel']
            fmt_dict[val] = lbl

        return(fmt_dict)


class XmlCodebook(object):

    def __init__(self, element_tree):
        self._elementTree = element_tree

        self._root = self.elementTree.getroot()

        self._dataFields = self._wrapElements('DataFields', DataField)
        self._dataFormats = self._wrapElements('DataFormats', DataFormat)

        self._fileHeader = self.root.find('DataFile')

    @property
    def elementTree(self):
        return(self._elementTree)

    @property
    def root(self):
        return(self._root)

    @property
    def dataFields(self):
        return(self._dataFields)

    @property
    def dataFormats(self):
        return(self._dataFormats)

    @property
    def header(self):
        return(self._fileHeader.attrib)

    def __getattr__(self, attr_name):
        try:
            return(self.header[attr_name])
        except KeyError:
            return(super().__getattribute__(attr_name))

    def _wrapElements(self, tag_str, wrapper_class):

        tag_count_map = {
            'DataFields': 'numfields',
            'DataFormats': 'numformats',
            'IRTScales': 'numscales',
            'Samples': 'numsamples',
            'Groups': 'numgroups'
        }

        elem_parent = self.root.find(tag_str)

        if not elem_parent:
            raise ValueError(
                "XML root has no child with tag '{0}'".format(tag_str))

        elem_list = [elem for elem in list(
            elem_parent) if elem.tag == tag_str[:-1]]

        num_expected = int(elem_parent.attrib[tag_count_map[tag_str]])
        num_found = len(elem_list)

        if num_found != num_expected:
            print("{0}: num_found ({1}) differs from num_expected {2}".format(
                tag_str, num_found, num_expected))

        return([wrapper_class(elem) for elem in elem_list])
