#!/usr/bin/python3
# https://codegolf.stackexchange.com/q/175485
import sys
import itertools


def codegolf_175485(a, b):
	diff_sign = (a < b) - (a > b)
	return itertools.chain((a, b), range(a + diff_sign, b, diff_sign | 1))


def parse_pair(s, type=int):
	a, sep, b = s.partition(',')
	if sep:
		try:
			return (type(a), type(b))
		except ValueError as ex:
			cause = ex
	else:
		cause = None
	raise \
		ValueError('Invalid {:s} pair: {!r}'.format(type.__qualname__, s)) \
		from cause


def main(args=None):
	if args is None:
		args = sys.argv[1:]
	if not args:
		args = sys.stdin or ()

	for a, b in map(parse_pair, args):
		print('{:4d},{:4d} -> [{:s}]'.format(a, b,
			', '.join(map(str, codegolf_175485(a, b)))))


if __name__ == '__main__':
	main()
