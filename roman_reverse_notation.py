#!/usr/bin/python3 -O
"""
Reverse/Polish notation calculator for roman numerals.

It supports the operations of addition (+), subtraction (- and − (U+2212)),
multiplication (*, × (U+00D7), · (U+00B7), and ⋅ (U+22C5)), and division
(/ and ÷ (U+00F7)). Roman digits may be represented with latin letters or
roman numeral characters (U+2160 through U+217F).

See https://codegolf.stackexchange.com/questions/152180/romaneverse-polish-notation
"""
import re, operator, itertools, numbers
from functools import partial as fpartial
from fractions import Fraction


ROMAN_NUMERALS_DECODE = {
	'I': 1, 'Ⅰ': 1,
	'V': 5, 'Ⅴ': 5,
	'X': 10, 'Ⅹ': 10,
	'L': 50, 'Ⅼ': 50,
	'C': 100, 'Ⅽ': 100,
	'D': 500, 'Ⅾ': 500,
	'M': 1000, 'Ⅿ': 1000
}

OPERATORS_REALDIV = {
	'+': operator.add,
	'-': operator.sub, '−': operator.sub,
	'*': operator.mul, '×': operator.mul, '⋅': operator.mul, '·': operator.mul,
	'/': operator.truediv, '÷': operator.truediv
}

OPERATORS_RATIONALDIV = {
	c: Fraction if op is operator.truediv else op
	for c, op in OPERATORS_REALDIV.items()
}


def decode_roman_numeral(s, subtractive=True):
	s = map(ROMAN_NUMERALS_DECODE.__getitem__, s)
	if subtractive:
		s = iter(run_lengths(s))
		try:
			last_v, last_rl = next(s)
		except StopIteration:
			return 0
		n = 0
		for v, rl in s:
			if last_v >= v:
				n += last_v * last_rl
			else:
				n -= last_v * last_rl
			last_v = v
			last_rl = rl
		return n + last_v * last_rl
	else:
		return sum(s)


def run_lengths(iterable):
	iterable = iter(iterable)
	try:
		last_item = next(iterable)
	except StopIteration:
		return

	run_length = 1
	for item in iterable:
		if item == last_item:
			run_length += 1
		else:
			yield (last_item, run_length)
			last_item = item
			run_length = 1

	yield (last_item, run_length)


ROMAN_NUMERALS_ENCODE = sorted(
	((value, char) for char, value in ROMAN_NUMERALS_DECODE.items()
		if char.isalpha()),
	key=operator.itemgetter(0), reverse=True)

ROMAN_NUMERALS_ENCODE_ALT = sorted(
	((value, char) for char, value in ROMAN_NUMERALS_DECODE.items()
		if not char.isalpha()),
	key=operator.itemgetter(0), reverse=True)

ROMAN_NUMERAL_SUBTRACTIVE_PAIRS = {
	5: 6,
	10: 6,
	50: 4,
	100: 4,
	500: 2,
	1000: 2
}

def encode_roman_numeral(n, subtractive=True, numerals=ROMAN_NUMERALS_ENCODE):
	if isinstance(n, numbers.Rational) and n.denominator != 1:
		return (
			_encode_roman_numeral_impl(n.numerator, subtractive, numerals) + '/' +
			_encode_roman_numeral_impl(n.denominator, subtractive, numerals))
	else:
		return _encode_roman_numeral_impl(int(n), subtractive, numerals)


def _encode_roman_numeral_impl(n, subtractive, numerals):
	if n <= 0:
		raise ValueError('Expected positive integer, got ' + repr(n))

	rn = []
	for value, char in numerals:
		m, n = divmod(n, value)
		if m:
			rn.append(char * m)
		if subtractive and value != 1:
			subtrahend_value, subtrahend_char = (
				numerals[ROMAN_NUMERAL_SUBTRACTIVE_PAIRS[value]])
			if n >= value - subtrahend_value:
				rn.append(subtrahend_char)
				rn.append(char)
				n -= value - subtrahend_value
		if not n:
			break
	return ''.join(rn)


TOKEN_REGEX = re.compile(
	'([{}-]+)|([{}]+)'.format(
		''.join(filter('-'.__ne__, OPERATORS_REALDIV.keys())),
		''.join(ROMAN_NUMERALS_DECODE.keys())),
	re.IGNORECASE)

def calc_roman_reverse(s, subtractive=True, ops=OPERATORS_REALDIV):
	if isinstance(s, str): s = (s,)
	opstack = []
	for op, num in itertools.chain.from_iterable(
		map(operator.methodcaller('groups'), TOKEN_REGEX.finditer(t)) for t in s
	):
		if num is not None:
			opstack.append(decode_roman_numeral(num.upper(), subtractive))
			#print('Pu:', num, '=', opstack[-1])
		else:
			arg2 = opstack.pop()
			arg1 = opstack.pop()
			opstack.append(ops[op](arg1, arg2))
			#opstack[-2:] = (ops[op](*opstack[-2:]),)
			#print('Op:', arg1, op, arg2, '=', opstack[-1])
	return opstack


from functools import*
N=dict(I=1,V=5,X=10,L=50,C=100,D=500,M=1000)
def c1(w):
	s=[]
	for t in w.split():s+=[str(reduce(lambda n,v:n+v-n%v*2,map(N.get,t))if t[0]in N else eval(s.pop(-2)+t+s.pop()))]
	return s

from functools import*
N=dict(I=1,V=5,X=10,L=50,C=100,D=500,M=1000)
def c2(w):
	return reduce(lambda s,t:s+[str(reduce(lambda n,v:n+v-n%v*2,map(N.get,t))if t[0]in N else eval(s.pop(-2)+t+s.pop()))],w.split(),[])


def main(args):
	import argparse
	ap = argparse.ArgumentParser(
		formatter_class=argparse.ArgumentDefaultsHelpFormatter,
		**dict(zip(('description', 'epilog'),
			map(str.strip, __doc__.rsplit('\n\n', 1)))))
	ap.add_argument('expr', nargs='*',
		help='A sequence of arithmetic expressions. (Default: read from standard '
			'input)')
	ap.add_argument('-S', '--no-subtractive',
		action='store_true', default=False,
		help='Do not use subtractive notation like CIV.')
	ap.add_argument('-d', '--division',
		choices=('real', 'rational'), default='real',
		help='Select the type of division to use.')
	ap.add_argument('-o', '--output-encoding',
		choices=('arabic', 'roman', 'roman-alt'), default='arabic',
		help='Select the encoding of the results.')
	ap.add_argument('--golfed', action='store_true',
		help='Use the code-golfed implementation. Implies subtractive notation, '
			'real division and arabic output.')
	args = ap.parse_args(args)

	if not args.expr:
		args.expr = sys.stdin

	if args.golfed:
		results = c2(' '.join(args.expr))
	else:
		ops = globals()['OPERATORS_' + args.division.upper() + 'DIV']
		results = calc_roman_reverse(args.expr, not args.no_subtractive, ops)
		if args.output_encoding.startswith('roman'):
			encoder_kwargs = { 'subtractive': not args.no_subtractive }
			if args.output_encoding == 'roman-alt':
				encoder_kwargs['numerals'] = ROMAN_NUMERALS_ENCODE_ALT
			results = map(fpartial(encode_roman_numeral, **encoder_kwargs), results)
		else:
			assert args.output_encoding == 'arabic'

	print(*results, sep='\n')


if __name__ == '__main__':
	import sys
	main(sys.argv[1:])
