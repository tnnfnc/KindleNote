import xml.etree.ElementTree as ET
import random
from .mapbuilder import MapBuilder
import datetime


def java_date(date):
    # 1, 1970, 00:00:00 GMT
    beginning = datetime.datetime(
        1970, 1, 1, 0, 0, 0, 0, datetime.timezone.utc)
    jdate = date - beginning
    jdate = 1000 * (jdate.days * 24 * 3600 +
                    jdate.seconds + jdate.microseconds)
    return jdate


class FreeMapBuilder(MapBuilder):

    def __init__(self, **kwargs):
        super().__init__()
        self.root = None
        self.chapter = None
        self.center = None
        self.node = None
        self.counter = 1
        self.kwargs = kwargs

    def XMLroot(self, element='map', **kwargs):
        # if root raise RootException
        attrib = {'version': "1.0.1"}
        self.root = ET.Element(element,  attrib=attrib)

    def comment(text, **kwargs):
        text = "To view this file, download free mind mapping software FreeMind from http://freemind.sourceforge.net"
        self.root.insert(0, ET.Comment(text=text))

    def bookTitle(self, element, **kwargs):
        now = java_date(datetime.datetime.now(tz=datetime.timezone.utc))
        text = self._formatText(element)
        attrib = {'COLOR': "#000000",
                  'CREATED': str(now),
                  'ID': self._ID(),
                  'MODIFIED': str(now),
                  'TEXT': text}
        self.center = ET.SubElement(self.root, 'node', attrib=attrib)
        ET.SubElement(self.center, 'font', attrib={
            'BOLD': "true", 'NAME': "SansSerif", 'SIZE': "14"})
        return text

    def authors(self, element, **kwargs):
        now = java_date(datetime.datetime.now(tz=datetime.timezone.utc))
        text = self._formatText(element)
        attrib = {'COLOR': "#0033ff",
                  'CREATED': str(now),
                  'ID': self._ID(),
                  'FOLDED': "false",
                  #   'LINK': "",
                  'MODIFIED': str(now),
                  'POSITION': "right",
                  'TEXT': text}
        ET.SubElement(self.center, 'node', attrib=attrib)
        return text

    def citation(self, element, **kwargs):
        now = java_date(datetime.datetime.now(tz=datetime.timezone.utc))
        text = self._formatText(element)
        attrib = {'COLOR': "#0033ff",
                  'CREATED': str(now),
                  'ID': self._ID(),
                  'FOLDED': "false",
                  #   'LINK': "",
                  'MODIFIED': str(now),
                  'POSITION': "right",
                  'TEXT': text}
        ET.SubElement(self.center, 'node', attrib=attrib)
        return text

    def sectionHeading(self, element, **kwargs):
        now = java_date(datetime.datetime.now(tz=datetime.timezone.utc))
        text = ' '.join((str(self.counter), self._formatText(element)))
        attrib = {'COLOR': "#0033ff",
                  'CREATED': str(now),
                  'ID': self._ID(),
                  'FOLDED': "true",
                  #   'LINK': "",
                  'MODIFIED': str(now),
                  'POSITION': "right",
                  'TEXT': text}
        self.counter += 1
        self.chapter = ET.SubElement(self.center, 'node', attrib=attrib)
        # <font BOLD="true" NAME="SansSerif" SIZE="14"/>
        ET.SubElement(self.chapter, 'font', attrib={
                      'BOLD': "true", 'NAME': "SansSerif", 'SIZE': "12"})
        return text

    def noteHeading(self, element, **kwargs):
        now = java_date(datetime.datetime.now(tz=datetime.timezone.utc))
        text = self._formatText(element)
        attrib = {'COLOR': "#990000",
                'CREATED': str(now),
                'ID': self._ID(),
                'FOLDED': "true",
                #   'LINK': "",
                'MODIFIED': str(now),
                'POSITION': "right",
                'TEXT': text}
        self.node = ET.Element('node', attrib=attrib)
        ET.SubElement(self.node, 'font', attrib={
            'BOLD': "true", 'NAME': "SansSerif", 'SIZE': "10"})
        return text

    def noteText(self, element, **kwargs):
        now = java_date(datetime.datetime.now(tz=datetime.timezone.utc))
        text = self._formatText(element)
        attrib = {'COLOR': "#000000",
                  'CREATED': str(now),
                  'ID': self._ID(),
                  'FOLDED': "true",
                  #   'LINK': "",
                  'MODIFIED': str(now),
                  'POSITION': "right",
                  'TEXT': text}
        if not self.node is None:
            node = ET.SubElement(self.chapter, 'node', attrib=attrib)
            if self.kwargs and self.kwargs.get('page_on'):
                node.insert(0, self.node)
            self.node = None
        return text

    def document(self):
        return ET.ElementTree(self.root)

    def _formatText(self, element, **kwargs):
        if element.descendants:
            s = ''.join(element.strings).strip()
            return s if s else ''
            # rif = re.findall(r'(\d+)', text)
            # subchapter = re.findall(r'- (.*)>', text)
        return ''

    def _ID(self):
        return 'ID_{rnd!s:0>}'.format(rnd=random.randint(0, 9999999999))
