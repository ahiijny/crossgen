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
)

class CrossgenQt(QMainWindow):
	def __init__(self, app):
		QMainWindow.__init__(self)
		self.app = app
		self.setWindowTitle("Crossgen")
		dim = app.primaryScreen().availableGeometry()
		self.sizeHint = lambda : QSize(dim.width(), dim.height())
		self.statusBar().showMessage("Ready")

		self._build_main_menu()

		self.layout = QBoxLayout(QBoxLayout.LeftToRight)
		self.pane = QWidget()
		self.pane.setLayout(self.layout)

		self.input_pane = self._build_input_pane()
		self.layout.addWidget(self.input_pane)

		self.btn_generate = QPushButton('Generate')
		self.layout.addWidget(self.btn_generate)

		self.output_pane = self._build_output_pane()
		self.layout.addWidget(self.output_pane)		
		
		self.setCentralWidget(self.pane)

	def _build_main_menu(self):
		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')

		act_exit = QAction('&Exit', self) # http://zetcode.com/gui/pyqt5/menustoolbars/
		act_exit.setShortcut('Alt+F4')
		act_exit.setStatusTip('Exit application')
		act_exit.triggered.connect(self.app.quit)
		fileMenu.addAction(act_exit)

	def _build_input_pane(self):
		input_layout = QBoxLayout(QBoxLayout.TopToBottom)
		input_pane = QWidget()
		input_pane.setLayout(input_layout)

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

		self.output_view = QTextEdit("<b>Hello</b> <i>Qt!</i>")
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

