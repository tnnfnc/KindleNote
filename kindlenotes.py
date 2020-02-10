"""KindleNote: a help kindle annotations management.
    Conventions:

        - Define kv field as _<prefix>_<name>, prefixes:

            _inp_ : input text widget
            _lab_ : label widgets
            _spi_ : spinner widget
            _out_ : output text widget
            _wid_ : widget container
            _btn_ : button widget
            _swi_ : switch widget
            _scr_ : scroll widget
            _prb_ : progress bar widget

        - Define kivy properties prefixes:

            pr_<name> :
            pr_<name>_wid : container widget property

        - Field convention:

            Fields are dictionary key - value, the input field in a .kv screen
            is _inp_key, the kivy property is pr_key.
"""
from bs4 import BeautifulSoup, Tag
from builders.freemapbuilder import FreeMapBuilder
import base64
import json
import re
import os
import sys
import appconfig as conf
import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.lang.builder import Builder
from kivy.properties import ObjectProperty
from kivy.properties import StringProperty
from filemanager import OpenFilePopup, SaveFilePopup, message, decision
dummy = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dummy)

# =============================================================================
# Kivy config
# =============================================================================
kivy.require('1.11.0')  # Current kivy version

MAJOR = 1
MINOR = 0
MICRO = 2
RELEASE = True
__version__ = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

# _ = conf.translate(['it'])
_ = conf.translate(['it'])


Builder.load_file('user_interface.kv')


class OpenFile(OpenFilePopup):

    def cmd_load(self, path, selection):
        """
        Open file.
        """
        if selection:
            if isinstance(selection, list):
                file = selection[0]
            app = App.get_running_app()
            app.open(file)
            self.dismiss()
        return False

    def cmd_cancel(self):
        """
        Cancel without doing nothing.
        """
        self.dismiss()

    def is_valid(self, folder, file):
        return True


class NotesManagerWidget(BoxLayout):
    """App enter screen."""

    def __init__(self, *args, **kwargs):
        super(NotesManagerWidget, self).__init__(**kwargs)
        # App.get_running_app

    def open(self):
        popup = OpenFile()
        popup.title = _('Open')
        popup.open()

    def exit(self):
        App.get_running_app().stop()

    def log(self, log):
        self.ids._out_log.text += f'\n>{log}'

    def content(self, content):
        self.ids._out_content.text += f'\n{content}'

    def clear_content(self):
        self.ids._out_content.text = _('Parsed content:\n\n')

    def clear_log(self):
        self.ids._out_log.text = _('App Log:\n\n')


