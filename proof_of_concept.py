import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup, Tag
import os
import re
import random


class MapBuilder(object):

    def root(self, element, **kwargs):
        pass

    def comment(self, text, **kwargs):
        pass

    def bookTitle(self, element, **kwargs):
        pass

    def authors(self, element, **kwargs):
        pass

    def citation(self, element, **kwargs):
        pass

    def sectionHeading(self, element, **kwargs):
        pass

    def noteHeading(self, element, **kwargs):
        pass

    def noteText(self, element, **kwargs):
        pass

    def document(self, element, **kwargs):
        pass


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


# Open
fname = 'notes.html'
with open(file=fname, encoding='UTF-8') as f:
    soup = BeautifulSoup(f, features="html.parser")

# Fields extraction
# 0 - bodyContainer: div class="bodyContainer"
builder = FreeMapBuilder()
builder.XMLroot()
element = soup.find_all("div", class_="bookTitle", limit=1)[0]
key = None
while element:
    if isinstance(element, Tag):
        try:
            # 1 - title: div class="bookTitle"
            if "bookTitle" in element['class']:
                builder.bookTitle(element)
            # 1 - authors: div class="authors"
            if "authors" in element['class']:
                builder.authors(element)
            # 1 - citation: div class="citation"
            if "citation" in element['class']:
                builder.citation(element)
            # 1 - sectionHeading: div class="sectionHeading"
            if "sectionHeading" in element['class']:
                #     Evidenziazione(<span class="highlight_yellow">giallo</span>) - Pagina 29 · Posizione 230
                #     Nota - Pagina 29 · Posizione 230
                #     Segnalibro - Pagina 29 · Posizione 233
                builder.sectionHeading(element)
            if "noteHeading" in element['class']:
                builder.noteHeading(element)
            # 1 - noteText: div class="noteText"
            if "noteText" in element['class']:
                builder.noteText(element)

        except KeyError as err:
            pass

    element = element.next_sibling

document = builder.document()
document.write('%s.mm' % (fname),
               encoding='utf-8', xml_declaration=False)
