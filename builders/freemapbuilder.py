import xml.etree.ElementTree as ET
import random
from .mapbuilder import MapBuilder


class FreeMapBuilder(MapBuilder):

    def __init__(self):
        super().__init__()
        self.root = None
        self.chapter = None
        self.center = None
        self.node = None
        self.counter = 1

    def XMLroot(self, element='map', **kwargs):
        # if root raise RootException
        attrib = {'version': "1.0.1"}
        self.root = ET.Element(element,  attrib=attrib)

    def comment(text, **kwargs):
        text = "To view this file, download free mind mapping software FreeMind from http://freemind.sourceforge.net"
        self.root.insert(0, ET.Comment(text=text))

    def bookTitle(self, element, **kwargs):
        attrib = {'COLOR': "#000000",
                  'CREATED': "1111111111111",
                  'ID': self._ID(),
                  'MODIFIED': "1111111111111",
                  'TEXT': self._formatText(element)}
        self.center = ET.SubElement(self.root, 'node', attrib=attrib)

    def authors(self, element, **kwargs):
        attrib = {'COLOR': "#0033ff",
                  'CREATED': "1111111111111",
                  'ID': self._ID(),
                  'FOLDED': "false",
                  #   'LINK': "",
                  'MODIFIED': "1111111111111",
                  'POSITION': "right",
                  'TEXT': self._formatText(element)}
        ET.SubElement(self.center, 'node', attrib=attrib)

    def citation(self, element, **kwargs):
        attrib = {'COLOR': "#0033ff",
                  'CREATED': "1111111111111",
                  'ID': self._ID(),
                  'FOLDED': "false",
                  #   'LINK': "",
                  'MODIFIED': "1111111111111",
                  'POSITION': "right",
                  'TEXT': self._formatText(element)}
        ET.SubElement(self.center, 'node', attrib=attrib)

    def sectionHeading(self, element, **kwargs):
        attrib = {'COLOR': "#0033ff",
                  'CREATED': "1111111111111",
                  'ID': self._ID(),
                  'FOLDED': "false",
                  #   'LINK': "",
                  'MODIFIED': "1111111111111",
                  'POSITION': "right",
                  'TEXT': ' '.join((str(self.counter), self._formatText(element)))}
        self.counter += 1
        self.chapter = ET.SubElement(self.center, 'node', attrib=attrib)

    def noteHeading(self, element, **kwargs):
        attrib = {'COLOR': "#0033ff",
                  'CREATED': "1111111111111",
                  'ID': self._ID(),
                  'FOLDED': "false",
                  #   'LINK': "",
                  'MODIFIED': "1111111111111",
                  'POSITION': "right",
                  'TEXT': self._formatText(element)}
        self.node = ET.Element('node', attrib=attrib)

    def noteText(self, element, **kwargs):
        attrib = {'COLOR': "#0033ff",
                  'CREATED': "",
                  'ID': self._ID(),
                  'FOLDED': "false",
                  #   'LINK': "",
                  'MODIFIED': "",
                  'POSITION': "right",
                  'TEXT': self._formatText(element)}
        if not self.node is None:
            node = ET.SubElement(self.chapter, 'node', attrib=attrib)
            node.insert(0, self.node)
            self.node = None

    def document(self):
        return ET.ElementTree(self.root)

    def _formatText(self, element, **kwargs):
        if element.descendants:
            return ''.join(element.strings).strip()
            # rif = re.findall(r'(\d+)', text)
            # subchapter = re.findall(r'- (.*)>', text)
        return None

    def _ID(self):
        return 'ID_{rnd!s:0>}'.format(rnd=random.randint(0, 9999999999))
