#!/usr/bin/python3
# See https://codegolf.stackexchange.com/q/156943
from itertools import chain
from functools import partial as fpartial


def get_rows(n):
	return (range(i * n + 1, (i + 1) * n + 1)
		for i in chain(range(0, n, 2), range((n - 2) | 1, 0, -2)))


def _rformat(format_spec, value):
	return format(value, format_spec)


def main(*numbers):
	for i, n in enumerate(numbers):
		max_digits = len(str(n * n))
		if i:
			print()
		for r in map(
			fpartial(map, fpartial(_rformat, str(max_digits) + 'd')),
			get_rows(n)
		):
			print(*r)


if __name__ == '__main__':
	import sys
	main(*map(int, sys.argv[1:]))
