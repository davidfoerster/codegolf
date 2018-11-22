#!/usr/bin/python3
# See https://codegolf.stackexchange.com/questions/150936/is-it-a-pleasing-number
import itertools
import collections.abc


_base_format_chars = { 2: 'b', 8: 'o', 10: 'd', 16: 'x' }
_digits = list(map(chr, itertools.chain(
	range(ord('0'), ord('9') + 1), range(ord('A'), ord('Z') + 1))))

def int2str( n, base, prefix_positive=False ):
	fmt = _base_format_chars.get(base)
	if fmt is not None:
		return format(n, fmt)

	if not isinstance(n, int):
		bad_type = ('number', type(n))
	elif not isinstance(base, int):
		bad_type = ('base', type(base))
	else:
		bad_type = None
	if bad_type is not None:
		raise TypeError(
			'Expected {:s} to be an int, got a {0.__module__:s}.{0.__qualname__:s}'
				.format(*bad_type))
	if base < 2 or base > len(_digits):
		raise ValueError(
			'Expected base to be between 2 and {:d}, got {:d}'
				.format(len(_digits), base))

	if n == 0:
		return '0'
	if n > 0:
		prefix = '+' if prefix_positive else ''
	else:
		prefix = '-'
		n = -n

	s = []
	while n:
		n, digit = divmod(n, base)
		s.append(_digits[digit])

	s.append(prefix)
	return ''.join(reversed(s))


def is_pleasing_number( n, base=10 ):
	if isinstance(n, int):
		ns = int2str(n, base)
	else:
		ns = n.upper()
		n = int(n, base)
	if n < 0:
		raise ValueError('Expected a non-negative number, got {:d}'.format(n))
	if all(map(ns[0].__eq__, ns)):
		raise ValueError(
			'Expected a sequence of at least two distinct digits, got {!r}'
				.format(n))

	prefix = ns.rstrip(ns[-1])
	a = int(max(prefix), base)
	b = len(ns) - len(prefix)
	return a <= 1 or a == 1 << b or round(a ** (1 / b)) ** b == a


def _is_pleasing_number_golfed1(n):p=n.rstrip(n[-1]);a=int(max(p));b=len(n)-len(p);return round(a**(1/b))**b==a


def main( *args ):
	for n in args:
		print('{} => {}, {}'.format(
			n, is_pleasing_number(n), _is_pleasing_number_golfed(n)))


if __name__ == '__main__':
	import sys
	main(*sys.argv[1:])
