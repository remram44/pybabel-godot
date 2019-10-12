Babel Godot plugin
==================

This is a plugin for `Babel <http://babel.pocoo.org/>`_, the internationalization library, that adds support for scene files from the `Godot game engine <https://godotengine.org/>`_.

Using a mapping file like this::

    [python: **.gd]
    encoding = utf-8
    extract_messages = tr

    [godot_scene: **.tscn]
    encoding = utf-8

you can extract messages to be translated from both your ``.gd`` and ``.tscn`` files using::

    pybabel extract -F babel_mapping_file -k Label/text -k tr -o translations.pot .

You can then create ``.po`` files from the POT catalog using `Poedit <https://poedit.net/>`_, or online services  such as `Crowdin <https://crowdin.com/>`_, `Transifex <https://www.transifex.com/>`_, or `Weblate <https://weblate.org/>`_.
