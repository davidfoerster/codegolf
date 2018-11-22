#!/usr/bin/python3 -O
"""
Fix holes in characters sequences with tape.

Sources:
  https://codegolf.stackexchange.com/q/157240,
  https://codegolf.stackexchange.com/q/157600,
  https://codegolf.stackexchange.com/q/157612,
  https://codegolf.stackexchange.com/q/157770.
"""

import builtins, collections.abc
from itertools import *
from functools import reduce
from functools import partial as fpartial
from operator import itemgetter


def fix_with_tape(s, tape=('T','A','P','E')):
	"""Fix holes in characters sequences with tape"""
	s, t = tee(s)
	for c, n in zip(s, chain(islice(t, 1, None), '\0')):
		yield c
		yield from islice(cycle(tape), max(ord(n) - ord(c) - 1, 0))


def fix_with_tape_golfed1(s):
	return [c+('TAPE'*6)[:max(ord(n)+~ord(c),0)]for c,n in zip(s,s[1:]+' ')]


def fix_with_rope(lines, rope=('R','O','P','E')):
	if isinstance(lines, str):
		lines = lines.split('\n')

	if __debug__ and not isinstance(lines, collections.abc.Sequence):
		lines = tuple(lines)
	assert all(map(frpartial(isinstance, str), lines)), (
		'Lines must be of type str')
	assert not lines or all(map(len(lines[0]).__eq__, map(len, lines))), (
		'All lines must have the same length')

	rcolumns = []
	rope = iter(cycle(rope))
	for column in map(tee, zip(*lines)):
		rcolumn = []
		rcolumns.append(rcolumn)
		for c, n in zip(column[0], chain(islice(column[1], 1, None), '\0')):
			rcolumn.append(c)
			rcolumn += islice(rope, max(ord(n) - ord(c) - 1, 0))

	return map(''.join, zip_longest(*rcolumns, fillvalue=' '))


def fix_with_rope_golfed1(l):r=cycle('ROPE');return zip_longest(*(''.join(c+''.join(islice(r,max(ord(n)+~ord(c),0)))for c,n in zip(z,z[1:]+(' ',)))for z in zip(*l)),fillvalue=' ')


def fix_with_scissors(w, scissors):
	w = iter(w)
	scissors = tee(scissors)
	for c, n in zip(scissors[0], chain(islice(scissors[1], 1, None), '\0')):
		yield next(w)
		for i in range(ord(n) - ord(c) - 1): next(w)

	yield from w


def fix_with_scissors_golfed1(w,s):
	w=iter(w)
	for c, n in zip(s,s[1:]+' '):yield next(w);w=islice(w,max(ord(n)+~ord(c),0),None)
	yield from w


def _range_downto_0(start):
	return range(start, 0, -1)


def _blow_up_analyse(s):
	s = tee(s)
	for c, n in zip(s[0], chain(islice(s[1], 1, None), '\0')):
		yield c
		d = ord(n) - ord(c) - 1
		if d > 0:
			r1 = _range_downto_0(d)
			if d & 1:
				yield (r1, _range_downto_0(d + 1))
			else:
				yield (_range_downto_0(d - 1), (d,))
				yield ((), r1)


def blow_up(s):
	s = tuple(_blow_up_analyse(s))
	v = [0] * len(s)
	for i, c in enumerate(s):
		if not isinstance(c, str):
			assert len(c) == 2, (
				'Unexpected object encountered at s[{:d}]: {!r}'.format(i, c))
			for j, d in chain(
				zip(range(i - 1, -1, -1), c[0]),
				zip(range(i, len(s)), c[1])
			):
				v[j] += d

	#print(s, t, sep='\n')
	return ''.join(str(d) if d else c for c, d in zip(s, v))


def blow_up_golfed1(s):
	# def D(d):a=R(d,0,-1);b=R(d+d%2*2-1,0,-1);return[]if d<1 else[[a,b]]if d%2 else[[b,[d]],[[],a]]

	# def D(d):a=R(d,0,-1);return[]if d<1 else[[a,R(d+1,0,-1)]]if d%2 else[[R(d-1,0,-1),[d]],[[],a]]

	# E=lambda o:R(o,0,-1)
	# def D(d):a=E(d);return[]if d<1 else[[a,E(d+1)]]if d%2 else[[E(d-1),[d]],[[],a]]

	Z=zip;R=range;E=lambda o:R(o,0,-1);D=lambda d:[]if d<1else[[E(d),E(d+1)]]if d%2else[[E(d-1),[d]],[[],E(d)]]
	s=sum(([c]+D(ord(n)+~ord(c))for c,n in Z(s,s[1:]+' ')),[]);l=len(s);v=[0]*l
	for i,c in enumerate(s):
		if len(c)>1:
			# for j,d in chain(Z(R(i-1,-1,-1),c[0]),Z(R(i,l),c[1])):v[j]+=d
			for j,d in list(Z(R(i-1,-1,-1),c[0]))+list(Z(R(i,l),c[1])):v[j]+=d
	print(*(d or c for c,d in Z(s,v)),sep='')


