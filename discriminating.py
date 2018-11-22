#!/usr/bin/python3
# https://codegolf.stackexchange.com/q/156967
import collections


def is_discriminating(iterable):
	c = iter(collections.Counter(iterable).values())
	n = next(c, 2)
	return n >= 2 and all(map(n.__eq__, c))


def main(*args):
	for word in args:
		print(repr(word), '=>', is_discriminating(word))


if __name__ == '__main__':
	import sys
	main(*sys.argv[1:])
