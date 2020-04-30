"""
- Internal Map Builder: builds a map from a html kindle notes
- Free Map Builder: builds a map from a Internal Map tree to FreeMind format
- Html Map Builder: builds a map from a Internal Map tree to html format
"""
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup, Tag
import random
import datetime
import io

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


def explore(document):
    """
    Return a text representation, the parents list, the maximum 
    section depth, the maximun element depth.
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
        if '_node_type' in node.attrib and node.attrib['_node_type'] == SECTION:
            count = max(int(node.attrib['_section_counter']), count)
            node_level = max(int(node.attrib['_node_level']), node_level)
        else:
            node_level = max(level, node_level)
            # _type = _types[level] if level < len(_types) else ''
            # _section_counter = _section_counter + 1 if level == 2 else 0
            # attrib = {'_node_type': _type, '_node_level': f'{level}', '_section_counter': f'{_section_counter}'}

        # Text
        text += node_text(node, level)
    return {'text': text,
            'parents': parents,
            'max_node_level': node_level,
            'max_section_counter': count}


def remove_pages(document):
    """Remove the element 'note heading' from the document"""
    s = ET.tostring(element=document.getroot(), encoding='utf-8')
    root = ET.fromstring(s)
    for element in root.iter('node'):
        headings = [e for e in element.findall(
            'node') if e.attrib.get('_node_type') == HEADING]
        if headings:
            element.remove(headings[0])

    return ET.ElementTree(root)


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
                # return XmlMapDocument(self.parse_html(file))
                return self.parse_html(file)
            elif soup.find('map') and soup.find('node'):
                # return XmlMapDocument(self.parse_xml(file))
                return self.parse_xml(file)

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
                        # Contains the page number
                        if "noteHeading" in element['class']:
                            builder.noteHeading(element)
                        # 1 - noteText: div class="noteText"
                        if "noteText" in element['class']:
                            builder.noteText(element)
                    except Exception as e:
                        self.logs.append(f'{e}')
                element = element.next_sibling
            return builder.get_document()
        except Exception as e:
            self.logs.append(f'{e}')
        return None

    def getlogs(self):
        """Return the conversion logs"""
        return self.logs


class FreeMapBuilder():
    """
    Convert a HTML formatted file from Kindle Notes to an internal
    fomat similar to FreeMap raw formatted file.
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.root = None
        self.chapter = None
        self.center = None
        self.node = None
        self.section_counter = 0
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
                  '_node_type': TITLE,
                  '_node_level': '1',
                  '_section_counter': f'{self.section_counter}'}
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
                  '_node_type': AUTHORS,
                  '_node_level': '2',
                  '_section_counter': f'{self.section_counter}'}
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
                  '_node_type': CITATION,
                  '_node_level': '1',
                  '_section_counter': f'{self.section_counter}'}
        ET.SubElement(self.center, 'node', attrib=attrib)
        return text

    def sectionHeading(self, element, **kwargs):
        now = java_date(datetime.datetime.now(tz=datetime.timezone.utc))
        text = ' '.join((str(self.section_counter), self._formatText(element)))
        self.section_counter += 1
        attrib = {'COLOR': "#0033ff",
                  'CREATED': str(now),
                  'ID': ID(),
                  'FOLDED': "true",
                  #   'LINK': "",
                  'MODIFIED': str(now),
                  'POSITION': "right",
                  'TEXT': text,
                  '_node_type': SECTION,
                  '_node_level': '2',
                  '_section_counter': f'{self.section_counter}'}
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
                  '_node_type': HEADING,
                  '_node_level': '4',
                  '_section_counter': f'{self.section_counter}'}
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
                  '_node_type': TEXT,
                  '_node_level': '3',
                  '_section_counter': f'{self.section_counter}'}
        if not self.node is None:
            node = ET.SubElement(self.chapter, 'node', attrib=attrib)
            node.insert(0, self.node)
            self.node = None
        return text

    def get_document(self):
        return ET.ElementTree(self.root)
