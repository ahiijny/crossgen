import unicodedata
import sys, locale, os

def fold(words):
	for word in words:
		word = word.strip()
	pass

def test():
	print(sys.stdout.encoding)
	print(sys.stdout.isatty())
	print(locale.getpreferredencoding())
	print(sys.getfilesystemencoding())
	sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf8', buffering=1)
	print(chr(246), chr(9786), chr(9787))

	s = "éçâdだ"
	d = unicodedata.normalize("NFD", s)
	c = unicodedata.normalize("NFC", s)
	kd = unicodedata.normalize("NFKD", s)
	kc = unicodedata.normalize("NFKC", s)
	print("\nNFD:")
	for i, ch in enumerate(d):
		print(ch, ord(ch), unicodedata.name(ch))
	print("\nNFC:")
	for i, ch in enumerate(c):
		print(ch, ord(ch), unicodedata.name(ch))
	print("\nNFKD:")
	for i, ch in enumerate(kd):
		print(ch, ord(ch), unicodedata.name(ch))
	print("\nNFKC:")
	for i, ch in enumerate(kd):
		print(ch, ord(ch), unicodedata.name(ch))
	while True:
		x = input("> ")
		print(x, )

if __name__ == "__main__":
	test()