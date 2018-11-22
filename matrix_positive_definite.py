#!/usr/bin/python3
# https://codegolf.stackexchange.com/q/172677
__all__ = ('Matrix',)

import math
import operator
import itertools
import collections.abc
from array import array
from itertools import islice, zip_longest
from functools import reduce, partial as fpartial


class Matrix:

	__slots__ = ('data', 'width', 'height')

	default_typecode = 'd'

	_takeover = object()


	def __init__(self, data=None, width=None, height=None, typecode=None):
		remainder = min(width or 0, height or 0)
		if remainder < 0:
			raise ValueError('Negative matrix dimension(s): {:d}'.format(remainder))
		if typecode is None:
			typecode = getattr(data, 'typecode', self.default_typecode)

		remainder = 0
		if data is None:
			if width is None or height is None:
				raise ValueError(
					'If data is unset you must set both width and height.')
			data = array(typecode, itertools.repeat(0, width * height))

		elif (data and isinstance(data, collections.abc.Sequence) and
			all(map(isinstance, data, itertools.repeat(collections.abc.Sequence)))
		):
			height = self._get_dimemsion(height, len(data), 'height')
			width = self._get_dimemsion(width, len(data[0]), 'width')
			if any(map(width.__ne__, map(len, data))):
				raise ValueError('Size mismatch of nested sequences')
			data = array(typecode, itertools.chain.from_iterable(data))

		else:
			if typecode is self._takeover:
				assert isinstance(data, array)
				typecode = data.typecode
			else:
				data = array(typecode, data)

			if width is None and height is None:
				width = len(data)
				height = 1
			elif width is None:
				width, remainder = divmod(len(data), height)
			elif height is None:
				height, remainder = divmod(len(data), width)
			elif width * height != len(data):
				raise ValueError(
					'Data length ({:d}) must match the product of width ({:d}) and '
					'height ({:d}) if all are given.'
					.format(len(data), width, height))

		if remainder:
			assert (width is None) != (height is None)
			raise ValueError(
				'Data length ({:d}) must be divisible by width or height ({:d}) if '
				'either but not both are given.'
				.format(len(data), height if width is None else width))

		if min(width, height) <= 0:
			raise ValueError('Zero-sized matrix')

		self.data = data
		self.width = width
		self.height = height


	@staticmethod
	def _get_dimemsion(given, expected, name):
		if given is not None and given != expected:
			raise ValueError(
				'Mismatch of given ({:d}) and data set ({:d}) {:s}s'
				.format(given, expected, name))
		return expected


	def __eq__(self, other):
		if not isinstance(other, Matrix):
			return NotImplemented
		return (
			self.width == other.width and self.height == other.height and
			self.data == other.data)


	def __getitem__(self, idx):
		w = self.width
		h = self.height

		if idx is Ellipsis or isinstance(idx, (int, slice)):
			if h == 1:
				x = idx
				y = 0
			elif w == 1:
				x = 0
				y = idx
			else:
				raise TypeError(
					'Array index must be a tuple if both matrix dimensions are greater '
					'than 1.')
		else:
			x, y = idx

		if isinstance(x, int) and isinstance(y, int):
			return self.data[y * w + x]

		# Normalize and verify indices
		x = normalize_slice(x, w, 1, range)
		y = normalize_slice(y, h, w, range)

		if not x or not y:
			return ()

		if len(x) == w:
			result = self.data[y.start : y.stop]

		else:
			primary, secondary = sorted([x, y], key=len)
			if len(primary) == 1:
				result = self.data[slice_add(secondary, primary.start)]
			else:
				result = reduce(iadd_if_not_none,
					map(self.data.__getitem__,
						slice_join(map(fpartial(slice_add, secondary), primary))),
					None)

		return type(self)(result, len(x), len(y), self._takeover)


	def transpose(self):
		w = self.width
		h = self.height
		primary = slice((h - 1) * w, -1, -w)
		secondary = slice(w - 1, -1, -1)
		if w < h:
			secondary, primary = primary, secondary

		return type(self)(
			reduce(iadd_if_not_none,
				map(self.data.__getitem__,
					map(fpartial(slice_add, secondary),
						range(primary.start, primary.stop, primary.step))),
				None),
			h, w, self._takeover)

	__invert__ = transpose


	def multiply(self, other, typecode=None):
		if not isinstance(other, Matrix):
			raise TypeError(
				'The right operand must be of type Matrix, not '
				'{0.__module__:s}.{0.__qualname__:s}.'.format(type(other)))
		return self._multiply_impl(other, typecode)


	def __mul__(self, other):
		if not isinstance(other, Matrix):
			return NotImplemented
		return self._multiply_impl(other, None)


	def _multiply_impl(self, other, typecode):
		assert isinstance(other, Matrix)

		m = self.width
		if m != other.height:
			raise ValueError(
				'Left operand width and right operand height do not match: '
				'{:d} != {:d}'.format(self.width, other.height))
		if typecode is None:
			typecode = self.typecode
		if self.data.typecode in 'df' or other.data.typecode in 'df':
			_sum = math.fsum
		else:
			_sum = sum

		m = range(m)
		w = other.width
		h = self.height
		left_getitem = self.data.__getitem__
		right_getitem = other.data.__getitem__
		return type(self)(
			(_sum(map(operator.mul,
				map(left_getitem, zip(i, m)), map(right_getitem, zip(m, k))))
				for k, i in itertools.product(
					map(itertools.repeat, range(w)), map(itertools.repeat, range(h)))),
			w, h, typecode)


	def _check_index(self, x, y, *, names=('x', 'y')):
		return (
			check_index(0, x, self.width, names=(None, names[0], 'width')) and
			check_index(0, y, self.height, names=(None, names[1], 'height')))


