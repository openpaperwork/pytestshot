#!/usr/bin/env python3

from setuptools import setup


setup(
    name="pytestshot",
    version="0.1",
    description=(
        "Automated tests for Python/GTK using screenshots and image processing"
    ),
    long_description=(
        "Automated tests for Python/GTK using screenshots and image processing"
    ),
    keywords="tests",
    url="https://github.com/jflesch/pytestshot#readme",
    download_url=("https://github.com/jflesch/pytestshot/archive/master.tar.gz"),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        ("License :: OSI Approved ::"
         " GNU General Public License v3 or later (GPLv3+)"),
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion",
        "Topic :: Scientific/Engineering :: Image Recognition",
    ],
    license="GPLv3+",
    author="Jerome Flesch",
    author_email="jflesch@gmail.com",
    packages=[
        'pytestshot',
    ],
    package_dir={
        'pytestshot': 'src/pytestshot',
    },
    scripts=[],
    install_requires=[
        "Pillow",
        "pypillowfight",
    ],
)
