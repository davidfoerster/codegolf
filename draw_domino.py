#!/usr/bin/python3
"""
Print domino pips

See https://codegolf.stackexchange.com/questions/151588/draw-me-a-domino.
"""


def half_pip_mask(n):
	if not 0 <= n <= 9:
		raise ValueError('Expected a value between 0 and 9, got {:d}'.format(n))

	p = list(map(n.__gt__, (3, 5, 1, 7)))
	p.append(bool(n & 1))
	p.extend(p[-2::-1])
	return p


def half_pip_matrix(n, symbols, sep=' '):
	n = tuple(map(symbols.__getitem__, half_pip_mask(n)))
	return map(sep.join, (n[0:3], n[3:6], n[6:9]))


def pip(a, b, horizontal=False, hspace=' ', vspace='\n', symbols=(' ', '⚫'),
	border=('─', '│', '┌', '┐', '└', '┘', '├', '┤', '┬', '┴')
):
	if len(symbols) == 1:
		symbols = (hspace, symbols[0])

	a = half_pip_matrix(a, symbols, hspace)
	b = half_pip_matrix(b, symbols, hspace)
	v = border[1]

	if horizontal:
		vl = v + hspace
		vr = hspace + v
		vc = hspace + v + hspace
		sep = vr + vspace + vl
		line = border[0] * 7
		l = (
			border[2] + line + border[8] + line + border[3],
			vl + sep.join(map(vc.join, zip(a, b))) + vr,
			border[4] + line + border[9] + line + border[5])
	else:
		sep = v + vspace + v
		line = border[0] * 5
		l = (
			border[2] + line + border[3],
			v + sep.join(a) + v,
			border[6] + line + border[7],
			v + sep.join(b) + v,
			border[4] + line + border[5])

	return vspace.join(l) + vspace


def parse_pip_def(s):
	return map(int, s.split(',', 1))


def _parse_args(args):
	import argparse
	ap = argparse.ArgumentParser(
		formatter_class=argparse.ArgumentDefaultsHelpFormatter,
		**dict(zip(('description', 'epilog'),
			map(str.strip, __doc__.rsplit('\n\n', 1)))))

	ap.add_argument('-o', '--orientation', metavar='OR',
		choices=('horizontal', 'h', 'vertical', 'v'), default='h',
		help='Pip orientation')
	ap.add_argument('pip', nargs='*',
		help='Pip definition, a tuple of comma-separated integers')

	return ap.parse_args(args)


def main(args):
	args = _parse_args(args)
	args.horizontal = args.orientation.startswith('h')

	if args.pip:
		for pip_def in args.pip:
			sys.stdout.write(pip(*parse_pip_def(pip_def), horizontal=args.horizontal))
	else:
		import random
		sys.stdout.write(pip(
			random.randrange(10), random.randrange(10), args.horizontal))


if __name__ == '__main__':
	import sys
	main(sys.argv[1:])
