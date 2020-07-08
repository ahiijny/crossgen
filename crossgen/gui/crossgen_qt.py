from PyQt5.QtCore import (
	QSize,
	QObject,
	QThread,
	pyqtSignal,
	QBuffer,
	QIODevice,
	QUrl,
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
	QDialog,
	QFormLayout,
	QSpinBox,
	QCheckBox,
	QAbstractScrollArea,
)
from PyQt5.QtWebEngineWidgets import (
	QWebEngineView,
)

from PyQt5.QtWebEngineCore import (
	QWebEngineUrlSchemeHandler,
	QWebEngineUrlScheme,
	QWebEngineUrlRequestJob,
)

from io import StringIO
import sys
import logging

import crossgen.command
import crossgen.grid
import crossgen.pretty
from crossgen.gui.debug_window import DebugWindow

# hacky workaround to allow QWebEngineView load html that's
# larger than 2 MB https://stackoverflow.com/questions/48926971/qwebengineview-loading-of-2mb-content
class OutputLoader(QWebEngineUrlSchemeHandler):
	def set_html(self, html):
		self.html = html

	# @Override
	def requestStarted(self, request):
		url = request.requestUrl()
		path = url.path()

		if path != "html.html":
			request.fail(QWebEngineUrlRequestJob.UrlNotFound)
			return

		buffer = QBuffer(parent=self) # need to set parent to avoid buffer lifetime issues
			# see also: https://github.com/qutebrowser/qutebrowser/blob/master/qutebrowser/browser/webengine/webenginequtescheme.py
			# https://riverbankcomputing.com/pipermail/pyqt/2016-September/038076.html
		buffer.open(QIODevice.WriteOnly)
		buffer.write(self.html.encode("utf8"))
		buffer.close()
		request.destroyed.connect(buffer.deleteLater)

		request.reply("text/html".encode("utf8"), buffer)

output_scheme = QWebEngineUrlScheme("output".encode("utf8"))
output_scheme.setSyntax(QWebEngineUrlScheme.Syntax.Path)
QWebEngineUrlScheme.registerScheme(output_scheme)

