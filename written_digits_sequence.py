#!/usr/bin/python3
# https://codegolf.stackexchange.com/q/174521
import sys
import itertools


def sequence(n=None, digit_lengths=(4, 3, 3, 5, 4, 4, 3, 5, 5, 4)):
	assert digit_lengths and all(
		isinstance(x, int) and x > 0
		for x in map(digit_lengths.__getitem__, range(10)))

	seq = _sequence_impl(digit_lengths.__getitem__)

	if n is not None:
		if isinstance(n, slice):
			seq = itertools.islice(seq,
				default_if_none(n.start, 0), n.stop, default_if_none(n.step, 1))
		else:
			return next(itertools.islice(seq, n, None))

	return seq


def _sequence_impl(digit_lengths):
	a = 0
	while True:
		yield a
		a += sum(map(digit_lengths, digits(a)))


def digits(n, base=10):
	assert isinstance(n, int) and n >= 0
	assert isinstance(base, int) and base >= 2
	while n >= base:
		n, d = divmod(n, base)
		yield d
	yield n


def default_if_none(x, default):
	return x if x is not None else default


def main(args=None):
	if args is None:
		args = sys.argv[1:]

	for a in sequence(slice(int(args[0]))):
		print(a)


if __name__ == '__main__':
	main()
