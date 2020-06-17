from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QPushButton, QVBoxLayout

class CrossgenQt(QMainWindow):
	def __init__(self):
		QMainWindow.__init__(self)

		window = QWidget()
		layout = QVBoxLayout()
		layout.addWidget(QPushButton('Top'))
		layout.addWidget(QPushButton('Bottom'))
		window.setLayout(layout)
		self.setCentralWidget(window)
