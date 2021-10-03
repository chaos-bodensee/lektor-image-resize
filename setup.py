# -*- coding: utf-8 -*-
import ast
import io
import re

from setuptools import setup, find_packages

with io.open('README.md', 'rt', encoding="utf8") as f:
    readme = f.read()

_description_re = re.compile(r'description\s+=\s+(?P<description>.*)')

with open('lektor_image_resize.py', 'rb') as f:
    description = str(ast.literal_eval(_description_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    author='L3D',
    author_email='l3d@c3woc.de',
    description=description,
    keywords='Lektor plugin to generate webp and jpg thumbnails in the defined sizes',
    license='MIT',
    long_description=readme,
    long_description_content_type='text/markdown',
    name='lektor-image-resize',
    packages=find_packages(),
    py_modules=['lektor_image_resize'],
    url='https://github.com/chaos-bodensee/lektor-image-resize.git',
    version='0.6.1',
    install_requires=[],
    classifiers=[
        'Framework :: Lektor',
        'Environment :: Plugins',
    ],
    entry_points={
        'lektor.plugins': [
            'image-resize = lektor_image_resize:ImageResizePlugin',
        ]
    }
)
