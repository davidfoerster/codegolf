#!/usr/bin/python3
# https://codegolf.stackexchange.com/q/172295
import sys
import operator
from operator import itemgetter
from itertools import groupby
from collections import Counter


def longest_repeating_subsequence(iterable, all=False):
	# collect subsequence lengths
	counts = Counter(
		(item, sum(map(bool, group))) for item, group in groupby(iterable))
	counts = (
		(seq, (seq[1], count)) for seq, count in counts.items() if count >= 2)
	key_func = itemgetter(1)

	if all:
		return map(itemgetter(0), top_all(counts, operator.ge, key_func))
	return max(counts, key=key_func, default=(None,))[0]


def top_all(iterable, predicate, key=None):
	iterable = iter(iterable)
	top_items = []
	try:
		top_items.append(next(iterable))
	except StopIteration:
		pass
	else:
		if key is None: key = identity
		top_key = key(top_items[0])
		for x in iterable:
			k = key(x)
			if predicate(k, top_key):
				if k != top_key:
					top_key = k
					top_items.clear()
				top_items.append(x)

	return top_items


def identity(x):
	return x


#from collections import*
#from itertools import*
def longest_repeating_subsequence_golfed1(s):
	return max((e for e in Counter(''.join(g)for k,g in groupby(s)).items()if e[1]>1),key=lambda e:(len(e[0]),e[1]))[0]


def main(args=None):
	if args is None:
		args = sys.argv[1:] or map(str.strip, sys.stdin)

	for n in map(int, args):
		expected = frozenset(
			str(digit) * length for digit, length in
				longest_repeating_subsequence(map(int, str(n)), True))
		print('{:d} => [{:s}]'.format(n, ', '.join(sorted(expected))))

		golfed = longest_repeating_subsequence_golfed1(str(n))
		success = golfed in expected
		print(n, '=>', golfed, end=(', FAILED!\n', '\n\n')[success])

		if not success:
			return 1

	return 0


if __name__ == '__main__':
	sys.exit(main())
