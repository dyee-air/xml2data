from abc import ABC, abstractproperty


class AbstractXmlElement(ABC):

    def __init__(self, xml_element, tag_str=None):

        if xml_element.tag != tag_str:
            raise TypeError(
                "Attempted to construct {0} object from non-{0} XML element.".format(tag_str))

        self._parent_tag = tag_str + 's'

        self._xml_element = xml_element

    @property
    def xml_element(self):
        return self._xml_element

    @abstractproperty
    def name(self):
        pass

    def get(self, attr_name, default=None):
        try:
            return getattr(self, attr_name)
        except AttributeError:
            return default

    def __getattr__(self, attr_name):
        try:
            return self.xml_element.attrib[attr_name]
        except KeyError:
            return super().__getattribute__(attr_name)


class DataCount(AbstractXmlElement):

    def __init__(self, xml_element, parent_field=None, data_format=None):
        super().__init__(xml_element, tag_str='DataCount')

        self.setParentField(parent_field)
        self.setDataFormat(data_format)

    @property
    def name(self):
        return

    @property
    def parent_field(self):
        return self._parent_field

    @property
    def data_format(self):
        return self._data_format

    @property
    def datalabel(self):
        return self.data_format.getLabel(self.datavalue)

    def setDataFormat(self, data_format):
        if data_format and not isinstance(data_format, DataFormat):
            raise TypeError(
                "{0} is not a valid DataFormat".format(data_format))

        self._data_format = data_format

    def setParentField(self, parent_field):
        if parent_field and not isinstance(parent_field, DataField):
            raise TypeError("DataCount requires DataField as parent")

        self._parent_field = parent_field

    def __getattr__(self, attr_name):
        try:
            return self.xml_element.attrib[attr_name]
        except KeyError:
            if attr_name in self._parent_field.attrib:
                return self._parent_field.get(attr_name)
            super().__getattr__(attr_name)


class DataField(AbstractXmlElement):

    def __init__(self, xml_element):

        super().__init__(xml_element, tag_str='DataField')

    @property
    def name(self):
        return self.fieldname

    @property
    def is_discrete(self):
        return self.type == "discrete"

    @property
    def is_numeric(self):
        return self.format == "numeric"


class DataFormat(AbstractXmlElement):

    def __init__(self, xml_element):

        super().__init__(xml_element, tag_str='DataFormat')

    @property
    def name(self):
        return self.formatname

    @property
    def format_dict(self):

        fmt_dict = dict()

        for format_code in list(self.xml_element):
            val = int(format_code.attrib['formatvalue'])
            lbl = format_code.attrib['formatlabel']
            fmt_dict[val] = lbl

        return fmt_dict

    def getLabel(self, value):
        try:
            return self.format_dict[value]
        except KeyError:
            return None

    def getValue(self, label):
        try:
            return [val for val in self.format_dict if self.format_dict[val] == label][0]
        except KeyError:
            return None


class XmlCodebook(object):

    def __init__(self, element_tree):
        self._element_tree = element_tree

        self._root = self.element_tree.getroot()

        self._data_fields = self._wrapElements('DataFields', DataField)
        self._data_formats = self._wrapElements('DataFormats', DataFormat)
        self._data_counts = list()
        self._counts_map = dict()
        for field in self.data_fields:
            if field.xml_element.find('DataCounts'):
                self._data_counts += [DataCount(elem, parent_field=field) for elem in field.xml_element.find('DataCounts')]


        # counts_map = {c:p for p in self.data_fields for c in p.find('DataCounts')}


        for field in self.data_fields:
            if hasattr(field, 'formatname'):
                field_format = [
                    fmt for fmt in self.data_formats if fmt.name == field.formatname]
                if field_format:
                    field.format_dict = field_format[0].format_dict

        self._file_header = self.root.find('DataFile')

    @property
    def element_tree(self):
        return self._element_tree

    @property
    def root(self):
        return self._root

    @property
    def data_fields(self):
        return self._data_fields

    @property
    def data_formats(self):
        return self._data_formats

    @property
    def data_counts(self):
        return self._data_counts

    def getRows(self, attr_list, numeric=False, discrete=False):

        row_list = list()

        if numeric:
            if discrete:
                field_list = [f for f in self.data_fields if (
                    f.format == 'numeric') and (f.type == 'discrete')]
            else:
                field_list = [f for f in self.data_fields if (
                    f.format == 'numeric') and (f.type == 'continuous')]
        else:
            field_list = self.data_fields

        for field in field_list:
            row = list()

            for attr_name in attr_list:
                try:
                    row.append(field.get(attr_name))
                except AttributeError:
                    row.append(None)

            row_list.append(row)

        return row_list

    @property
    def header(self):
        return self._file_header.attrib

    def __getattr__(self, attr_name):
        try:
            return self.header[attr_name]
        except KeyError:
            return super().__getattribute__(attr_name)

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

        return [wrapper_class(elem) for elem in elem_list]
