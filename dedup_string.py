#!/usr/bin/python3 -O
import re, itertools
from collections.abc import Mapping
from functools import partial as fpartial


def dedup(iterable, filter_items, max_occurrences=1):
	if not isinstance(filter_items, Mapping):
		filter_items = zip(filter_items, itertools.repeat(max_occurrences))
	filter_items = dict(filter_items)

	for obj in iterable:
		filter_count = filter_items.get(obj)
		if filter_count is None:
			yield obj
		elif filter_count > 0:
			filter_items[obj] = filter_count - 1
			yield obj


def main(input, filter_items):
	for words in map(main.word_pattern.findall, input):
		print(*dedup(words, filter_items))

main.word_pattern = re.compile(r'[^\W\d_]+', re.UNICODE)


if __name__ == '__main__':
	import sys
	main(sys.stdin, sys.argv[1:])
