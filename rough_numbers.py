#!/usr/bin/python3
# https://codegolf.stackexchange.com/q/175158
import itertools


def rough_numbers(b, k=None):
	assert isinstance(b, int) and b >= 1

	if b <= 2:
		r = itertools.count(1, b)
	else:
		r = itertools.chain((1,), filter(
			lambda n: all(map(n.__mod__, range(3, min(n, b + 1)))),
			itertools.count(b + b % 2 + 1, 2)))

	if k is not None:
		r = itertools.islice(r, k)

	return r
