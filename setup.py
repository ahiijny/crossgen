from setuptools import setup, find_packages
import os

def read(fname):
	return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
	name="crossgen",
	version="0.0.2",
	description="crossword generation tool",
	long_description=read('README.md'),
	author="ahiijny",
	author_email="ahiijny@gmail.com",
	license="MIT",
	packages=find_packages(),
	python_requires="3",
	install_requires = [
		'networkx',
		'PyQt5',
	],
	entry_points = {
		"gui_scripts" : [
			"crossgen = crossgen.__main__:gui"
		]
		"console_scripts" : [
			"crossgenc = crossgen.__main__:console",
		]
	},
)
