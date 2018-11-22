#!/usr/bin/python3
# https://codegolf.stackexchange.com/q/54105
__all__ = ('encode', 'decode')
import re
import sys
import string
import argparse
import itertools
import functools
import collections
import collections.abc


class DigitMappings(collections.defaultdict):

	def __init__(self):
		super().__init__()

	def __missing__(self, key):
		if not (key and isinstance(key, str)):
			raise KeyError
		value = dict(zip(key, itertools.count(1)))
		self[key] = value
		return value


digit_mappings = DigitMappings()


def decode(s, digits=digit_mappings[string.ascii_uppercase]):
	base = len(digits)
	if base <= 1:
		raise ValueError

	if __debug__:
		if isinstance(digits, collections.abc.Mapping):
			values = digits.values()
		else:
			values = digits
		assert sorted(values) == list(range(1, base + 1))

	return functools.reduce(
		functools.partial(muladd, base), map(digits.__getitem__, s))


def muladd(a, b, c):
	return a * b + c


def encode(n, digits=string.ascii_uppercase):
	return (
		(''.join if isinstance(digits, str) else tuple)(
			_encode_impl(n, digits))[::-1])


def _encode_impl(n, digits):
	base = len(digits)

	if not isinstance(n, int):
		raise TypeError
	if n <= 0 or base <= 1:
		raise ValueError

	while n > 0:
		n, d = divmod(n, base)
		yield digits[d - 1]
		n -= not d
	assert n == 0


def identity(x):
	return x


def parse_args(args):
	ap = argparse.ArgumentParser()
	ap.add_argument('numbers', nargs='+')

	for m in ('encode', 'decode'):
		ap.add_argument('-' + m[0], '--' + m, metavar='DIGITS',
			nargs='?', type=parse_digits, const=string.ascii_uppercase)

	args = ap.parse_args(args)
	if args.encode is None and args.decode is None:
		args.encode = string.ascii_uppercase

	if args.encode is not None:
		args.numbers = tuple(map(int, args.numbers))
		args.encode = functools.partial(encode, digits=args.encode)
	else:
		args.encode = identity

	if args.decode is not None:
		args.decode = functools.partial(decode, digits=digit_mappings[args.decode])
	else:
		args.decode = identity

	return args


digit_sets = {
	'upper': string.ascii_uppercase,
	'lower': string.ascii_lowercase,
	'digits': string.digits,
	'base64': ''.join((
		string.ascii_uppercase, string.ascii_lowercase, string.digits, '+/'))
}


def parse_digits(s):
	s = re.sub(r'\[:([\w-]*):\]', lambda m: digit_sets[m.group(1)], s)
	if not 1 < len(s) == len(frozenset(s)):
		raise ValueError
	return s



def main(args=None):
	args = parse_args(args)
	for s in args.numbers:
		print(s, '->', args.encode(args.decode(s)))


if __name__ == '__main__':
	main()
