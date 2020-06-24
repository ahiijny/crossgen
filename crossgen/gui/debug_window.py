from PyQt5.QtCore import (
	QSize,
	QObject,
	QThread,
	pyqtSignal,
)
from PyQt5.QtWidgets import (
	QFrame,
	QMainWindow,
	QApplication,
	QWidget,
	QPushButton,
	QBoxLayout,
	QVBoxLayout,
	QTextEdit,
	QPlainTextEdit,
	QLabel,
	QDesktopWidget,
	QMenuBar,
	QAction,
	QMessageBox,
	QFileDialog,
	QSizePolicy
)
from PyQt5.QtWebEngineWidgets import QWebEngineView

from io import StringIO
import logging

class DebugWindow(QMainWindow):
	def __init__(self, parent=None):
		super().__init__(parent=parent)
		self.pane = QWidget()
		self.setCentralWidget(self.pane)
		self.sizeHint = lambda : QSize(600, 600)
		self.setWindowTitle("Debug output")

		self.layout = QBoxLayout(QBoxLayout.TopToBottom)
		self.pane.setLayout(self.layout)

		self.debug_pane = QPlainTextEdit()
		doc = self.debug_pane.document()
		font = doc.defaultFont()
		font.setFamily("Consolas")
		font.setPointSize(10)
		doc.setDefaultFont(font)
		self.debug_pane.setStyleSheet("background-color: black; color: lime;")
		self.debug_pane.setReadOnly(True)

		self.layout.addWidget(self.debug_pane)

	# signals

	closed = pyqtSignal()

	# @Override
	def closeEvent(self, event):
		self.closed.emit()

	# slots

	def append_text(self, text):
		self.debug_pane.appendPlainText(text)
		
if __name__ == "__main__":
	app = QApplication([])
	app.setStyle('Fusion')
	debug = DebugWindow()
	debug.show()
	debug.append_text("Testing 123456789")
	app.exec_()
