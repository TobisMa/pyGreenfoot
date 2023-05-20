from setuptools import find_packages, setup

setup(
    name='PyGreenfoot',
    version="1.0.0",
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
