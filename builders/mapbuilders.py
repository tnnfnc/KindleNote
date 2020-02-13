"""
- Internal Map Builder: builds a map from a html kindle notes
- Free Map Builder: builds a map from a Internal Map tree to FreeMind format
- Html Map Builder: builds a map from a Internal Map tree to html format
"""
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup, Tag
import random
import datetime

MAP = 'map'
TITLE = 'title'
AUTHORS = 'authors'
CITATION = 'citation'
SECTION = 'section'
HEADING = 'heading'
TEXT = 'text'


def ID():
    return 'ID_{rnd!s:0>}'.format(rnd=random.randint(0, 9999999999))


def java_date(date):
    # 1, 1970, 00:00:00 GMT
    beginning = datetime.datetime(
        1970, 1, 1, 0, 0, 0, 0, datetime.timezone.utc)
    jdate = date - beginning
    jdate = 1000 * (jdate.days * 24 * 3600 +
                    jdate.seconds + jdate.microseconds)
    return jdate


def node_text(element, level, length=70):
    if element.tag == 'node':
        return f'\n{level}-{element.tag}> {element.attrib["TEXT"][:length]}...'
    else:
        return f'\n{level}-{element.tag}> ...'


def hierarchy(document):
    """
    Return a couple (text, hierarchy) from a xml document.
    """
    text = ''
    root = document.getroot()
    parents = [root]
    node_level = 0
    level = 0
    count = 0
    _types = [MAP, TITLE, SECTION, TEXT, HEADING]
    for node in root.iter('*'):
        p = [i for i in range(0, len(parents)) if node in list(parents[i])]
        if p:
            level = p[0] + 1
            if len(parents) > level:
                parents[level] = node
            else:
                parents.append(node)
        if '_TYPE' in node.attrib and node.attrib['_TYPE'] == SECTION:
            count = max(int(node.attrib['_COUNT']), count)
            node_level = max(int(node.attrib['_LEVEL']), node_level)
        else:
            node_level = max(level, node_level)
            # _type = _types[level] if level < len(_types) else ''
            # _count = _count + 1 if level == 2 else 0
            # attrib = {'_TYPE': _type, '_LEVEL': f'{level}', '_COUNT': f'{_count}'}

        # Text
        text += node_text(node, level)
    return text, parents, node_level, count


class XmlMapDocument(object):
    def __init__(self, document, **kwargs):
        self._document = document
        self._text, self._hierarchy, self._levels, self._headings = hierarchy(
            document)

    @property
    def document(self):
        return self._document

    @property
    def string(self):
        if self._text:
            return self._text
        return None

    @property
    def hierarchy(self):
        if self._hierarchy:
            return self._hierarchy
        return None

    @property
    def headings(self):
        return (1, self._headings)

    @property
    def levels(self):
        return (0, self._levels)


