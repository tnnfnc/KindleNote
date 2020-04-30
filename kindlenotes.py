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
from builders.mapbuilders import FreeMapBuilder, NotesParser, explore, remove_pages
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
MICRO = 4
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
        return os.path.isdir(file) or os.path.splitext(file)[1] in ['.html', '.xml', '.mm']


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
        self.ids._out_log.text = _('App Logs:\n')

    def update_gui(self, **kwargs):
        self.ids._inp_chapter_low.text = str(
            kwargs.get('chapter_range', [0, 0])[0])
        self.ids._inp_chapter_high.text = str(kwargs.get(
            'chapter_range', (0, 0))[1])
        self.ids._inp_level_low.text = str(
            kwargs.get('level_range', [0, 0])[1])

    def get_options(self):
        return {
            'section_range': (self.ids._inp_chapter_low.text, self.ids._inp_chapter_high.text),
            'level_low': self.ids._inp_level_low.text,
            'pages': self.ids._chk_page_on.active == True,
            'summary': self.ids._chk_summary_on.active == True
        }


class KindleNotesApp(App):
    # Defaults constants
    # SETTINGS = 'Settings'

    use_kivy_settings = True
    file = StringProperty('')

    def __init__(self, **kwargs):
        super(KindleNotesApp, self).__init__(**kwargs)
        self.root = root = NotesManagerWidget()
        self.builder = None
        # Internal document
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
            self.root.clear_content()
            self.root.clear_log()
            self.file = file
            self.log(_('Opening file: %s' % (file)))
            # Build internal document
            self.build_document()
        else:
            self.log(_('No file was loaded'))

    def write_map(self):
        """Transform from internal document to FreeMind"""
        if self.file and self.document:
            try:
                # Options take effect here:
                # Include page positions: _TYPE': HEADING

                document = self.filter_document()

                file = '%s.mm' % (self.file)
                document.write(file, encoding='utf-8', xml_declaration=False)
                self.log(_('Saved to map: %s') % (file))
            except Exception as err:
                self.log(_('Error creating map: %s') % (err))
        else:
            self.log(_('No file was loaded'))

    def write_html(self):
        """Transform from internal document to html"""
        if self.file and self.document:
            # self.builder = HtmlMapBuilder()
            try:
                self.log(_('Option not available'))
            except Exception as err:
                self.log(_('Error creating map: %s') % (file))
        else:
            self.log(_('No file was loaded'))

    def filter_document(self):
        """Apply formatting options to the document. 
        Return a document."""
        document = self.document
        options = self.root.get_options()

        if options.get('section_range', None):
            pass
        if options.get('level_range', None):
            pass
        if options.get('pages', None): # include pages
            pass
        else: # remove page numbers
            document = remove_pages(self.document)
        if options.get('summary', None):
            pass

        return document

    def content(self, text):
        """Log action"""
        self.root.content(text)

    def log(self, log):
        """Log action"""
        self.root.log(log)

    def exit(self):
        """Exit the app doing nothing. """
        self.stop()

    def build_document(self):
        """
        Build internal document: parse the file to FreeMap format.
        This format is the starting point for converting to other ones.
        """
        parser = NotesParser()
        self.document = parser.parse(self.file)
        logs = parser.getlogs()
        # Logging
        for log in logs:
            self.root.log(log)

        if self.document:
            docinfo = explore(self.document)
            self.root.log(_('Conversion ok'))
            self.root.content(docinfo['text'][0:5000])
            self.root.update_gui(
                chapter_range=(1, docinfo['max_section_counter']),
                level_range=(1, docinfo['max_node_level'])
            )
        else:
            self.root.log(_('Conversion failed'))


if __name__ == '__main__':
    KindleNotesApp().run()
