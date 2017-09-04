from setuptools import setup, find_packages
import os

def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name="crosschan",
	version="0.1.0",
	description="derp crossword helper tool",
	long_description=read('README.md'),
	author="ahiijny",
	author_email="ahiijny@gmail.com",
	license="MIT",
	packages=find_packages(),
	entry_points = {
		"console_scripts" : [
			"crosschan = crosschan.__main__:main",
		],
	},
	install_requires = [
		"require-python-3"
	],
)
