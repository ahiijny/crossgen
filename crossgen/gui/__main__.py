import sys

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from .crossgen_qt import CrossgenQt

def main():
	app = QApplication([])
	app.setStyle('Fusion')
	window = CrossgenQt(app)
	window.show()
	exit_code = app.exec_()
	return exit_code

if __name__ == "__main__":
	sys.exit(main())
