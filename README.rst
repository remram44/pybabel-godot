Babel Godot plugin
==================

This is a plugin for `Babel <http://babel.pocoo.org/>`_, the internationalization library, that adds support for scene files from the `Godot game engine <https://godotengine.org/>`_.

Installation
------------

Install Babel and this plugin::

    pip install Babel Babel-Godot

Usage
-----

Using a mapping file like this::

    [python: **.gd]
    encoding = utf-8
    extract_messages = tr

    [godot_scene: **.tscn]
    encoding = utf-8

    [godot_resource: **.tres]
    encoding = utf-8

you can extract messages to be translated from both your ``.gd`` and ``.tscn`` files using::

    pybabel extract -F babel_mapping_file -k Label/text -k Resource/catchphrase -k tr -o translations.pot .

You can then create ``.po`` files from the POT catalog using `Poedit <https://poedit.net/>`_, or online services  such as `Crowdin <https://crowdin.com/>`_, `Transifex <https://www.transifex.com/>`_, or `Weblate <https://weblate.org/>`_.

See ``testproject/`` in the repository for an example.
