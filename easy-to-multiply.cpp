#include <limits>
#include <type_traits>
#include <utility>
#include <algorithm>
#include <string>
#include <iosfwd>
#include <sstream>
#include <iostream>
#include <locale>
#include <cstddef>
#include <cstdint>
#include <cstring>
#include <cassert>
#include <sysexits.h>


template <class T>
inline constexpr std::size_t countof( const T& )
{
	return std::extent<T>::value;
}


template <class IntT>
inline constexpr IntT ceildiv( IntT dividend, IntT divisor )
{
	return (dividend - 1) / divisor + 1;
}


template <class IntT>
inline constexpr bool islog2( IntT n )
{
	return (n & (n - 1)) == 0;
}


inline constexpr int clz( unsigned int n ) {
	return __builtin_clz(n);
}
inline constexpr int clz( unsigned long int n ) {
	return __builtin_clzl(n);
}
inline constexpr int clz( unsigned long long int n ) {
	return __builtin_clzll(n);
}


template <class IntT>
inline constexpr unsigned log2( IntT n )
{
	typedef std::numeric_limits<IntT> lim;
	return static_cast<unsigned>((lim::digits - !lim::is_signed) - clz(n));
}


template <class IntT>
inline constexpr unsigned log2_ceil( IntT n )
{
	return log2(n) + !islog2(n);
}


template <class IntT>
bool easy_to_multiply( IntT a, IntT b, IntT base )
{
	typedef std::numeric_limits<IntT> lim;
	assert(base >= 2);

	const std::size_t max_digits = ceildiv(
		2 * static_cast<unsigned>(lim::digits + lim::is_signed),
		(base >= 2) ? log2_ceil(base) : 0);
	IntT p[max_digits] = {};
	if (a > b) std::swap(a, b);

	for (unsigned i = 0; a != 0; i++, a /= base)
	{
		const IntT x = a % base;
		const IntT base_ceildiv_x =
			ceildiv(base, std::max(x, static_cast<IntT>(1)));

		IntT _b = b;
		for (unsigned j = i + 1; _b != 0; j++, _b /= base)
		{
			assert(j < max_digits);
			const IntT y = _b % base;
			if (y >= base_ceildiv_x)
				return false;
			const IntT xy = x * y;
			if (p[j] >= base - xy)
				return false;
			p[j] += xy;
		}
	}

	return true;
}


template <class IntT, class CharT, class Traits>
void main_pair( IntT a, IntT b, std::basic_ostream<CharT, Traits>& os )
{
	os << a << " x " << b << " = " << (a * b) << " => ";
	if (!easy_to_multiply(a, b, static_cast<IntT>(10)))
		os << "NOT ";
	os << "easy" << std::endl;
}


template <class CharT, class Traits>
bool main_str( std::basic_istream<CharT, Traits>& is,
	std::basic_ostream<CharT, Traits>& os )
{
	std::uintmax_t a, b;

	is >> std::noskipws >> a;
	if (is.get() != Traits::to_int_type(is.widen('x')))
		is.setstate(std::ios::failbit);
	is >> b;

	bool success = !(is.rdstate() & ~std::ios::eofbit);
	if (success)
		main_pair(a, b, os);
	return success;
}


int main( int argc, char *argv[] )
{
	using std::ios;
	using std::cin;
	using std::cout;
	using std::cerr;

	std::ios::sync_with_stdio(false);
	std::cout.imbue(std::locale(""));
	std::cout.exceptions(ios::badbit | ios::failbit);

	argc--; argv++;
	if (argc > 0 && std::strcmp(*argv, "--test") == 0)
	{
		argc--; argv++;
		static const unsigned easy[][2] =
			{ {331, 1021}, {1021, 331}, {101, 99}, {333, 11111}, {243, 201} };
		for (size_t i = 0; i < countof(easy); i++)
			main_pair(easy[i][0], easy[i][1], cout);

		cout << std::endl;

		static const unsigned not_easy[][2] =
			{ {431, 1021}, {12, 16}, {3, 4}, {3333, 1111}, {310, 13} };
		for (size_t i = 0; i < countof(not_easy); i++)
			main_pair(not_easy[i][0], not_easy[i][1], cout);
	}

	if (argc > 0)
	{
		std::string sbuf;
		std::istringstream iss;
		iss.exceptions(ios::badbit | ios::failbit);
		for (; argc > 0 && iss; argc--, argv++)
		{
			iss.clear();
			iss.str(sbuf.assign(*argv));
			main_str(iss, cout);
			if (!(iss.rdstate() & ios::eofbit))
				iss.setstate(ios::failbit);
		}
	}
	else
	{
		typedef std::istream::traits_type traits_type;
		cin.tie(nullptr);
		cin.exceptions(ios::badbit | ios::failbit);
		while (traits_type::not_eof(cin.peek()) && main_str(cin, cout) && cin.good())
		{
			const traits_type::int_type c = cin.get();
			if (c != '\n')
			{
				if (traits_type::not_eof(c))
					cin.setstate(ios::failbit);
				break;
			}
		}
	}

	return EX_OK;
}
