#!/usr/bin/python3
# https://codegolf.stackexchange.com/q/175405
__all__ = ('smallest_integer_disk',)

import operator
import itertools
import numpy as np
from math import floor, ceil

import re
import sys
import argparse


def smallest_integer_disk(points, debug=None):
	if len(points) < 2:
		real_center, = points
	else:
		real_center = np.add(*max(
			itertools.combinations(points, 2),
			key=lambda p: np.sum(np.square(p[1] - p[0])))) / 2
	if debug is not None:
		print('Real center', real_center, sep=': ', file=debug)


	candidate_centers = map(np.array, itertools.product(
		*zip(map(floor, real_center), map(ceil, real_center))))
	if debug is not None:
		candidate_centers = np.vstack(tuple(candidate_centers))
		print('Candidate centers', candidate_centers, sep=': ', file=debug)

	return min(
		((c, ceil(np.max(np.linalg.norm(points - c, None, 2))))
			for c in candidate_centers),
		key=operator.itemgetter(1))


def parse_point(s, dtype=int,
	pattern=re.compile(r'\s*[+-]?\d+\s*(?:,\s*[+-]?\d+\s*)*', re.ASCII)
):
	if not pattern.fullmatch(s):
		raise ValueError('Invalid point: {!r}'.format(s))
	return np.fromstring(s, dtype, -1, ',')


def stack_points(points):
	try:
		return np.vstack(points)
	except ValueError:
		raise ValueError(
			'Inconsistent point vector lengths: {:s}'.format(
				', '.join(map(str, sorted(frozenset(map(len, points)))))))


def parse_args(args):
	ap = argparse.ArgumentParser()
	ap.add_argument('points', nargs='*', type=parse_point)
	ap.add_argument('--debug', action='store_const', const=sys.stderr)

	args = ap.parse_args(args)

	if args.points:
		args.points = (args.points,)
	elif sys.stdin:
		args.points = (tuple(map(parse_point, line.split())) for line in sys.stdin)

	return args


def main(args=None):
	args = parse_args(args)
	debug = args.debug

	for i, points in enumerate(map(stack_points, args.points)):
		if debug:
			print('{:s}{:d}- Points: {!s}'.format('\n'[:i], i, points), file=debug)

		print('{:d}- center: {!s}, radius: {:d}'.format(
			i, *smallest_integer_disk(points, debug)))


if __name__ == '__main__':
	main()
