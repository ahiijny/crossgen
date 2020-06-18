from PyQt5.QtCore import (
	QSize,
	QThread,
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

import crossgen.command
import crossgen.grid
import crossgen.pretty

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
		self.confirm_generate = True # if generated crosswords aren't saved, prompt user
		self.max = 5
		self.batch = 1
		self.crosswords = []

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
		self.btn_generate.clicked.connect(self.on_generate_pressed)
		self.layout.addWidget(self.btn_generate)

		self.output_pane = self._build_output_pane()
		self.layout.addWidget(self.output_pane)		
		
		self.setCentralWidget(self.pane)

		# Post-setup

		self._refresh_window_title()
		self.on_input_changed() # populate status bar with initial status
		self.on_output_changed()

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
		self.text_input.textChanged.connect(self.on_input_changed)
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

		#self.output_view = QTextEdit()
		self.output_view = QWebEngineView()
		self.output_view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		#self.output_view.setReadOnly(True)
		web_frame = QFrame()
		web_frame.setStyleSheet("""border:1px solid #B9B9B9""") # hack to back output pane have some border colour as input pane
		web_frame_layout = QVBoxLayout()
		web_frame_layout.setSpacing(0)
		web_frame_layout.setContentsMargins(0, 0, 0, 0)
		web_frame.setLayout(web_frame_layout)
		web_frame_layout.addWidget(self.output_view)
		output_layout.addWidget(web_frame)

		self.output_label = QLabel("")
		output_layout.addWidget(self.output_label)

		return output_pane

	def on_input_changed(self):
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

	def on_generate_pressed(self):
		# TODO: long-running tasks should be done in a new thread so that it
		# doesn't block the GUI thread

		if self.confirm_generate and self.is_dirty:
			if not self.can_generate():
				return

		text = self.text_input.document().toPlainText()
		lines = text.split("\n")
		words = [line.strip() for line in lines if not line.isspace()]

		def progress_callback(num_crosswords):
			self.statusBar().showMessage(f"Generated {num_crosswords}/{self.max} crosswords...")

		self.crosswords = crossgen.command.create_crosswords(words=words, max=self.max, batch=self.batch,
				progress_callback=progress_callback)
		self.on_output_changed()
		self.statusBar().showMessage(f"Generated {self.max} crosswords")

	def on_output_changed(self):
		if len(self.crosswords) > 0:
			strbuf = StringIO()
			pretty_printer = crossgen.pretty.HtmlGridPrinter(outstream=strbuf)
			pretty_printer.print_crosswords(self.crosswords)
			html = strbuf.getvalue()
			self.output_view.setHtml(html)
			self.set_dirty(True)

	def set_dirty(self, is_dirty):
		"""Dirty = if the file has been changed since it was last saved"""
		self.is_dirty = is_dirty
		self._refresh_window_title()			

	def save(self):
		if self.save_path == "":
			self.save_as()
			return

		def on_htmlled(html):
			print(html) # TODO actually save the file

			self.statusBar().showMessage(f"Saved to {self.save_path}")
			self.set_dirty(False)

		self.output_view.page().toHtml(on_htmlled)

	def save_as(self):
		dialog = QFileDialog(self, caption="Save Crosswords", directory="./crosswords.html", filter="HTML files (*.html)")
		dialog.setDefaultSuffix(".html")
		dialog.setFileMode(QFileDialog.AnyFile) # including files that don't exist
		dialog.setAcceptMode(QFileDialog.AcceptSave)

		result = dialog.exec_()
		if not result: # user rejected the save
			return

		file_names = dialog.selectedFiles()
			# output looks something like ("C:/Users/Person/Documents/crosswords.html", 'HTML files (*.html)')
		if len(file_names) == 0:
			return
		self.save_path = file_names[0]
		self.save()

	def closeEvent(self, event):
		"""@Override"""
		if self.can_exit():
			event.accept()
		else:
			event.ignore()

	def can_generate(self):
		if self.is_dirty:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			msg.setWindowTitle("Generate Crosswords")
			msg.setText("Current crosswords aren't saved. Generate new crosswords?")			
			msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
			retval = msg.exec_()
			if retval == QMessageBox.No:
				return False
		return True

	def can_exit(self):
		if self.is_dirty:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Warning)
			msg.setWindowTitle("Exit Application")
			msg.setText("You have unsaved changes. Are you sure you want to exit?")			
			msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
			retval = msg.exec_()
			if retval == QMessageBox.No:
				return False
		return True
