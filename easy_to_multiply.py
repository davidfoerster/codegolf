#!/usr/bin/python3
# See https://codegolf.stackexchange.com/questions/151130/easy-to-multiply-numbers
import array, itertools


def is_easy_to_multiply( a, b ):
	if not (isinstance(a, int) and isinstance(b, int)):
		raise TypeError(
			'Expected int arguments, got {} and {}'.format(type(a), type(b)))

	a = array.array('B', map(int, str(abs(a))))
	b = array.array('B', map(int, str(abs(b))))
	p = array.array('Q', bytearray((len(a) + len(b)) << 4))
	for i, x in enumerate(a):
		for j, y in enumerate(b, i + 1):
			p[j] += x * y
			if p[j] >= 10:
				return False
	return True


def main( *args ):
	if not args or (len(args) == 1 and args[0] == '-'):
		args = (l.rstrip('\n') for l in sys.stdin)
	for a in args:
		if isinstance(a, str):
			a = tuple(map(int, a.split('x', 1)))
		print(a[0], 'x', a[1], '=>', is_easy_to_multiply(*a))


if __name__ == '__main__':
	import sys
	if len(sys.argv) == 2 and sys.argv[1] == '--test':
		main((331, 1021), (1021, 331), (101, 99), (333, 11111), (243, 201))
		print()
		main((431, 1021), (12, 16), (3, 4), (3333, 1111), (310, 13))
	else:
		main(*sys.argv[1:])
