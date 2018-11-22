#!/usr/bin/python3
# https://codegolf.stackexchange.com/q/175236


def square(x):
	return x * x


def naturals_sum(n):
	return n * (n + 1) // 2


def sum_square_difference(n):
	return sum(square, range(n)) - square(naturals_sum(n))


s=lambda x:x*x
s=(2).__rpow__
def sum_square_difference_golfed1(n):
	return sum(x*x for x in range(n))-(n*(n+1)/2)**2
	return sum(map(s,range(n)))-s(n*(n+1)/2)