class CrossgenQt(QMainWindow):
	def __init__(self, app):
		# Setup

		QMainWindow.__init__(self)
		self.app = app
		dim = app.primaryScreen().availableGeometry()
		self.sizeHint = lambda : QSize(dim.width(), dim.height())

		# Attributes

		self.save_path = ""
		self.is_dirty = False
		self.confirm_generate = False # if generated crosswords aren't saved, prompt user
		self.max = 10
		self.batch = 5
		self.capitalize = True
		self.remove_spaces = True
		self.no_progress_timeout = 5 # number of batches
		self.words = []
		self.crosswords = []
		self.gen_worker = None
		self.save_worker = None
		self.output_loader = OutputLoader()
		self.html = ""
		self.options_window = None
		self.debug_window = None
		self.qt_log_handler = None

		# Build UI

		self._build_main_menu()

		self.layout = QBoxLayout(QBoxLayout.LeftToRight)
		margins = self.layout.contentsMargins()
		margins.setBottom(2)
		self.layout.setContentsMargins(margins)
		self.pane = QWidget()
		self.pane.setLayout(self.layout)

		self.input_pane = self._build_input_pane()
		size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		size_policy.setHorizontalStretch(5)
		self.input_pane.setSizePolicy(size_policy)
		self.layout.addWidget(self.input_pane)

		self.centre_pane = self._build_centre_pane()
		self.layout.addWidget(self.centre_pane)

		self.output_pane = self._build_output_pane()
		size_policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
		size_policy.setHorizontalStretch(7)
		self.output_pane.setSizePolicy(size_policy)
		self.layout.addWidget(self.output_pane)
		
		self.setCentralWidget(self.pane)

		# Post-setup

		self.output_view.page().profile().installUrlSchemeHandler("output".encode("utf8"), self.output_loader)
		self.output_view.loadStarted.connect(self.on_output_load_started)
		self.output_view.loadProgress.connect(self.on_output_load_progress)
		self.output_view.loadFinished.connect(self.on_output_load_finished)

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
		file_menu = menubar.addMenu('&File')
		tools_menu = menubar.addMenu('&Tools')

		act_save = QAction('&Save', self) # http://zetcode.com/gui/pyqt5/menustoolbars/
		act_save.setShortcut('Ctrl+S')
		act_save.setStatusTip('Save the generated crosswords')
		act_save.triggered.connect(self.save)
		file_menu.addAction(act_save)

		act_save_as = QAction('&Save As...', self)
		act_save_as.setStatusTip('Save a copy of the generated crosswords')
		act_save_as.triggered.connect(self.save_as)
		file_menu.addAction(act_save_as)

		act_exit = QAction('&Exit', self)
		act_exit.setShortcut('Alt+F4')
		act_exit.setStatusTip('Exit application')
		act_exit.triggered.connect(self.close)
		file_menu.addAction(act_exit)

		act_options = QAction('Advanced &options', self)
		act_options.setStatusTip('More options')
		act_options.triggered.connect(self.show_advanced_options)
		tools_menu.addAction(act_options)

		act_debug = QAction('&Debug logging', self)
		act_debug.setStatusTip('Show debug output for crossword generation')
		act_debug.triggered.connect(self.show_debug)
		tools_menu.addAction(act_debug)

		tools_menu.addSeparator()

		act_about = QAction('&About', self)
		act_about.setStatusTip('Show information')
		act_about.triggered.connect(self.show_about)
		tools_menu.addAction(act_about)

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

	def _build_centre_pane(self):
		centre_layout = QBoxLayout(QBoxLayout.TopToBottom)
		centre_layout.setContentsMargins(0, 40, 0, 40)
		centre_pane = QWidget()
		centre_pane.setLayout(centre_layout)

		self.btn_generate = QPushButton('Generate')
		self.btn_generate.clicked.connect(self.on_generate_pressed)
		centre_layout.addWidget(self.btn_generate)

		options_layout = QFormLayout()
		options_layout.setContentsMargins(0, 5, 0, 0)
		options_pane = QWidget()
		options_pane.setLayout(options_layout)

		self.max_spinbox = QSpinBox()
		self.max_spinbox.setMinimum(1)
		self.max_spinbox.setMaximum(999)
		self.max_spinbox.setValue(self.max)
		self.max_spinbox.valueChanged.connect(self.set_max_crosswords)
		options_layout.addRow("How many:", self.max_spinbox)
		centre_layout.addWidget(options_pane)

		self.caps_checkbox = QCheckBox()
		self.caps_checkbox.setText("Capitalize all letters")
		self.caps_checkbox.setChecked(self.capitalize)
		def set_caps(checked):
			self.capitalize = checked
		self.caps_checkbox.toggled.connect(set_caps)
		centre_layout.addWidget(self.caps_checkbox)

		self.spaces_checkbox = QCheckBox()
		self.spaces_checkbox.setText("Remove spaces")
		self.spaces_checkbox.setChecked(self.remove_spaces)
		def set_spaces(checked):
			self.remove_spaces = checked
		self.spaces_checkbox.toggled.connect(set_spaces)
		centre_layout.addWidget(self.spaces_checkbox)

		return centre_pane

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
		web_frame.setStyleSheet("""border:1px solid #B9B9B9""") # hack to make output pane have same border colour as input pane
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
		self.words = [line.strip() for line in lines if len(line.strip()) > 0]
		word_count = len(self.words)
		label_text = f"{word_count} "
		if word_count == 1:
			label_text += "word"
		else:
			label_text += "words"
		self.word_count_label.setText(label_text)

		if self.gen_worker is None:
			if word_count > 0:
				self.statusBar().showMessage("Ready")
			else:
				self.statusBar().showMessage("Enter some words!")

	def set_max_crosswords(self, number):
		self.max = number

	class GenerateCrosswordsWorker(QThread):
		num_done_updated = pyqtSignal(int)
		finished = pyqtSignal()

		def __init__(self, words, max, batch, capitalize, remove_spaces, no_progress_timeout):
			super().__init__()
			self.words = words
			self.max = max
			self.batch = batch
			self.capitalize = capitalize
			self.remove_spaces = remove_spaces
			self.no_progress_timeout = no_progress_timeout
			self.crosswords = []

		def run(self):
			def progress_callback(num_done):
				self.num_done_updated.emit(num_done)

			self.crosswords = crossgen.command.create_crosswords(words=self.words, max=self.max, batch=self.batch,
					progress_callback=progress_callback, capitalize=self.capitalize, remove_spaces=self.remove_spaces,
					no_progress_timeout=self.no_progress_timeout)

			self.finished.emit()

	def update_progress(self, num_done):
		if num_done == 0:
			self.statusBar().showMessage(f"Could not generate any crosswords with the words given.")
			return

		self.statusBar().showMessage(f"Generated {num_done}/{self.used_max} crosswords...")

	def on_generate_pressed(self):
		if not self.can_generate(): # avoid generating while already generating, and prompt if previous crosswords are unsaved
			return

		self.btn_generate.setEnabled(False)
		self.used_words = list(self.words) # save these values in a separate variable in case they change while generating
		self.used_max = self.max

		self.gen_worker = CrossgenQt.GenerateCrosswordsWorker(self.used_words, self.used_max,
				self.batch, self.capitalize, self.remove_spaces, self.no_progress_timeout)
		self.gen_worker.num_done_updated.connect(self.update_progress)
		self.gen_worker.finished.connect(self.on_done_generating)
		self.gen_worker.start()
		self.statusBar().showMessage("Generating crosswords...")

	def on_interrupt_generate(self):
		if self.gen_worker is not None:
			self.gen_worker.terminate()
			self.on_done_generating()
			print(file=sys.stderr)
			logging.info("Crossword generation interrupted with Ctrl+C!")
			self.statusBar().showMessage(f"Crossword generation interrupted with Ctrl+C!")

	def on_done_generating(self):
		self.crosswords = self.gen_worker.crosswords
		self.on_output_changed(self.crosswords, self.used_words)
		if len(self.crosswords) == 0:
			self.statusBar().showMessage(f"Could not generate any crosswords.")
		else:
			self.statusBar().showMessage(f"Generated {len(self.crosswords)} crosswords!")
		self.gen_worker = None
		self.btn_generate.setEnabled(True)

	def on_output_changed(self, crosswords=[], words=[]):
		logging.info(f"Output changed: num_crosswords={len(crosswords)}, words={words}")
		if len(crosswords) > 0:
			strbuf = StringIO()
			pretty_printer = crossgen.pretty.HtmlGridPrinter(outstream=strbuf)
			pretty_printer.print_crosswords(crosswords, words)
			self.html = strbuf.getvalue()
			logging.info(f"Length of output html = {len(self.html)} bytes")
			# self.output_view.setHtml(self.html)
			## ^ this old solution fails for file sizes > 2 MB https://doc.qt.io/qt-5/qwebengineview.html#setHtml
			self.output_loader.set_html(self.html)
			self.output_view.load(QUrl("output:html.html"))
			self.set_dirty(True)
		elif len(crosswords) == 0 and len(words) != 0:
			self.output_view.setHtml("")

	def on_output_load_started(self):
		logging.debug("Output display load started")
		self.statusBar().showMessage(f"Loading output...")

	def on_output_load_progress(self, progress):
		logging.debug(f"Output display load progress: {progress}%")
		self.statusBar().showMessage(f"Loading output {progress}%...")

	def on_output_load_finished(self, is_success):
		logging.debug(f"Output display load finished: result={is_success}")
		if is_success:
			self.statusBar().showMessage(f"Generated {len(self.crosswords)} crosswords!")
		else:
			self.statusBar().showMessage(f"Error: Could not load output.")

	def set_dirty(self, is_dirty):
		"""Dirty = if the file has been changed since it was last saved"""
		self.is_dirty = is_dirty
		self._refresh_window_title()			

	class SaveCrosswordsWorker(QThread):
		done = pyqtSignal(bool) # bool is_success

		def __init__(self, save_path, html):
			super().__init__()
			self.save_path = save_path
			self.html = html

		def run(self):
			try:
				with open(self.save_path, "w", encoding="utf-8") as f:
					f.write(self.html)
				self.done.emit(True)
			except IOError as err:
				print("Save error:", err, file=sys.stderr)
				self.done.emit(False)

	def can_save(self):
		if self.save_worker is not None:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			msg.setWindowTitle("Save Crosswords")
			msg.setText("Not done previous save yet!")			
			msg.setStandardButtons(QMessageBox.Ok)
			msg.exec_()
			return False
		return True

	def save(self):
		if not self.can_save():
			return

		if self.save_path == "":
			self.save_as()
			return

		save_path = self.save_path
		html = self.html

		def done_save(is_success):
			if is_success:
				self.statusBar().showMessage(f"Saved to {save_path}")
				self.set_dirty(False)
			else:
				self.statusBar().showMessage(f"Error: Failed to save to {save_path}")
			self.save_worker = None

		self.save_worker = CrossgenQt.SaveCrosswordsWorker(save_path, html)
		self.save_worker.done.connect(done_save)
		self.save_worker.start()
		self.statusBar().showMessage(f"Saving...")

	def save_as(self):
		if not self.can_save():
			return

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
		if len(self.words) == 0:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			msg.setWindowTitle("Generate Crosswords")
			msg.setText("Enter some words first!")			
			msg.setStandardButtons(QMessageBox.Ok)
			msg.exec_()
			return False
		if self.gen_worker is not None:
			msg = QMessageBox()
			msg.setIcon(QMessageBox.Information)
			msg.setWindowTitle("Generate Crosswords")
			msg.setText("Already generating!")			
			msg.setStandardButtons(QMessageBox.Ok)
			msg.exec_()
			return False
		if self.confirm_generate and self.is_dirty:
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

	# https://stackoverflow.com/questions/24469662/how-to-redirect-logger-output-into-pyqt-text-widget
	# https://stackoverflow.com/questions/28655198/best-way-to-display-logs-in-pyqt

	class QtLogHandler(logging.Handler, QObject): # multiple inheritance hack
		logged_msg = pyqtSignal(str)
		stream = 1

		def __init__(self):
			logging.Handler.__init__(self)
			QObject.__init__(self)

		def emit(self, record):
			msg = self.format(record) + "\n"
			self.logged_msg.emit(msg)

		def write(self, text):
			self.logged_msg.emit(text)

		def flush(self):
			pass			

	def show_debug(self):
		if self.debug_window is None:
			self.debug_window = DebugWindow(parent=self)
			current_width = self.frameGeometry().width()
			current_height = self.frameGeometry().height()
			self.debug_window.sizeHint = lambda : QSize(current_width/3, current_height)
			self.qt_log_handler = self.QtLogHandler()
			formatter = logging.Formatter(fmt=self.debug_window.FORMAT, datefmt=self.debug_window.DATE_FORMAT)
			self.qt_log_handler.setFormatter(formatter)
			self.qt_log_handler.logged_msg.connect(self.debug_window.append_text)

			logging.basicConfig(format=self.debug_window.FORMAT, datefmt=self.debug_window.DATE_FORMAT, level=logging.INFO)
			logging.getLogger().addHandler(self.qt_log_handler)
			logging.getLogger().setLevel(logging.INFO)
			logging.info("Set up logging")
			old_stderr = sys.stderr

			def on_debug_closed():
				sys.stderr = old_stderr
				logging.info("sys.stderr restored back to original value")

			self.debug_window.closed.connect(on_debug_closed)
			self.debug_window.interrupt.connect(self.on_interrupt_generate)

		if not self.debug_window.isVisible():
			# might be running in pythonw/gui_scripts/windowed mode
			# should remove the default basicConfig StreamHandler from logging or else it'll show errors
			# hacky hack
			if sys.stderr is None:	
				for handler in logging.getLogger().handlers:
					if isinstance(handler, logging.StreamHandler) and handler.stream is None:
						logging.getLogger().removeHandler(handler)
						break

			sys.stderr = self.qt_log_handler
			
			logging.info("sys.stderr now prints to the debug window")

		self.debug_window.show()
		self.debug_window.activateWindow()

	def show_advanced_options(self):
		if self.options_window is not None:
			self.options_window.show()
			self.options_window.activateWindow()
			return

		self.options_window = msg = QDialog(parent=self)
		msg.setWindowTitle("Advanced options")
		msg.setModal(False)

		options_layout = QFormLayout()
		msg.setLayout(options_layout)

		batch_spinbox = QSpinBox()
		batch_spinbox.setMinimum(1)
		batch_spinbox.setMaximum(999)
		batch_spinbox.setValue(self.batch)
		def set_batch_size(num):
			self.batch = num
		batch_spinbox.valueChanged.connect(set_batch_size)
		options_layout.addRow("Batch size (crosswords):", batch_spinbox)

		timeout_spinbox = QSpinBox()
		timeout_spinbox.setMinimum(-1)
		timeout_spinbox.setMaximum(999)
		timeout_spinbox.setValue(self.no_progress_timeout)
		def set_no_progress_timeout(num):
			self.no_progress_timeout = num
		timeout_spinbox.valueChanged.connect(set_no_progress_timeout)
		options_layout.addRow("No progress timeout (batches):", timeout_spinbox)
		msg.show()

	def show_about(self):
		msg = QDialog(parent=self)
		msg.setWindowTitle("About crossgen")
		msg.setModal(True)

		about_pane = QTextEdit()
		about_pane.setReadOnly(True)
		about_pane.setStyleSheet("""font-size: 8pt;""")
		about_pane.setText("""A quick, hacky crossword generation tool.

The crosswords are generated randomly, so they may be different every time!

Scores are calculated computed somewhat arbitrarily, with the main intent of sorting nicer looking crosswords closer to the top, for some definition of "nicer".

By: ahiijny (2020)
""")
		about_pane.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
		layout = QVBoxLayout()
		layout.addWidget(about_pane)
		msg.setLayout(layout)

		size_hint = msg.minimumSizeHint()
		msg.setMinimumSize(QSize(size_hint.width(), size_hint.height() * 1.2))
		msg.exec_()
