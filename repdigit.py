#!/usr/bin/python3
# https://codegolf.stackexchange.com/q/125133
import operator
import itertools


def is_repdigit(n, base=10):
	return all(map_pairs(operator.eq, digits(n, base)))


is_repdigit_golfed1 = lambda n:len(set(str(n)))<2


def digits(n, base=10):
	if not isinstance(n, int):
		raise TypeError
	if n < 0:
		raise ValueError

	while n >= base:
		n, d = divmod(n, base)
		yield d
	yield n


def map_pairs(func, iterable, n=2):
	return map(func, *_pairs_helper(iterable, n))

def _pairs_helper(iterable, n=2):
	return map(itertools.islice,
		itertools.tee(iterable, n), itertools.count(), itertools.repeat(None))