def normalize_slice(s, length, step=1, slice=slice):
	assert length >= 0 and step > 0

	if s is Ellipsis:
		start = 0
		stop = length

	elif isinstance(s, int):
		if s < 0:
			s += length
		start = s
		stop = s + 1

	elif s.step in (None, 1):
		start = s.start
		if start is None:
			start = 0
		elif start < 0:
			start += length

		stop = s.stop
		if stop is None:
			stop = length
		elif stop < 0:
			stop += length

	else:
		raise ValueError(
			'Step length must be 1 or unspecified/None, not {!r}'.format(step))

	check_index(0, start, stop, length, names=(None, 'start', 'stop', 'length'))
	return slice(start * step, stop * step, step)


def check_index(*idxs, names=(), exception_type=IndexError, fmt='d'):
	if idxs[-2] >= idxs[-1] or any(map(operator.gt,
		islice(idxs, 0, len(idxs) - 2), islice(idxs, 1, len(idxs) - 1))
	):
		names = [
			'{:s} ({:{}})'.format(n, i, fmt) if n else format(i, fmt)
			for i, n in zip_longest(idxs, islice(names, len(idxs)))
		]
		raise exception_type(
			'{1:s} < {0:s} violated'.format(names.pop(), ' <= '.join(names)))
	return True


def slice_add(sl, n, slice=slice):
	return slice(sl.start + n, sl.stop + n, sl.step)


def slice_join(iterable, slice=slice):
	iterable = iter(iterable)
	a = next(iterable)
	stop = a.stop

	for b in iterable:
		assert a.step == b.step and check_index(
			a.start, stop, b.start, b.stop, exception_type=AssertionError,
			names=map('.'.join, itertools.product(('a', 'b'), ('start', 'stop'))))

		if stop < b.start:
			yield a if stop == a.stop else slice(a.start, stop, a.step)
			a = b
		stop = b.stop

	yield a


def iadd_if_not_none(acc, item):
	if acc is None:
		return item

	acc += item
	return acc
