#!/usr/bin/python3
# https://codegolf.stackexchange.com/q/172281
import sys
import string


CIPHER_DICT = str.maketrans(
	string.ascii_uppercase, 'ECDFIGHJOKLMNPUQRSTVAWXYZB')
DECIPHER_DICT = { v: k for k, v in CIPHER_DICT.items() }
VOWELS = frozenset('AEIOU')
SUFFIX = 'AY'

assert len(CIPHER_DICT) == len(DECIPHER_DICT)


def cipher(s, dictionary=CIPHER_DICT, suffix=SUFFIX):
	t = s.translate(dictionary)
	return t if not t or t[0] in VOWELS else ''.join((t[1:], t[0], suffix))


c1=lambda s:''.join('ECDFIGHJOKLMNPUQRSTVAWXYZB'[ord(c)-65]for c in(s[1:]+s[0]+'UX',s)[s[0]in'AEIOU'])


def decipher(s, dictionary=DECIPHER_DICT, suffix=SUFFIX):
	if s.endswith(suffix) and suffix:
		last = len(s) - len(suffix) - 1
		s = s[last] + s[:last]

	return s.translate(dictionary)



def main(args=None):
	if args is None:
		args = sys.argv[1:] or map(str.strip, sys.stdin)

	for s in map(str.upper, args):
		expected = cipher(s)
		print(s, '=>', expected, '=>', decipher(expected))

		golfed = c1(s)
		success = golfed == expected
		print(s, '=>', golfed, end=(', FAILED!\n', '\n\n')[success])

		if not success:
			return 1

	return 0


if __name__ == '__main__':
	sys.exit(main())