def main(*args):
	"""Main entry point for this module. Call with '-h' for usage."""
	args = _parse_args(args or None)
	return globals()['_main_' + args.mode](args)


def _main_tape(args):
	status_names = ('FAIL!', 'success')
	end = '\n' if args.golfed else '\n\n'

	for s in map(args.filter_mode, args.words):
		fixed = ''.join(fix_with_tape(s, args.tape))
		print(repr(s), repr(fixed), sep='\n', end=end)

		if args.golfed:
			fixed_golf = ''.join(args.golfed(s))
			print(
				'{:s} ({:s}):'.format(
					args.golfed.__name__, status_names[fixed == fixed_golf]),
				repr(fixed_golf), end='\n\n')

	if args.golfed:
		import re, inspect
		src = inspect.getsourcelines(args.golfed)[0][1:]
		f = None
		if len(src) == 1:
			m = re.match(r'\s*return\b\s*', src[0])
			if m:
				f = 'f=lambda s:' + src[0][m.end():].rstrip()
		if not f:
			f = 'def f(s):\n' + '\n'.join(map(str.rstrip, src))
		print('{:d} bytes: ---'.format(len(f)), f, sep='\n')


def _main_rope(args):
	total_success = True
	status_names = ('FAIL!', 'success')
	output_headers = ('{:d}. Output (FAIL!):', '{:d}. Output:')
	print_opts = {'sep': '\n', 'end': '\n\n'}

	for i, s in enumerate(map(args.filter_mode, args.words), 1):
		print('{:d}. Input:'.format(i), s, **print_opts)
		fixed = '\n'.join(fix_with_rope(s, args.rope))
		expected = args.demo.get(s)
		print(
			output_headers[expected is None or fixed == expected].format(i),
			fixed, **print_opts)

		if args.golfed:
			fixed_golfed = '\n'.join(map(''.join, args.golfed(s.split('\n'))))
			success = fixed == fixed_golfed
			total_success &= success
			print(
				'{:d}. Golfed output "{:s}" ({:s}):'.format(
					i, args.golfed.__name__, status_names[success]),
				fixed_golfed, **print_opts)

	if args.golfed and total_success:
		import inspect
		src = inspect.getsourcelines(args.golfed)[0]
		src[0] = src[0].replace(args.golfed.__name__, 'f', 1)
		src = 'from itertools import*\n' + '\n'.join(map(str.rstrip, src))
		print('{:d} bytes: ---'.format(len(src)), src, sep='\n')


def _main_scissors(args):
	total_success = True
	status_names = ((' (FAIL!)', ''), ('FAIL!', 'success'))
	print_opts = {'sep': '\n', 'end': '\n' if args.golfed else '\n\n'}

	for i, w in enumerate(args.words, 1):
		scissors, sep, s = w.partition(' ')
		fixed = ''.join(fix_with_scissors(s, scissors))
		expected = args.demo.get(w, fixed)
		success = fixed == expected
		total_success &= success
		print(
			'{:d}{:s}:'.format(i, status_names[0][success]),
			repr(s), repr(scissors), repr(fixed), **print_opts)

		if args.golfed:
			fixed_golfed = ''.join(args.golfed(s, scissors))
			success = fixed_golfed == expected
			total_success &= success
			print(
				'{!r} --- {:s} ({:s})'.format(
					fixed_golfed, status_names[1][success], args.golfed.__name__),
				end='\n\n')

	if args.golfed and total_success:
		import inspect
		src = inspect.getsourcelines(args.golfed)[0]
		src[0] = src[0].replace(args.golfed.__name__, 'f', 1)
		src = 'from itertools import*\n' + '\n'.join(map(str.rstrip, src))
		print('{:d} bytes: ---'.format(len(src)), src, sep='\n')


