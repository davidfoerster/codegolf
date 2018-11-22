#!/usr/bin/python3 -O
"""
Split a number as fairly or as evily as possible.

See https://codegolf.stackexchange.com/q/150954 and
https://codegolf.stackexchange.com/q/151621.
"""
__all__ = ('fair_split', 'evil_split', 'main')
import itertools, collections, collections.abc
from functools import partial as fpartial


def fair_split(n):
	if isinstance(n, int):
		n = abs(n)
		ns = str(n)
	else:
		raise TypeError(
			'Expected int or str, got {0.__module__}.{0.__qualname__}'
				.format(type(n)))

	optim_k = n
	optim_v = []
	for i in range(1, len(ns)):
		a = int(ns[:i])
		b = int(ns[i:])
		diff = abs(a - b)
		if diff <= optim_k:
			if diff != optim_k:
				optim_k = diff
				optim_v.clear()
			optim_v.append((a, b))

	return (optim_k, optim_v)


def fair_split_golfed(n):
	return min(((int(n[:i]),int(n[i:]))for i in range(1,len(n))),key=lambda p:abs(p[0]-p[1]))


def fair_split_result2str(split):
	diff, split = split
	if split:
		return '{:s} = {:d}'.format(
			' = '.join(itertools.starmap('|{:d} - {:d}|'.format, split)),
			diff)
	else:
		return str(diff)


def divisors(n, start=1, end=None, include_self=True):
	if end is None:
		end = n // 2 + 1

	r = range(start, end)
	rv = itertools.filterfalse(n.__mod__, r)
	if include_self and n not in r:
		rv = (rv, (n,))
		if n < start: rv = rv[::-1]
		rv = itertools.chain(*rv)
	return rv


def combinations(seq, n):
	if len(seq) == 1 and n > 1:
		if not hasattr(seq, '__mul__'):
			seq = tuple(seq)
		return (seq * n,)
	else:
		return itertools.combinations(seq, n)


def slice_sequence(ints, step=None):
	ints = iter(ints)
	try:
		acc = slice(next(ints))
	except StopIteration:
		return
	for item in ints:
		acc = slice(acc.stop, item, step)
		yield acc



def evil_split(n):
	if isinstance(n, int):
		ns = str(abs(n))
	else:
		raise TypeError(
			'Expected int or str, got {0.__module__}.{0.__qualname__}'
				.format(type(n)))

	l = len(ns)
	optim_k = 0
	optim_v = collections.defaultdict(set)
	for part_count in divisors(l):
		for ab in combinations(
			frozenset(map(int, map(ns.__getitem__,
				slice_sequence(range(0, l + 1, l // part_count))))),
			2
		):
			diff = abs(int.__sub__(*ab))
			if diff >= optim_k:
				if diff != optim_k:
					optim_k = diff
					optim_v.clear()
				optim_v[part_count].add(ab)

	return (optim_k, optim_v)


def evil_split_result2str(split):
	diff, split = split
	return '{:s};  {:s} = {:d}'.format(
		' or '.join(map(str, sorted(split.keys()))),
		' = '.join(itertools.starmap('|{:d} - {:d}|'.format,
			itertools.chain.from_iterable(split.values()))),
		diff)


def rapply(func, arg1, arg0):
	return func(arg0, arg1)


def hashable_func(func):
	return lambda *args, **kwargs: func(*args, **kwargs)


class NamedMethod(collections.UserString):
	def __init__(self, func, name=None):
		super().__init__(name or func.__name__)
		self.__call__ = func


class PrefixDict(collections.UserDict):
	def get_prefix_collisions(self):
		return filter(lambda p: p[0].startswith(p[1]),
				map(fpartial(sorted, key=len, reverse=True),
					itertools.combinations(self.keys(), 2)))

	def verify_keys(self):
		if any(self.get_prefix_collisions()):
			raise KeyError(
			'The following key pairs are not prefix-free: ' +
			', '.join(itertools.starmap('{!r} and {!r}'.format,
				self.get_prefix_collisions())))

	def get_candidates(self, key):
		return filter(fpartial(rapply, type(key).startswith, key), self.keys())

	def get_prefix(self, key):
		if key not in self:
			key_candidates = tuple(self.get_candidates(key))
			if len(key_candidates) == 1:
				key = key_candidates[0]
			elif key_candidates:
				raise KeyError(
					'Ambigous key prefix {!r} with possible meanings: {}'
						.format(key, ', '.join(map(repr, result))))
			else:
				raise KeyError('No such key prefix: ' + repr(key))

		return self[key]


def main(args):
	import argparse
	ap = argparse.ArgumentParser(
		formatter_class=argparse.ArgumentDefaultsHelpFormatter,
		**dict(zip(('description', 'epilog'),
			map(str.strip, __doc__.rsplit('\n\n', 1)))))
	ap.add_argument('numbers', metavar='N', nargs='+', type=int)

	modes = PrefixDict(
		(m, NamedMethod(globals()[m + '_split'], m))
			for m in ('fair', 'evil'))
	if __debug__: modes.verify_keys()
	ap.add_argument('-m', '--mode',
		choices=modes.values(), default=modes['fair'],
		type=hashable_func(modes.get_prefix),
		help='Choose to split fairly or evily.')

	args = ap.parse_args(args)
	args.mode = fair_split if args.mode.startswith('f') else evil_split
	result2str = globals()[ args.mode.__name__ + '_result2str' ]

	if len(args.numbers) == 1 and args.numbers[0] < 0:
		if args.mode is fair_split:
			args.numbers = (
				10, 11, 12, 13, 101, 128, 313, 1003, 7129, 81128, 999999, 9999999)
		elif args.mode is evil_split:
			args.numbers = (
				1, 10, 11, 12, 42, 101, 2222, 6567, 123000, 123001, 121131, 294884,
				192884729, 123456189012, 123457117346)

	for n in args.numbers:
		print(n, '=>', result2str(args.mode(n)))


if __name__ == '__main__':
	import sys
	main(sys.argv[1:])