class KindleNotesApp(App):
    # Defaults constants
    # SETTINGS = 'Settings'

    use_kivy_settings = True
    file = StringProperty('')

    def __init__(self, **kwargs):
        super(KindleNotesApp, self).__init__(**kwargs)
        self.root = root = NotesManagerWidget()
        self.builder = None
        self.document = None

    def build(self):
        self.title = 'KindleNotes %s' % (__version__)
        self.icon = '%s\\%s' % (conf.icons_dir, conf.ICON)

        return self.root

    def build_settings(self, settings):
        """Build settings from a JSON file / data first.
        """
        # JSON template is needed ONLY to create the panel
        # path = os.path.dirname(os.path.realpath(__file__))
        # with open(f'{path}\knsettings.json') as f:
        #     s = json.dumps(eval(f.read()))
        # settings.add_json_panel('settings', self.config, data=s)

    def build_config(self, config):
        """The App class handles ‘ini’ files automatically add sections and
        default parameters values. """
        # config.adddefaultsection('section_name')
        # config.setdefault('name', 'value', 'default')  # sec.

    def on_start(self):
        """Event handler for the on_start event which is fired after initialization
        (after build() has been called) but before the application has started running."""
        # Init screens:
        return super().on_start()

    def on_pause(self):
        """Event handler called when Pause mode is requested. You should return
        True if your app can go into Pause mode, otherwise return False and your
        application will be stopped."""
        return super().on_pause()

    def on_resume(self):
        """Event handler called when your application is resuming from the Pause mode."""
        return super().on_resume()

    def on_stop(self):
        """Event handler for the on_stop event which is fired when the application
        has finished running (i.e. the window is about to be closed)."""
        return super().on_stop()

    def open(self, file):
        if file:
            self.file = file
            self.log(_('Opening file: %s' % (file)))
            self.buid_document()
        else:
            self.log(_('No file was loaded'))

    def write_map(self):
        """Transform to FreeMind"""
        if self.file and self.document:
            try:
                file = '%s.mm' % (self.file)
                self.document.write(file,
                                    encoding='utf-8', xml_declaration=False)
                self.log(_('Converted into map: %s') % (file))
            except Exception as err:
                self.log(_('Error creating map: %s') % (file))
        else:
            self.log(_('No file was loaded'))

    def write_html(self):
        """Transform to html"""
        if self.file and self.document:
            # self.builder = HtmlMapBuilder()
            try:
                self.log(_('Option not available'))
            except Exception as err:
                self.log(_('Error creating map: %s') % (file))
        else:
            self.log(_('No file was loaded'))

    def content(self, text):
        """Log action"""
        self.root.content(text)

    def log(self, log):
        """Log action"""
        self.root.log(log)

    def exit(self):
        """Exit the app doing nothing. """
        self.stop()

    def buid_document(self):
        """
        Parse the file to FreeMap format. This format is the starting 
        point for converting to other ones.
        """
        # Parameters
        # Add page numbers
        page_on = self.root.ids._chk_page_on.active
        # Append the table of content (html only)
        summary_on = self.root.ids._chk_summary_on.active

        builder = FreeMapBuilder(page_on=page_on, summary_on=summary_on)
        errs = []
        tree = []
        try:
            with open(file=self.file, encoding='UTF-8') as f:
                soup = BeautifulSoup(f, features="html.parser")
            self.log(_('Open file: %s') % (self.file))
        except IOError as e:
            message(
                _('Open'), _('Invalid file: "%s":\n%s') % (os.path.basename(self.file), e), 'e')
            self.file = None
            return False
        except ValueError as e:
            message(_('Open'), f'"{os.path.basename(self.file)}":\n{e}', 'e')
            return False
        # Fields extraction
        try:
            builder.XMLroot()
            element = soup.find_all("div", class_="bookTitle", limit=1)[0]
            self.log(_('Start parsing'))
            while element:
                if isinstance(element, Tag):
                    try:
                        # 1 - title: div class="bookTitle"
                        if "bookTitle" in element['class']:
                            text = builder.bookTitle(element)
                            tree.append((0, text))
                        # 1 - authors: div class="authors"
                        if "authors" in element['class']:
                            text = builder.authors(element)
                            tree.append((0, text))
                        # 1 - citation: div class="citation"
                        if "citation" in element['class']:
                            text = builder.citation(element)
                            tree.append((0, text))
                        # 1 - sectionHeading: div class="sectionHeading"
                        if "sectionHeading" in element['class']:
                            text = builder.sectionHeading(element)
                            tree.append((1, text))
                        if "noteHeading" in element['class']:
                            text = builder.noteHeading(element)
                            tree.append((3, text))
                        # 1 - noteText: div class="noteText"
                        if "noteText" in element['class']:
                            text = builder.noteText(element)
                            tree.append((2, text))
                    except Exception as err:
                        errs.append(err)
                element = element.next_sibling
        except Exception as err:
            errs.append(_('Error parsing the file'))
        # Logging
        self.root.clear_content()
        self.root.clear_log()
        self.log(_('End parsing %s lines') % (len(tree)))
        text = '\n'.join([f'Level: {a[0]}> {a[1]}' for a in tree])
        self.content(text)
        self.log(errs)
        if len(tree) > 0:
            self.log(_('Conversion ok'))
            try:
                self.document = builder.document()
            except Exception as err:
                self.log(_('Error creating map'))
        else:
            self.log(_('Error creating map'))


if __name__ == '__main__':
    KindleNotesApp().run()