def _main_blow_up(args):
	import io, contextlib
	total_success = True
	status_names = ((' (FAIL!)', ''), ('FAIL!', 'success'))
	print_opts = {'sep': '\n', 'end': '\n' if args.golfed else '\n\n'}

	for i, s in enumerate(args.words, 1):
		fixed = blow_up(s)
		expected = args.demo.get(s, fixed)
		success = fixed == expected
		total_success &= success
		print(
			'{:d}{:s}:'.format(i, status_names[0][success]),
			repr(s), repr(fixed), **print_opts)

		if args.golfed:
			with contextlib.redirect_stdout(io.StringIO()) as fixed_golfed:
				args.golfed(s)
			fixed_golfed = fixed_golfed.getvalue().rstrip('\n')
			success = fixed_golfed == expected
			total_success &= success
			print(
				'{!r} --- {:s} ({:s})'.format(
					fixed_golfed, status_names[1][success], args.golfed.__name__),
				end='\n\n')

	if args.golfed and total_success:
		import inspect
		src = [
			l for l in map(str.rstrip, inspect.getsourcelines(args.golfed)[0])
			if l and not l.lstrip().startswith('#')
		]
		src[0] = src[0].replace(args.golfed.__name__, 'f', 1)
		src[0:0] = src.pop(1).lstrip().split(';')
		print(
			'{:d} bytes: ---'.format(sum(map(len, src), len(src) - 1)),
			*src, sep='\n')


def identity(x):
	"""Returns its only argument unmodified"""
	return x


class frpartial:
	"""
	A partial function object that binds a number of arguments to a function call.

	The pre-defined arguments are *appended* to the arguments supplied during
	later invocation of the frpartial instance.
	"""

	def __init__(self, func, *args, **kwargs):
		self.func = func
		self.args = args
		self.kwargs = kwargs

	def __call__(self, *args, **kwargs):
		return self.func(*(args + self.args), **dict(self.kwargs, **kwargs))

	def __str__(self):
		return repr(self)

	def __repr__(self):
		return '{:s}({:s})'.format(
			type(self).__qualname__,
			', '.join(chain(
				(repr(self.func),),
				map(repr, self.args),
				starmap('{:s}={!r}'.format, self.kwargs.items()))))


class chartuple(tuple):
	"""Stores a string as a tuple of characters"""

	def __init__(self, *args):
		tuple.__init__(*args)
		assert all(isinstance(c, str) and len(c) == 1 for c in self)

	def __str__(self):
		"""Returns the characters in this tuple as a string"""
		return ''.join(self)


class FrozenDict(collections.abc.Mapping):
	"""A frozen, hashable dictionary object"""

	def __init__(self, *args, **kwargs):
		self._data = dict(*args, **kwargs) if args else kwargs
		self._hash = None

	def __iter__(self):
		return iter(self._data)

	def __len__(self):
		return len(self._data)

	def __contains__(self, key):
		return key in self._data

	def __getitem__(self, key):
		return self._data[key]

	def get(self, key, default=None):
		return self._data.get(key, default)

	def keys(self):
		return self._data.keys()

	def values(self):
		return self._data.values()

	def __hash__(self):
		if self._hash is None:
			self._hash = reduce(
				int.__xor__, map(hash, self.values()),
				~hash(FrozenDict.__base__))
		return self._hash


class named_function:
	"""A named function object"""

	def __init__(self, func, name=None):
		self._func = func
		self._name = name or func.__qualname__

	@property
	def name(self):
		return self._name

	@property
	def func(self):
		return self._func

	def __str__(self):
		return self._name

	def __repr__(self):
		return '{:s}({!r}, name={!r})'.format(
			type(self).__qualname__, self._func, self._name)

	def __call__(self, *args):
		return self._func(*args)

	def __hash__(self):
		return hash(self._name) ^ hash(self._func)


def _check_arg(s, parser, *checkers, type=None, final_type=None):
	val = s

	if type is not None:
		val = type(val)

	for c in checkers:
		if isinstance(c, collections.abc.Sequence):
			c, err = c
		else:
			err = ValueError
		if not c(val):
			if isinstance(err, builtins.type) and issubclass(err, BaseException):
				err = err(s)
			else:
				if callable(err):
					err = err(val)
				if isinstance(err, str):
					parser.error(err)
					err = ValueError(err)
			raise err

	if final_type is not None:
		val = final_type(val)

	return val


def strip_linebreak(s):
	if s.endswith('\n'):
		s = s[:-1]
	return s


