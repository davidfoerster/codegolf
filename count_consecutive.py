#!/usr/bin/python3
from __future__ import print_function, division, absolute_import, unicode_literals
import collections

try:
	from functools import reduce
except ImportError:
	pass


_cc_accumulator = collections.namedtuple(
	'_cc_accumulator', ('current', 'longest', 'last_c'))
_cc_accumulator._initial = _cc_accumulator(0, 0, -2)


def _cc_reductor(acc, c):
	return _cc_accumulator(
		acc.current + 1 if acc.last_c + 1 == c else 1,
		max(acc.current, acc.longest), c)


def count_consecutive(s):
	r = reduce(_cc_reductor, sorted(set(map(ord, s))), _cc_accumulator._initial)
	return max(r.current, r.longest)


count_consecutive_golfed1 = \
lambda s:max(reduce(lambda a,c:(a[2]+1!=c or a[0]+1,max(a[:2]),c),sorted(set(map(ord,s))),[0]*3)[:2])

def main(args):
	try:
		digits = len(args)
	except TypeError:
		digits = 0
	else:
		digits = len(str(digits))

	for i, s in enumerate(args, 1):
		print('{:{}d}: {!r} => {:d}'.format(
			i, digits, s, count_consecutive(s)))


if __name__ == '__main__':
	import sys
	main(sys.argv[1:])
