#!/usr/bin/python3
# https://codegolf.stackexchange.com/q/171395

__all__ = ('decode',)
import sys
import itertools
islice = itertools.islice


DECODER_MAP = dict(zip(
	('I', 'A', 'O', 'U',
		'IDI', 'IDA', 'IDO', 'IDU',
		'ADI', 'ADA', 'ADO', 'ADU',
		'ODI', 'ODA', 'ODO', 'ODU'),
	itertools.count()))


def decode(s, msb_byteorder=True):
	assert s == '' or s.startswith('B')
	nibbles = itertools.tee(
		map(DECODER_MAP.__getitem__, islice(s.split('B'), 1, None)))
	return ''.join(map(chr, map(int.__or__,
		islice(nibbles[0], bool(msb_byteorder), None, 2),
		map((4).__rlshift__, islice(nibbles[1], not msb_byteorder, None, 2)))))


def decode_golfed1(s):t=['IAOU'.find(n[-1])|' IAOU'.find(n[:len(n)>1])*4for n in s.split('B')[1:]];return''.join(chr(l|h<<4)for h,l in zip(t[::2],t[1::2]))


def main(args=None):
	if args is None:
		args = sys.argv[1:] or map(str.rstrip, sys.stdin)

	for s in args:
		print(repr(decode(s)))


if __name__ == '__main__':
	main()
