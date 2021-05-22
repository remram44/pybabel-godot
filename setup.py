# -*- coding: utf-8 -*-

from setuptools import setup


setup(
    name='Babel-Godot',
    version='1.0',
    description='Plugin for Babel to support Godot scene files (.tscn)',
    author='Remi Rampin',
    author_email='remirampin@gmail.com',
    license='BSD',
    url='https://github.com/remram44/pybabel-godot',

    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    py_modules=['babel_godot'],

    entry_points="""
    [babel.extractors]
    godot_scene = babel_godot:extract_godot_scene
    godot_resource = babel_godot:extract_godot_resource
    """
)
