from string import whitespace
from setuptools import setup

def get_version():
    with open("pygreenfoot/__init__.py", "r") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[-1].strip(whitespace + "\"\'")
    raise ValueError("No version in __init__.py")

setup(
    name='PyGreenfoot',
    version=get_version(),
    setup_requires=["setuptools_scm", "setuptools", ],
    description='The java greenfoot in a python package',
    packages=['pygreenfoot', 'pygreenfoot.templates', 'pygreenfoot.images'],
    license="GNU General Public License, version 2, with the Classpath Exception",
    python_requires=">=3.6.1, <4",
    install_requires=[
        "pygame >= 2.1.2",
        "typing"
    ],
    platforms=["linux", "mac", "win32"],
    include_package_data=True,
    package_dir={".": "pygreenfoot"},
    package_data={
        "": ["*.png", "*.jpg", "*.ico"]
    },
    extras_requires={
        "plantuml image generation": ["plantuml>=0.3.0"]
    }
)
