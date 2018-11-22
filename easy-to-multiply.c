#include <stddef.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <inttypes.h>
#include <limits.h>
#include <err.h>
#include <sysexits.h>
#include <assert.h>


#define countof( array ) (sizeof(array) / sizeof(*(array)))

#define ceildiv( dividend, divisor ) (((dividend) - 1) / (divisor) + 1)

#define max( a, b ) (((a) >= (b)) ? (a) : (b))

#define swap( a, b ) ({ \
		__typeof__(a) *__a = &(a), *__b = &(b), __temp = *__a; \
		*__a = *__b; *__b = __temp; (void) 0; \
	})

#define islog2( n ) ({ __typeof__(n) __n = (n); (__n & (__n - 1)) == 0; })

inline unsigned log2_imax( uintmax_t n )
{
	return (unsigned)(sizeof(n) * CHAR_BIT - 1) - (unsigned) __builtin_clzll(n);
}

inline unsigned log2_ceil_imax( uintmax_t n )
{
	return log2_imax(n) + !islog2(n);
}


bool easy_to_multiply( uintmax_t a, uintmax_t b, uintmax_t base )
{
	assert(base >= 2);

	const size_t max_digits = ceildiv(
		(sizeof(a) + sizeof(b)) * CHAR_BIT,
		(base >= 2) ? log2_ceil_imax(base) : 0);
	uintmax_t p[max_digits];
	memset(p, 0, max_digits * sizeof(*p));
	if (a > b) swap(a, b);

	for (unsigned i = 0; a != 0; i++, a /= base)
	{
		const uintmax_t x = a % base;
		const uintmax_t base_ceildiv_x = ceildiv(base, max(x, 1));

		uintmax_t _b = b;
		for (unsigned j = i + 1; _b != 0; j++, _b /= base)
		{
			assert(j < max_digits);
			const uintmax_t y = _b % base;
			if (y >= base_ceildiv_x)
				return false;
			const uintmax_t xy = x * y;
			if (p[j] >= base - xy)
				return false;
			p[j] += xy;
		}
	}

	return true;
}


int main_pair( uintmax_t a, uintmax_t b )
{
	return
		printf("%'"PRIuMAX" x %'"PRIuMAX" = %'"PRIuMAX" => %seasy\n",
			a, b, a * b, easy_to_multiply(a, b, 10) ? "" : "NOT ");
}


int main_str( const char *s )
{
	uintmax_t a, b;
	if (sscanf(s, "%"SCNuMAX"x%"SCNuMAX, &a, &b) != 2)
	{
		err(EX_DATAERR,
			"Argument \"%s\" doesn't conform to template \"NxM\" for two natural numbers N and M up until %'"PRIuMAX,
			s, UINTMAX_MAX);
	}

	return main_pair(a, b);
}


int main( int argc, char *argv[] )
{
	if (argc == 2 && strcmp(argv[1], "--test") == 0)
	{
		static const unsigned easy[][2] =
			{ {331, 1021}, {1021, 331}, {101, 99}, {333, 11111}, {243, 201} };
		for (size_t i = 0; i < countof(easy); i++)
			main_pair(easy[i][0], easy[i][1]);

		putchar('\n');

		static const unsigned not_easy[][2] =
			{ {431, 1021}, {12, 16}, {3, 4}, {3333, 1111}, {310, 13} };
		for (size_t i = 0; i < countof(not_easy); i++)
			main_pair(not_easy[i][0], not_easy[i][1]);
	}
	else
	{
		for (int i = 1; i < argc; i++)
			main_str(argv[i]);
	}
	return EX_OK;
}
