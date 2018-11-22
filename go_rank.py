#!/usr/bin/python3
__all__ = ('to_key',)
import sys


def to_key(rank):
	letter_index = 'kdp'.index(rank[-1].lower())
	number = int(rank[:-1])
	return (letter_index, number if letter_index else -number)


def k(x):r=' dp'.find(x[-1]);return r,int(x[:-1])*r
f=lambda x:max(x,key=k)


def main(args):
	fail_count = 0

	if not args:
		args = filter(None, sys.stdin)

	for i, item in enumerate(map(str.split, args), 1):
		if len(item) == 3:
			a, b, expected = item
		else:
			a, b = item
			expected = None

		actual = max(a, b, key=to_key)
		#actual = f((a, b))

		if expected is None:
			expected = ()
		else:
			expected = (actual == expected,)
			fail_count += not expected[0]

		print(
			'{:4d}: max{{{:>3s}, {:>3s}}} = {:>3s}'.format(i, a, b, actual),
			*expected)

	return int(bool(fail_count))


if __name__ == '__main__':
	sys.exit(main(sys.argv[1:]))
