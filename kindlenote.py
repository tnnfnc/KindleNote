from bs4 import BeautifulSoup, Tag
from builders.freemapbuilder import FreeMapBuilder
# Open
fname = 'notes.html'
with open(file=fname, encoding='UTF-8') as f:
    soup = BeautifulSoup(f, features="html.parser")

# Fields extraction
# 0 - bodyContainer: div class="bodyContainer"
# Look for BuilderFiles in package builders
# Choose the builder
# Import the module.BuilderClass
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
