from PyQt5.QtCore import (
	QSize,
	QObject,
	QThread,
	pyqtSignal,
	Qt,
	QEvent,
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
	QSizePolicy,
	QComboBox,
)
from PyQt5.QtGui import (
	QTextCursor,
	QKeySequence,
)
from PyQt5.QtWebEngineWidgets import QWebEngineView

from io import StringIO
import sys
import logging

class DebugWindow(QMainWindow):
	FORMAT = "[%(asctime)s] %(message)s"
	DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

	def __init__(self, parent=None):
		super().__init__(parent=parent)
		self.pane = QWidget()
		self.setCentralWidget(self.pane)
		self.sizeHint = lambda : QSize(600, 600)
		self.setWindowTitle("Debug output")

		self.layout = QBoxLayout(QBoxLayout.TopToBottom)
		self.pane.setLayout(self.layout)

		self.config_pane = QWidget()
		self.config_layout = QBoxLayout(QBoxLayout.LeftToRight)
		self.config_layout.setContentsMargins(0, 0, 0, 0)
		self.config_pane.setLayout(self.config_layout)
		self.label = QLabel("Debug level:")
		self.label.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Maximum)
		self.config_layout.addWidget(self.label)
		self.level_chooser = QComboBox()
		self.level_chooser.insertItems(0, ['INFO', 'DEBUG'])
		self.level_chooser.currentTextChanged.connect(self.set_logging_level)
		self.config_layout.addWidget(self.level_chooser)
		self.layout.addWidget(self.config_pane)

		self.debug_pane = QPlainTextEdit()
		self.debug_pane.installEventFilter(self)
		doc = self.debug_pane.document()
		font = doc.defaultFont()
		font.setFamily("Consolas")
		font.setPointSize(10)
		doc.setDefaultFont(font)
		self.debug_pane.setStyleSheet("background-color: black; color: lime;")
		self.debug_pane.setReadOnly(True)

		self.layout.addWidget(self.debug_pane)

		# Post-setup

		self.level_chooser.setCurrentText("INFO")

	# signals

	closed = pyqtSignal()
	interrupt = pyqtSignal() # TODO: connect this to something

	# @Override
	def closeEvent(self, event):
		self.closed.emit()

	# slots

	def set_logging_level(self, level): # TODO: how to make sure combobox keeps in sync?
		if level == "INFO":
			logging.getLogger().setLevel(logging.INFO)
		elif level == "DEBUG":
			logging.getLogger().setLevel(logging.DEBUG)
		else:
			raise NotImplementedError()
		logging.info(f"Logging level set to {level}")

	def append_text(self, text):
		"""Caller must provide their own newlines; no newlines are automatically added"""
		
		# https://stackoverflow.com/questions/13559990/how-to-append-text-to-qplaintextedit-without-adding-newline-and-keep-scroll-at

		self.debug_pane.moveCursor(QTextCursor.End)
		self.debug_pane.insertPlainText(text)
		self.debug_pane.moveCursor(QTextCursor.End)

	
	# @Override
	def eventFilter(self, source, event):
		if event.type() == QEvent.KeyPress:
			key = event.key()
			modifiers = event.modifiers()
			keyseq = QKeySequence(int(modifiers) + key)
			ctrlc = QKeySequence(Qt.CTRL + Qt.Key_C)
			if keyseq.matches(ctrlc) == QKeySequence.ExactMatch:
				self.interrupt.emit()

		return super().eventFilter(source, event) # should return False to not eat the event		
		
if __name__ == "__main__":
	app = QApplication([])
	app.setStyle('Fusion')
	debug = DebugWindow()
	debug.show()
	debug.append_text("Testing 123456789")
	app.exec_()
