import gettext
import os


current_dir = os.path.dirname(os.path.realpath(__file__))
icons_dir = '%s\icons' % (current_dir)
data_dir = '%s\data' % (current_dir)
locale_dir = '%s\locale' % (current_dir)

# Translations


def translate(languages=['il']):
    def f(x): return x
    try:
        lang = gettext.translation(
            'skipkey', localedir=locale_dir, languages=languages)
        lang.install()
    except FileNotFoundError as e:
        print(f'No translation found: {e}')
        lang = gettext.NullTranslations(fp=None)
        lang.install()
    finally:
        f = lang.gettext
    return f


# Command specification
ICON = 'reader.png'
