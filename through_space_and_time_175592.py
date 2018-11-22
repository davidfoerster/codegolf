#!/usr/bin/python3
# https://codegolf.stackexchange.com/q/175592
__all__ = ('through_space_and_time',)

import re
import sys
import itertools
import numpy as np
import time as mod_time


def through_space_and_time(space, time, current_year=None):
	if len(time):
		if current_year is None:
			current_year = mod_time.localtime().tm_year
		time = 0b111 == np.bitwise_or.reduce(
			1 << (1 + np.sign(np.asanyarray(time, int) - current_year)))
	else:
		time = False

	if len(space):
		space = np.asanyarray(space)
		space = np.all(np.any(space[0] != space[1:], 0))
	else:
		space = True

	return (space, time)


def parse_point(s, dtype=int,
	pattern=re.compile(r'\s*[+-]?\d+\s*(?:,\s*[+-]?\d+\s*)*', re.ASCII)
):
	if not pattern.fullmatch(s):
		raise ValueError('Invalid point: {!r}'.format(s))
	return np.fromstring(s, dtype, -1, ',')


def _is_space_string(s):
	return ',' in s


def _bits2int(bits):
	bits = np.asanyarray(bits, bool)
	return np.bitwise_or.reduce(bits << np.arange(len(bits)))


def main(args=None):
	if args is None:
		args = sys.argv[1:]

	if args:
		args = (args,)
	else:
		args = map(str.split, sys.stdin or ())

	for i, a in enumerate(args):
		if i:
			print()

		it = iter(a)
		try:
			p = a.index('--')
		except ValueError:
			p = None
			space = itertools.takewhile(_is_space_string, it)
			time = it
		else:
			space = itertools.islice(it, p)
			time = itertools.islice(it, 1, None)

		space = np.vstack(tuple(map(parse_point, space)))
		time = np.array(tuple(time), int)
		travelled = (
			('neither', 'space', 'time', 'both')[
				_bits2int(through_space_and_time(space, time))])

		print(
			'{0:d}- Space: {1!s}\n{0:d}- Time: {2!s}\n{0:d}- Travelled: {3:s}'
				.format(i + 1, space, time, travelled))


if __name__ == '__main__':
	main()
