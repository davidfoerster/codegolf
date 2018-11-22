#!/usr/bin/python3
# https://codegolf.stackexchange.com/q/159881


def is_self_number(x):
	if x <= 0:
		if x == 0:
			return (False, (0,))
		else:
			raise ValueError('Expected a positive number, got ' + str(x))

	counter_examples = tuple(filter(x.__eq__,
		map(_counter_example_candidate, range(1, x))))
	return (not counter_examples, counter_examples)


def _counter_example_candidate(n):
	return n + sum(map(int, str(n)))


def is_self_number_golfed1(x):
	return all(x^n+sum(map(int,str(n)))for n in range(x))


def main(*args):
	if args:
		args = list(args)
	else:
		import sys
		args = sys.argv[1:]

	if args and args[0] == '--golfed':
		del args[0]
		if args and not args[0].startswith('-'):
			golfed = args.pop(0)
		else:
			golfed = '1'
		golfed = globals()['is_self_number_golfed' + golfed]
	else:
		golfed = None

	if args and args[0] == '--':
		del args[0]

	if len(args) == 1 and args[0] == '-':
		import sys
		args = filter(None, map(str.strip, sys.stdin))

	total_success = True
	for x in map(int, args):
		b, counter_examples = is_self_number(x)
		print(
			'{:d} ({})'.format(x, b),
			*map(_format_counter_example, counter_examples),
			sep=' = ')
		if golfed:
			c = golfed(x)
			total_success &= c == b
			print('{:d}: {} ({:s}: {:s})'.format(
				x, c, golfed.__name__, ('FAIL!', 'success')[c == b]))

	if golfed and total_success:
		import inspect
		src = inspect.getsourcelines(golfed)[0]
		return_prefix = 'return'

		if (len(src) == 2 and src[0].startswith('def ') and
			src[1].strip().startswith(return_prefix)
		):
			src[0] = 'lambda {:s}:{:s}'.format(
				src[0][ src[0].find('(') + 1 : src[0].find(')') ].replace(' ', ''),
				src[1].strip()[ len(return_prefix): ].lstrip())
			del src[1:]
		else:
			src[0] = src[0].replace(golfed.__name__, 'f', 1)
			src[:] = map(str.rstrip, src)

		print('',
			'{:d} bytes'.format(sum(map(len, src)) + len(src) - 1),
			*src, sep='\n')


def _format_counter_example(n):
	n = str(n)
	return n + ' + ' + ' + '.join(n)


if __name__ == '__main__':
	main()
