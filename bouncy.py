#!/usr/bin/python3
# https://codegolf.stackexchange.com/q/168097
__all__ = ('MIN_BOUNCY', 'is_bouncy', 'sum_bouncy')

import sys
import operator
import itertools


MIN_BOUNCY = 101


def cmp(a, b):
	return (a > b) - (a < b)


def digits(n, base=10):
	assert isinstance(n, int) and n >= 0
	assert isinstance(base, int) and base >= 2

	while n >= base:
		n, d = divmod(n, base)
		yield d
	yield n


def pairs(iterable, n=2):
	return zip(*_pairs_helper(iterable, n))


def map_pairs(func, iterable, n=2):
	return map(func, *_pairs_helper(iterable, n))


def _pairs_helper(iterable, n):
	return map(itertools.islice,
		itertools.tee(iterable, n), itertools.count(), itertools.repeat(None))


def is_monotonuous(iterable, direction, strict=False):
	if direction:
		predicate = getattr(operator,
			('g','l')[direction>0] + ('t','e')[not strict])
	else:
		predicate = cmp

	iterable = map_pairs(predicate, iterable)

	if not direction:
		if not strict:
			iterable = filter(None, iterable)

		first = next(iterable, None)
		if not first:
			return first is None

		iterable = map(first.__eq__, iterable)

	return all(iterable)


def is_bouncy(n):
	if not isinstance(n, int):
		try:
			if not n.is_integer():
				return False
		except AttributeError:
			raise TypeError
		n = int(n)

	n = abs(n)
	return n >= MIN_BOUNCY and _is_bouncy_unchecked(n)


def _is_bouncy_unchecked(n):
	assert isinstance(n, int) and n >= MIN_BOUNCY
	return is_monotonuous(digits(n), 0)


def sum_bouncy(count):
	return sum(itertools.islice(
		filter(_is_bouncy_unchecked, itertools.count(MIN_BOUNCY)), count))


def main(args=None):
	if args is None:
		args = sys.argv[1:]
	if not args:
		args = sys.stdin or ()

	for n in map(int, args):
		print(n, '=>', sum_bouncy(n))


if __name__ == '__main__':
	main()
