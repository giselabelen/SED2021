from setuptools import setup, find_packages
setup(
   name='DEVSParser',
   version='0.1.0',
   author='Emiliano Lucero',
   author_email='eslucero2010@gmail.com',
   packages=find_packages(),
   scripts=[],
   url='',
   license='LICENSE.txt',
   description='Parsing tools for DEVS enviroment.',
   long_description=open('README.md').read(),
   install_requires=[
       "pytest",
       "pyparsing >= 3.0.7"
   ],
)
