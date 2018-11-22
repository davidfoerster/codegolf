#!/usr/bin/python3
# -*- coding: utf-8
"""
Convert between decimal and roman numerals
"""
__all__ = ('to_int', 'to_roman', 'NUMERAL_LIST', 'UNUMERAL_LIST', 'NUMERAL_MAP')

import operator
import itertools
import collections.abc


NUMERAL_LIST = (
	('M', 1000),
	('D', 500),
	('C', 100),
	('L', 50),
	('X', 10),
	('V', 5),
	('I', 1),
)

UNUMERAL_LIST = (
	('Ⅿ', 1000),
	('Ⅾ', 500),
	('Ⅽ', 100),
	('Ⅼ', 50),
	('Ⅹ', 10),
	('Ⅴ', 5),
	('Ⅰ', 1),
)

NUMERAL_MAP = dict(itertools.chain(NUMERAL_LIST, UNUMERAL_LIST))


def to_int(roman, modern=True, numeral_map=NUMERAL_MAP):
	assert numeral_map and isinstance(numeral_map, collections.abc.Mapping)
	try:
		return (to_int_modern if modern else to_int_classic)(roman, numeral_map)
	except (StopIteration, KeyError):
		raise ValueError('Invalid roman numeral ' + repr(roman))


def to_int_classic(roman, numeral_map):
	return sum(map(numeral_map.__getitem__, roman))


def to_int_modern(roman, numeral_map):
	roman_iter = (
		(v, iter_length(run))
		for v, run in itertools.groupby(map(numeral_map.__getitem__, roman)))

	total = 0
	prev_digit_value, prev_count = next(roman_iter)
	for digit_value, count in roman_iter:
		total += prev_digit_value * prev_count * cmp(prev_digit_value, digit_value)
		prev_digit_value = digit_value
		prev_count = count

	return total + prev_digit_value * prev_count


def to_roman(n, modern=True, numeral_list=NUMERAL_LIST):
	if __debug__:
		nl_copy = list(numeral_list)
		assert (nl_copy and
			nl_copy == sorted(nl_copy, key=operator.itemgetter(1), reverse=True))
		if not isinstance(numeral_list, collections.abc.Sized):
			numeral_list = iter(nl_copy)
		del nl_copy

	if not isinstance(n, int):
		try:
			n_is_int = n.is_integer()
		except AttributeError:
			raise TypeError(
				'The supplied number must be an integer, not '
					'{0.__module__:s}.{0.__qualname__:s}'.format(type(n)))
		if not n_is_int:
			raise ValueError(
				'The supplied number must be an integer, not {!r}'.format(n))
		n = int(n)

	if n <= 0:
		raise ValueError(
			'The supplied number must be a positive integer, not {:d}'.format(n))

	return ''.join(to_roman_impl(n, modern, numeral_list))


def to_roman_impl(n, modern, numeral_list):
	assert not modern or isinstance(numeral_list, collections.abc.Sequence)

	for i, rdigit in enumerate(numeral_list):
		rdigit, value = rdigit
		k, n = divmod(n, value)
		#print(k, '*', value, '+', n, '=', k * value + n)
		if k:
			yield rdigit * k
		if not n:
			break
		if modern:
			j = (i + 2) & ~1
			if j < len(numeral_list):
				rdigit_sub, value_sub = numeral_list[j]
				value_diff = value - value_sub
				#assert rdigit in {'I':'VX', 'X':'LC', 'C':'DM'}[rdigit_sub]
				if n >= value_diff:
					yield rdigit_sub
					yield rdigit
					n -= value_diff
					#print(value, '-', value_sub, '+', n, '=', n + value_diff)


def iter_length(iterator):
	return sum(1 for _ in iterator)


def cmp(a, b):
	return (a > b) - (a < b)


def _parse_args(args):
	import argparse
	ap = argparse.ArgumentParser(description=__doc__)
	ap.add_argument('numerals', nargs='+',
		help='Decimal or roman numerals to convert')

	from collections import OrderedDict
	mode_map = OrderedDict((
		('to-decimal', to_int),
		('to-roman',
			lambda s, modern, numeral_list: to_roman(int(s), modern, numeral_list)),
		(None, to_auto),
	))
	mode_map_keys = tuple(filter(None, mode_map))
	mode_group = ap.add_mutually_exclusive_group()
	mode_group.add_argument('-M', '--mode', dest='mode', choices=mode_map_keys,
		help='Sets the conversion direction. If none, try to detect it based on '
			'the input.')
	for m in mode_map_keys:
		mode_group.add_argument('-' + m[3], '--' + m, dest='mode',
			action='store_const', const=m, help="Equivalent to '-M {:s}'.".format(m))

	style_choices = ('modern', 'classic')
	style_group = ap.add_mutually_exclusive_group()
	style_group.add_argument('-S', '--style', dest='style',
		choices=style_choices, default=style_choices[0],
		help='Use classic additive-only style or modern subtractive style for '
			'roman numerals during the conversion. (default: modern)')
	for m in style_choices:
		style_group.add_argument('-' + m[0], '--' + m, dest='style',
		action='store_const', const=m, help="Equivalent to '-S {:s}'.".format(m))

	ap.add_argument('-u', '--unicode', dest='numeral_list',
		action='store_const', const=UNUMERAL_LIST, default=NUMERAL_LIST,
		help='Use roman numeral characters from the unicode range '
			'U+{:04X}–U+{:04X} during the conversion to roman. (default: use latin '
			'letter characters)'
			.format(ord(UNUMERAL_LIST[-1][0]), ord(UNUMERAL_LIST[0][0])))

	args = ap.parse_args(args)
	args.mode = mode_map[args.mode]
	return args


def to_auto(s, modern=True, numeral_list=NUMERAL_LIST):
	try:
		s = int(s)
	except ValueError:
		return to_int(s, modern)
	else:
		return to_roman(s, modern, numeral_list)


def main(*args):
	import sys, inspect
	args = _parse_args(args or None)
	modern = args.style == 'modern'
	to_func = args.mode
	if 'numeral_list' in inspect.signature(to_func).parameters:
		import functools
		to_func = functools.partial(to_func, numeral_list=args.numeral_list)

	for s in args.numerals:
		try:
			r = to_func(s, modern)
		except ValueError as ex:
			print(sys.argv[0], ex.args[0], sep=': ', file=sys.stderr)
		else:
			print(s, '=>', r)


if __name__ == '__main__':
	main()
