from PyQt5.QtCore import (
	QSize,
)
from PyQt5.QtWidgets import (
	QMainWindow,
	QApplication,
	QWidget,
	QPushButton,
	QBoxLayout,
	QTextEdit,
	QPlainTextEdit,
	QLabel,
	QDesktopWidget,
	QMenuBar,
	QAction,
	QMessageBox,
)

class CrossgenQt(QMainWindow):
	def __init__(self, app):
		# Setup

		QMainWindow.__init__(self)
		self.app = app
		dim = app.primaryScreen().availableGeometry()
		self.sizeHint = lambda : QSize(dim.width(), dim.height())

		# Properties

		self.save_path = ""
		self.is_dirty = False

		# Build UI

		self._build_main_menu()

		self.layout = QBoxLayout(QBoxLayout.LeftToRight)
		margins = self.layout.contentsMargins()
		margins.setBottom(2)
		self.layout.setContentsMargins(margins)
		self.pane = QWidget()
		self.pane.setLayout(self.layout)

		self.input_pane = self._build_input_pane()
		self.layout.addWidget(self.input_pane)

		self.btn_generate = QPushButton('Generate')
		self.layout.addWidget(self.btn_generate)

		self.output_pane = self._build_output_pane()
		self.layout.addWidget(self.output_pane)		
		
		self.setCentralWidget(self.pane)

		# Post-setup

		self.on_text_changed() # populate status bar with initial status
		self._refresh_window_title()

	def _refresh_window_title(self):
		title = "Crossgen "
		if self.save_path != "":
			title += " - " + self.save_path + " "
		if self.is_dirty:
			title += "(*)"
		self.setWindowTitle(title)

	def _build_main_menu(self):
		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')

		act_save = QAction('&Save', self) # http://zetcode.com/gui/pyqt5/menustoolbars/
		act_save.setShortcut('Ctrl+S')
		act_save.setStatusTip('Save the generated crosswords')
		act_save.triggered.connect(self.save)
		fileMenu.addAction(act_save)

		act_save_as = QAction('&Save As...', self)
		act_save_as.setStatusTip('Save a copy of the generated crosswords')
		act_save_as.triggered.connect(self.save_as)
		fileMenu.addAction(act_save_as)

		act_exit = QAction('&Exit', self)
		act_exit.setShortcut('Alt+F4')
		act_exit.setStatusTip('Exit application')
		act_exit.triggered.connect(self.close)
		fileMenu.addAction(act_exit)

	def _build_input_pane(self):
		input_layout = QBoxLayout(QBoxLayout.TopToBottom)
		input_pane = QWidget()
		input_pane.setLayout(input_layout)

		input_label = QLabel("Input (list of words, separated by newlines):")
		input_label.setStyleSheet("""font-size: 10pt""")
		input_layout.addWidget(input_label)

		self.text_input = QPlainTextEdit()
		doc = self.text_input.document()
		font = doc.defaultFont()
		font.setFamily("Consolas")
		font.setPointSize(13)
		doc.setDefaultFont(font)
		self.text_input.textChanged.connect(self.on_text_changed)
		input_layout.addWidget(self.text_input)

		self.word_count_label = QLabel("0 words")
		input_layout.addWidget(self.word_count_label)

		return input_pane

	def _build_output_pane(self):
		output_pane = QWidget()
		output_layout = QBoxLayout(QBoxLayout.TopToBottom)
		output_pane.setLayout(output_layout)

		output_label = QLabel("Output:")
		output_label.setStyleSheet("""font-size: 10pt""")
		output_layout.addWidget(output_label)

		self.output_view = QTextEdit()
		self.output_view.setReadOnly(True)
		output_layout.addWidget(self.output_view)

		self.output_label = QLabel("")
		output_layout.addWidget(self.output_label)

		return output_pane

	def on_text_changed(self):
		text = self.text_input.document().toPlainText()
		lines = text.split("\n")
		word_count = sum(len(line) > 0 and not line.isspace() for line in lines)
		label_text = f"{word_count} "
		if word_count == 1:
			label_text += "word"
		else:
			label_text += "words"
		self.word_count_label.setText(label_text)

		if word_count > 0:
			self.statusBar().showMessage("Ready")
			self.btn_generate.setEnabled(True)
		else:
			self.statusBar().showMessage("Enter some words!")
			self.btn_generate.setEnabled(False)

		if (len(self.text_input.document().toPlainText()) > 0
				or len(self.output_view.document().toPlainText()) > 0):
			self.set_dirty(True)
		else:
			self.set_dirty(False)

	def set_dirty(self, is_dirty):
		"""Dirty = if the file has been changed since it was last saved"""
		self.is_dirty = is_dirty
		self._refresh_window_title()			

	def save(self):
		if self.save_path == "":
			self.save_as()
			return

		self.set_dirty(False)

	def save_as(self):
		self.set_dirty(False)

	def closeEvent(self, event):
		"""Override"""
		if self.can_exit():
			event.accept()
		else:
			event.ignore()

	def can_exit(self):
		if self.is_dirty:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Warning)
			msg.setWindowTitle("Exit Application")
			msg.setText("Are you sure you want to exit?")			
			msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
			retval = msg.exec_()
			if retval == QMessageBox.No:
				return False
		return True
