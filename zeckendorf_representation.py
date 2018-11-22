#!/usr/bin/python3 -O
# https://codegolf.stackexchange.com/q/173601
__all__ = ('encode', 'decode')
import sys
import argparse
import itertools

String = (str, bytes)


def decode(bits):
	if isinstance(bits, String):
		bits = int(bits, 2)
	return sum(map(logical_and, int_bits(bits), _fibonacci_series_impl(1, 2)))


def encode(n, *, reverse=True, output_type=str):
	z = _encode_impl(n)
	if reverse:
		z = reversed(tuple(z))
	if output_type is not None:
		z = sum(map(int.__lshift__, map(bool, z), itertools.count()))
		if output_type is str:
			z = format(z, 'b')
		elif output_type is not int:
			raise ValueError('Invalid output type: {!r}'.format(output_type))
	return z


def _encode_impl(n):
	validate_int(n)
	for fib in reversed(tuple(
		itertools.takewhile(n.__ge__, _fibonacci_series_impl()))
	):
		if n >= fib:
			yield fib
			n -= fib
			if n <= 0:
				assert n == 0
				break
		else:
			yield 0


def fibonacci_series(current=0, successor=1):
	validate_int(current, 'current')
	validate_int(successor, 'successor')
	assert (
		(current == 0 and successor == 1) or (current <= successor and tuple(_fibonaci_series_from(current, 2)) == (current, successor))), \
		('Expected two subsequent items of the Fibonacci series, got {:d} and {:d}'
			.format(current, successor))
	return _fibonacci_series_impl(current, successor)


def _fibonacci_series_impl(current=0, successor=1):
	while True:
		yield current
		current, successor = successor, current + successor


def _fibonaci_series_from(n, count=None):
	n = max(int(n), 0)
	if count == 0:
		return ()
	fib = itertools.dropwhile(n.__lt__, _fibonacci_series_impl())
	if count is not None:
		fib = itertools.islice(fib, count)
	return fib


def is_secret_fibonacci(n):
	z = frozenset(_encode_impl(n))
	return len(z) in z


def int_bits(n):
	validate_int(n)
	while n:
		yield n & 1
		n >>= 1


def validate_int(n, name=None):
	if not isinstance(n, int):
		raise TypeError(
			'{0:s}Expected an int, got {1.__module__:s}.{1.__qualname__:s}'
				.format(_suffix_if_not_none(name), type(n)))
	if n < 0:
		raise ValueError(
			_suffix_if_not_none(name) + 'Integer must be non-negative')


def _suffix_if_not_none(s, suffix=': ', default=''):
	return default if s is None else s + suffix


def logical_and(a, b):
	return a and b


MODES = {
	'encode': lambda s:
		' + '.join(map(str, filter(None,
			encode(int(s), output_type=None, reverse=False))))
		or '0',
	'decode': decode,
}


def parse_args(args):
	ap = argparse.ArgumentParser()
	ap.add_argument('numbers', metavar='N', nargs='+')

	ap_mode = ap.add_mutually_exclusive_group(required=True)
	ap_mode.add_argument('-m', '--mode', choices=MODES)
	for m in MODES:
		ap_mode.add_argument('-' + m[0], '--' + m,
			action='store_const', dest='mode', const=m)

	args = ap.parse_args(args)
	args.mode = MODES[args.mode]

	return args


def main(args=None):
	args = parse_args(args)
	for i in args.numbers:
		print(i, '->', args.mode(i))


if __name__ == '__main__':
	main()
