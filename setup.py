from setuptools import setup

setup(
    name='PyGreenfoot',
    version="1.0.0",
    description='The java greenfoot in a python package',
    packages=['pygreenfoot', 'pygreenfoot.templates'],
    license="MIT License",
    python_requires=">=3.6.1, <4",
    install_requires=[
        "pygame >= 2.1.2",
        "typing"
    ],
)