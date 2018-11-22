#!/usr/bin/python3 -O
# https://codegolf.stackexchange.com/questions/8369
# https://en.wikipedia.org/wiki/Kolakoski_sequence
from operator import itemgetter
from itertools import cycle, islice, starmap
from collections import deque
from collections.abc import Iterable


def kolakoski_reference(n, k=2):
	k, m, s = _kolakoski_get_params(k)
	s = list(s)
	i = len(s) - 1
	while len(s) < n:
		s += m[i % k] * s[i]
		i += 1
	del s[n:]
	return s


def kolakoski(n, k=2):
	s = islice(kolakoski_gen(k), n)
	if __debug__:
		s = list(s)
		assert s == kolakoski_reference(n, k)
	return s


def kolakoski_gen(k=2):
	k, m, s = _kolakoski_get_params(k)

	i = len(s) - 1
	xi = s[i]
	yield from s

	s = deque()
	for i in cycle([i].__iadd__(range(i))):
		s += m[i] * xi
		xi = s.popleft()
		yield xi


def _kolakoski_get_params(k):
	if k == 2:
		return 2, ((1,), (2,)), [1, 2, 2]
	elif isinstance(k, int):
		if k >= 2:
			m = tuple(map(as_tuple, range(1, k + 1)))
		else:
			raise ValueError("'k' must be >= 2, not {:d}".format(k))
	elif isinstance(k, Iterable):
		m = tuple(map(as_tuple, k))
		k = len(m)
		if k < 2:
			raise ValueError('Integer sequence length must be >= 2, not {:d}'.format(k))
		for i in map(itemgetter(0), m):
			if not isinstance(i, int):
				raise TypeError(
					'Sequence contains a non-integer type {0.__module__}.{0.__qualname__}'
						.format(type(i)))
			if i <= 0:
				raise ValueError('Sequence contains a non-positive integer {:d}'.format(i))
	else:
		raise TypeError(
			"'k' must be an integer or iterable, not {0.__module__}.{0.__qualname__}"
				.format(type(k)))

	return k, m, (m[0] * m[0][0]) + (m[1] * m[1][0])


def as_tuple(*items):
	return items


def parse_arg(s, default_k=2):
	n, s, k = s.partition(':')

	n = int(n)
	if ',' in k:
		k = tuple(map(int, k.split(',')))
	elif k:
		k = int(k)
	else:
		k = default_k

	return n, k


def main(*args):
	if not args:
		import sys
		args = sys.argv[1:]
		if not args:
			args = sys.stdin

	args = tuple(map(parse_arg, args))
	if len(args) == 1:
		print(*kolakoski(*args[0]))
	else:
		len_width = len(str(max(map(itemgetter(0), args))))
		for s in map(tuple, starmap(kolakoski, args)):
			print('{:{}d}:'.format(len(s), len_width), *s)


if __name__ == '__main__':
	main()
