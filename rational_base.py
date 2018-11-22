#!/usr/bin/python3 -O
"""
Represent numbers using rational bases

Source: https://codegolf.stackexchange.com/q/157224
"""

import string
from numbers import Rational
from collections.abc import Sequence, ByteString


class strtuple(tuple):
	def __str__(self):
		return ''.join(self)


digits = {
	'alphanum-' + k: strtuple(
		string.digits + getattr(string, 'ascii_{:s}case'.format(k)))
	for k in ('upper', 'lower')
}


import fractions
class Fraction(fractions.Fraction):

	def __new__(cls, *args):
		if len(args) == 1 and isinstance(args[0], cls):
			return args[0]
		return super().__new__(cls, *args)


	def explode(self, n):
		return n // self.numerator * self.denominator


def frange(fstep, start, end=0, return_default=False):
	while return_default or start != end:
		yield start
		start = fstep(start)
		return_default = False


def _verify_base(base, digits=None):
	base = abs(base)
	if base <= 1:
		raise ValueError('Base must be greater than 1')
	if digits is not None and base.numerator > len(digits):
		raise ValueError(
			'Base {0} requires at least {0.numerator:d} digits, not {1!r} ({2:d})'
				.format(base, digits, len(digits)))


def _get_digit_type(digits):
	for i in range(2):
		if isinstance(digits, str):
			return str
		if isinstance(digits, ByteString):
			return bytes
		if not isinstance(digits, Sequence):
			break
		digits = digits[0]

	raise TypeError



def int2str(n, base=Fraction(10), sign_prefixes=strtuple(('-', '')),
	digits=digits['alphanum-upper']
):
	if base is None:
		if digits is not None:
			base = len(digits)
		else:
			raise ValueError("'base' and 'digits' are both None")
	elif not isinstance(base, Rational):
		raise TypeError(
			"'base' must be a Rational type, not {0.__module__}.{0.__qualname__}"
				.format(type(base)))
	_verify_base(base, digits)

	n = int(n)
	base = Fraction(base)
	s = list(map(base.numerator.__rmod__, frange(base.explode, n, 0, True)))
	s.reverse()

	if digits is None:
		return s
	return (sign_prefixes[n >= 0] +
		_get_digit_type(digits)().join(map(digits.__getitem__, map(abs, s))))


def _parse_sign_prefixes(s):
	if not s or len(s) > 2:
		raise ValueError('String is empty or longer than two')
	return s if len(s) == 2 else (s, '')


def _make_argparser():
	import argparse, inspect
	pp = inspect.signature(int2str).parameters

	p = argparse.ArgumentParser(
		formatter_class=argparse.ArgumentDefaultsHelpFormatter,
		**dict(zip(('description', 'epilog'),
			map(str.strip, __doc__.rsplit('\n\n', 1)))))
	p.add_argument('numbers', metavar='N[:Z]', nargs='+',
		help='Numbers and (optional) bases')
	p.add_argument('-b', '--base', metavar='Z',
		default=pp['base'].default,
		help='The default target base')
	p.add_argument('-s', '--sign-prefixes', metavar='CHARS',
		type=_parse_sign_prefixes, default=pp['sign_prefixes'].default,
		help='Characters used as sign prefixes; the first is for negative values, '
			'the second is for positive values and defaults to the empty string if '
			'ommitted.')

	d = p.add_mutually_exclusive_group()
	d.add_argument('-d', '--digits', metavar='CHARS',
		default=pp['digits'].default,
		help='Characters used to represent the digits')
	d.add_argument('--digits-preset', metavar='PRESET',
		choices=digits.keys(), help='Use a named digit preset.')

	return p


def _parse_args(args=None):
	args = _make_argparser().parse_args(args)

	if args.digits_preset:
		args.digits = digits[args.digits_preset]
	elif not args.digits:
		if args.base:
			args.digits = None
		else:
			raise ValueError('At least one of digits and base must be non-empty')

	if args.base:
		args.base = Fraction(args.base)
		_verify_base(args.base, args.digits)
	else:
		args.base = len(args.digits)

	return args


def main(args=None):
	args = _parse_args(args)
	for n in args.numbers:
		n, sep, base = n.partition(':')
		n = int(n)
		base = Fraction(base) if sep else args.base
		s = int2str(n, base, args.sign_prefixes, args.digits)
		if not isinstance(s, str):
			s = '{' + ', '.join(map(str, s)) + '}'
		print('{0:d} = {2:s} (base {1!s})'.format(n, base, s))


if __name__ == '__main__':
	main()