class NotesParser():
    """Parse a Kindle notes file or a FreeMind file
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.logs = []
        self.text = ''

    def parse(self, file):
        """Parse and return an ElementTree."""
        self.text = ''
        try:
            with open(file=file, encoding='UTF-8') as f:
                soup = BeautifulSoup(f, features="html.parser")
            if soup.find('html') and soup.select('div[class="bookTitle"]'):
                return XmlMapDocument(self.parse_html(file))
            elif soup.find('map') and soup.find('node'):
                return XmlMapDocument(self.parse_xml(file))

        except Exception as e:
            self.logs.append(f'{e}')
        return None

    def parse_xml(self, file):
        return ET.parse(file)

    def parse_html(self, file):
        try:
            with open(file=file, encoding='UTF-8') as f:
                soup = BeautifulSoup(f, features="html.parser")
            builder = FreeMapBuilder()
            builder.XMLroot()
            element = soup.find_all("div", class_="bookTitle", limit=1)[0]
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
                            builder.sectionHeading(element)
                        # 1 - noteHeading: div class="noteHeading"
                        if "noteHeading" in element['class']:
                            builder.noteHeading(element)
                        # 1 - noteText: div class="noteText"
                        if "noteText" in element['class']:
                            builder.noteText(element)
                    except Exception as e:
                        self.logs.append(f'{e}')
                element = element.next_sibling
            return builder.document
        except Exception as e:
            self.logs.append(f'{e}')
        return None

    def getlogs(self):
        """Return the conversion logs"""
        return self.logs


class FreeMapBuilder():
    """
    Convert a HTML formatted file from Kindle Notes to a FreeMap raw
    formatted file.
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.root = None
        self.chapter = None
        self.center = None
        self.node = None
        self.counter = 0
        self.kwargs = kwargs

    def _formatText(self, element, **kwargs):
        if element.descendants:
            s = ''.join(element.strings).strip()
            return s if s else ''
            # rif = re.findall(r'(\d+)', text)
            # subchapter = re.findall(r'- (.*)>', text)
        return ''

    def XMLroot(self, element='map', **kwargs):
        # if root raise RootException
        attrib = {'version': "1.0.1"}
        self.root = ET.Element(element,  attrib=attrib)

    def comment(self, text, **kwargs):
        text = "To view this file, download free mind mapping software FreeMind from http://freemind.sourceforge.net"
        self.root.insert(0, ET.Comment(text=text))

    def bookTitle(self, element, **kwargs):
        now = java_date(datetime.datetime.now(tz=datetime.timezone.utc))
        text = self._formatText(element)
        attrib = {'COLOR': "#000000",
                  'CREATED': str(now),
                  'ID': ID(),
                  'MODIFIED': str(now),
                  'TEXT': text,
                  '_TYPE': TITLE,
                  '_LEVEL': '1',
                  '_COUNT': f'{self.counter}'}
        self.center = ET.SubElement(self.root, 'node', attrib=attrib)
        ET.SubElement(self.center, 'font', attrib={
            'BOLD': "true", 'NAME': "SansSerif", 'SIZE': "14"})
        return text

    def authors(self, element, **kwargs):
        now = java_date(datetime.datetime.now(tz=datetime.timezone.utc))
        text = self._formatText(element)
        attrib = {'COLOR': "#0033ff",
                  'CREATED': str(now),
                  'ID': ID(),
                  'FOLDED': "false",
                  #   'LINK': "",
                  'MODIFIED': str(now),
                  'POSITION': "right",
                  'TEXT': text,
                  '_TYPE': AUTHORS,
                  '_LEVEL': '2',
                  '_COUNT': f'{self.counter}'}
        ET.SubElement(self.center, 'node', attrib=attrib)
        return text

    def citation(self, element, **kwargs):
        now = java_date(datetime.datetime.now(tz=datetime.timezone.utc))
        text = self._formatText(element)
        attrib = {'COLOR': "#0033ff",
                  'CREATED': str(now),
                  'ID': ID(),
                  'FOLDED': "false",
                  #   'LINK': "",
                  'MODIFIED': str(now),
                  'POSITION': "right",
                  'TEXT': text,
                  '_TYPE': CITATION,
                  '_LEVEL': '1',
                  '_COUNT': f'{self.counter}'}
        ET.SubElement(self.center, 'node', attrib=attrib)
        return text

    def sectionHeading(self, element, **kwargs):
        now = java_date(datetime.datetime.now(tz=datetime.timezone.utc))
        text = ' '.join((str(self.counter), self._formatText(element)))
        self.counter += 1
        attrib = {'COLOR': "#0033ff",
                  'CREATED': str(now),
                  'ID': ID(),
                  'FOLDED': "true",
                  #   'LINK': "",
                  'MODIFIED': str(now),
                  'POSITION': "right",
                  'TEXT': text,
                  '_TYPE': SECTION,
                  '_LEVEL': '2',
                  '_COUNT': f'{self.counter}'}
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
                  'ID': ID(),
                  'FOLDED': "true",
                  #   'LINK': "",
                  'MODIFIED': str(now),
                  'POSITION': "right",
                  'TEXT': text,
                  '_TYPE': HEADING,
                  '_LEVEL': '4',
                  '_COUNT': f'{self.counter}'}
        self.node = ET.Element('node', attrib=attrib)
        ET.SubElement(self.node, 'font', attrib={
            'BOLD': "true", 'NAME': "SansSerif", 'SIZE': "10"})
        return text

    def noteText(self, element, **kwargs):
        now = java_date(datetime.datetime.now(tz=datetime.timezone.utc))
        text = self._formatText(element)
        attrib = {'COLOR': "#000000",
                  'CREATED': str(now),
                  'ID': ID(),
                  'FOLDED': "true",
                  #   'LINK': "",
                  'MODIFIED': str(now),
                  'POSITION': "right",
                  'TEXT': text,
                  '_TYPE': TEXT,
                  '_LEVEL': '3',
                  '_COUNT': f'{self.counter}'}
        if not self.node is None:
            node = ET.SubElement(self.chapter, 'node', attrib=attrib)
            node.insert(0, self.node)
            self.node = None
        return text

    @property
    def document(self):
        return ET.ElementTree(self.root)
