#!/usr/bin/python3
# https://codegolf.stackexchange.com/q/175090
import sys
import argparse
import itertools

try:
	from math import gcd
except ImportError:
	from fractions import gcd


def lcm(m, n, _gcd=None):
	if _gcd is None:
		_gcd = gcd(m, n)
	return abs(m * n) // _gcd


def gcd_sort(l, max_rounds=None):
	ll = len(l)
	if max_rounds is None:
		max_rounds = ll * ll

	rounds = 0
	last_rounds = None

	while rounds != last_rounds:
		last_rounds = rounds
		for j in range(ll - 1):
			for k in range(j + 1, ll):
				a = l[j]
				b = l[k]
				if b % a:
					_gcd = gcd(a, b)
					l[j] = _gcd
					l[k] = a * b // _gcd  # least common multiple

					rounds += 1
					if rounds >= max_rounds:
						return rounds

	return rounds


def parse_list(s):
	return list(map(int, s.strip(' \t\r\n\v[]').split(',')))


def parse_positional_arg(s):
	s, sep, expected = s.partition('=>')
	return (parse_list(s), parse_list(expected) if sep else None)


def parse_args(args):
	ap = argparse.ArgumentParser()
	ap.add_argument('--show-steps', action='store_true')
	ap.add_argument('lists', nargs='*', type=parse_positional_arg)

	args = ap.parse_args(args)
	if not args.lists:
		args.lists = map(parse_positional_arg, sys.stdin)

	return args


def main(args=None):
	args = parse_args(args)
	for i, s in enumerate(args.lists, 1):
		s, expected = s
		r = s.copy()
		if not args.show_steps:
			gcd_sort(r)
		else:
			print(i, r, sep=': ')
			for j in itertools.count():
				k = gcd_sort(r, 1)
				if k or not j:
					print('=> {!s} ({:d})'.format(r, j + k))
				if not k:
					break

		expected = (
			() if expected is None or r == expected
			else ('(expected: {})'.format(expected),))

		if not args.show_steps:
			print('{:d}: {!s} => {!s}'.format(i, s, r), *expected)
		elif expected:
			print(*expected, end='\n\n')
		else:
			print()


if __name__ == '__main__':
	main()