def _parse_args(args):
	import argparse, inspect

	p = argparse.ArgumentParser(
		#formatter_class=argparse.ArgumentDefaultsHelpFormatter,
		**dict(zip(('description', 'epilog'),
			map(str.strip, __doc__.rsplit('\n\n', 1)))))
	p.add_argument('words', metavar='WORD', nargs='*',
		help='Words to fix with tape')

	mg = p.add_mutually_exclusive_group()
	defaults = {'scissors': True, 'blow_up': True}
	for mode in ('tape', 'rope'):
		mode_default = chartuple(
			inspect.signature(globals()['fix_with_' + mode])
				.parameters[mode].default)
		defaults[mode] = mode_default
		mg.add_argument('-' + mode[0], '--' + mode, metavar='CHARS',
			nargs='?', const=mode_default,
			type=frpartial(_check_arg,
				p, (bool, mode.capitalize() + ' is empty'), final_type=chartuple),
			help='Character sequence to use as {:s} (default: {})'
				.format(mode, mode_default))
	mg.add_argument('-s', '--scissors', action='store_true',
		help='Split each word into a pair at the first space character. '
			'In each pair of words use the 1st as "scissors" to cut the 2nd.')
	mg.add_argument('-b', '--blow-up', action='store_true',
		help='Blow each word up with numbers.')

	filter_mode_choices = FrozenDict(
		((s, named_function(getattr(str, s), s))
			for s in ('lower', 'upper', 'casefold')),
		none=named_function(identity, 'none'))
	p.add_argument('-f', '--filter-mode',
		type=filter_mode_choices.__getitem__,
		choices=filter_mode_choices.values(),
		default=filter_mode_choices['lower'],
		help='Apply input words filter (default: lower)')

	p.add_argument('--demo',
		action='store_const', default={}, const={
				'tape': 'fixed-it-with-tape.txt',
				'rope': 'fixed-it-with-rope.txt',
				'scissors': 'cut-it-with-scissors.txt',
				'blow_up': 'oops-i-blew-it-up.txt',
			},
		help='Add a series of demo arguments to the word list.')
	p.add_argument('--golfed', metavar='ID', nargs='?', const='1',
		help='Run and test the code-golfed implementation.')

	args = p.parse_args(args)
	_parse_mode(args, defaults)
	_parse_golfed(args, defaults, filter_mode_choices)
	_parse_demo(args)
	_parse_words(args)
	#print(args); p.exit()
	return args


def _parse_mode(args, defaults):
	args.mode = next(filter(fpartial(getattr, args), defaults.keys()), 'tape')
	if getattr(args, args.mode) is None:
		setattr(args, args.mode, defaults[args.mode])


def _parse_golfed(args, defaults, filter_mode_choices):
	if args.golfed is None:
		return

	for golfed_name in ('fix_with_', ''):
		golfed_name = (
			'{:s}{:s}_golfed{:s}'.format(golfed_name, args.mode, args.golfed))
		golfed_value = globals().get(golfed_name)
		if golfed_value is not None:
			args.golfed = golfed_value
			break
	if args.golfed is None:
		p.error('No such code-golfed implementation: ' + repr(golfed_name))
	if getattr(args, args.mode) != defaults[args.mode]:
		p.error(
			'The code-golfed implementation is incompatible with the custom '
			'fixtures string ' + repr(getattr(args, args.mode)))
	if args.filter_mode.name not in ('lower', 'none'):
		import sys
		print("Warning: Forcing filter mode to 'none' in demo mode.",
			end='\n\n', file=sys.stderr)
	args.filter_mode = filter_mode_choices['none']


def _parse_demo(args):
	if not args.demo:
		return

	import sys, os.path
	from collections import OrderedDict
	testcase_file = open(
		os.path.join(sys.path[0], 'test-cases', args.demo[args.mode]))
	with testcase_file:
		args.demo = OrderedDict(starmap(
			fpartial(_parse_testcase, filename=testcase_file.name),
			zip(*starmap(frpartial(islice, None, 2),
				map(itemgetter(slice(None, None, -1)),
					enumerate(tee(filter(itemgetter(1),
						enumerate(map(str.rstrip, testcase_file))))))))))
	args.words += args.demo.keys()


def _parse_testcase(*lines, filename='<unknown>'):
	if len(lines) != 2:
		raise TypeError('Expected 2 arguments, not {:d}'.format(len(lines)))

	for lineno, line in lines:
		try:
			yield _parse_testcase_part(line)
		except:
			raise ValueError(
				'Invalid test case in line {:d} of file {!r}: {!r}'
					.format(lineno, filename, line))


def _parse_testcase_part(s):
	delimiter = ':'
	prefix, sep, testcase = s.partition(delimiter)
	if not sep:
		raise ValueError('No delimiter ({!r})'.format(delimiter))
	return eval(testcase)


def _parse_words(args):
	if args.words:
		return

	import sys
	if sys.stdin:
		if args.mode == 'rope':
			args.words = (sys.stdin.read(),)
		else:
			args.words = map(strip_linebreak, sys.stdin)


if __name__ == '__main__':
	main()
