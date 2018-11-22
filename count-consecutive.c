#ifndef _POSIX_C_SOURCE
#define _POSIX_C_SOURCE 200809L
#endif

#include <stddef.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <stdarg.h>
#include <stdio.h>
#include <limits.h>
#include <string.h>
#include <ctype.h>
#include <getopt.h>
#include <errno.h>
#include <sysexits.h>
#include <assert.h>


#define MAX(a, b) ({ \
		__typeof__(a) __a = (a); \
		__typeof__(b) __b = (b); \
		(__a >= __b) ? __a : __b; \
	})


#define div_ceil_u(dividend, divisor) \
	(((dividend) > 0) ? (((dividend) - 1) / (divisor) + 1) : (0 / (divisor)))


#define most_significant_bits(x, n) ((x) >> (sizeof(x) * CHAR_BIT - (n)))


inline static int __builtin_ffsu(unsigned x) {
	return __builtin_ffs((int) x);
}
inline static int __builtin_ffslu(unsigned long x) {
	return __builtin_ffsl((long) x);
}
inline static int __builtin_ffsllu(unsigned long long x) {
	return __builtin_ffsll((long long) x);
}
#define trailing_zero_count(n) (_Generic((n), \
		int: __builtin_ffs, \
		unsigned int: __builtin_ffsu, \
		long: __builtin_ffsl, \
		unsigned long: __builtin_ffslu, \
		long long: __builtin_ffsll, \
		unsigned long long: __builtin_ffsllu \
	)(n) - 1)

#define trailing_one_count(n) trailing_zero_count(~(n))


#define popcount(n) (_Generic((n), \
		unsigned int: __builtin_popcount, \
		unsigned long: __builtin_popcountl, \
		unsigned long long: __builtin_popcountll \
	)(n))


#define __same_type(a, b) \
	__builtin_types_compatible_p(__typeof__(a), __typeof__(b))

#define __is_array(obj) (!__same_type((obj), &*(obj)))

#define __assert_array(obj) \
	static_assert(__is_array(obj), "Expected an array object, got '" #obj "'")

#define countof(arr) \
	({ __assert_array(arr); sizeof(arr) / sizeof(*(arr)); })


static void dbg_printf(const char *fmt, ...)
	__attribute__((format(printf, 1, 2)));

void dbg_printf(const char *fmt __attribute__((unused)), ...)
{
#ifdef DEBUG
	va_list ap;
	va_start(ap, fmt);
	vfprintf(stderr, fmt, ap);
	va_end(ap);
#endif
}


#define BITSET_DECLARE(name, size) uintmax_t (name)[ \
	((size) >= 0) ? div_ceil_u(size, (ssize_t) sizeof(uintmax_t) * CHAR_BIT) : -1 ]

static void bitset_set(uintmax_t *bitset, size_t position)
{
	static const size_t bits_per_element = sizeof(*bitset) * CHAR_BIT;
	bitset[position / bits_per_element] |=
		(uintmax_t)(1) << (position % bits_per_element);
}


#define longest_bit_sequence(bitset) \
	__longest_bit_sequence_impl(bitset, countof(bitset))

static size_t __longest_bit_sequence_impl(const uintmax_t *bitset,
	size_t bitset_size)
{
	assert(bitset_size <= SIZE_MAX / sizeof(*bitset) &&
		(uintptr_t) bitset <= UINTPTR_MAX - bitset_size * sizeof(*bitset));

	const uintmax_t *const bitset_end = bitset + bitset_size;
	size_t longest = 0, current = 0;
	for (; bitset < bitset_end; bitset++)
	{
		uintmax_t bits = *bitset;
		size_t previous = current;
		while (bits)
		{
			int count = trailing_zero_count(bits);
			dbg_printf("\t%zu: (%2d) %0*jX >> %2d -> ",
				bitset_size - (size_t)(bitset_end - bitset), popcount(bits),
				(int)(sizeof(bits) * 2), bits, count);
			assert(count >= 0);
			bits >>= count;
			count = trailing_one_count(bits);
			dbg_printf("%0*jX >> %2d -> ", (int)(sizeof(bits) * 2), bits, count);
			assert(count > 0);
			bits >>= count;
			current = previous + (unsigned) count;
			longest = MAX(longest, current);
			dbg_printf("%zu\n", current);
			previous = 0;
		}
		if (!most_significant_bits(*bitset, 1))
			current = 0;
	}

	return longest;
}


#define ALPHABET_SIZE ('Z' - 'A' + 1)


static int toupper_hack(int c)
{
	return c & ~('A' ^ 'a');
}


static size_t longest_consecutive_run(const char *s)
{
	if (!*s)
		return 0;

	BITSET_DECLARE(charset, ALPHABET_SIZE) = {0};
	for (; *s; s++)
	{
		int c = toupper_hack(*s) - 'A';
		if (c >= 0 && c < ALPHABET_SIZE)
			bitset_set(charset, (unsigned) c);
	}

	return longest_bit_sequence(charset);
}


static int count_digits(uintmax_t n, uintmax_t base)
{
	if (base < 2)
	{
		errno = ERANGE;
		return -1;
	}

	int count = 1;
	for (; n >= base; n /= base)
		count++;

	return count;
}


static void main_action(const char *s, unsigned count, int count_digits)
{
	if (
		(count_digits >= 0 &&
			printf("%*u: %s => ", count_digits, count, s) < 0) ||
		printf("%zu\n", longest_consecutive_run(s)) < 0)
	{
		perror("Error writing to stdout");
		exit(EX_IOERR);
	}
}


static ssize_t getline2(char **buf, size_t *bufsize, FILE *f)
{
	ssize_t count = getline(buf, bufsize, f);
	if (count > 0 && (*buf)[count-1] == '\n')
		(*buf)[--count] = '\0';
	return count;
}


int main(int argc, char *argv[])
{
	int digits = 0;

	static const struct option long_options[] = {
		{ "quiet", no_argument, NULL, 'q' },
		{ NULL }
	};
	int opt;
	while ((opt = getopt_long(argc, argv, "q", long_options, NULL)) != -1)
	{
		switch (opt)
		{
		case 'q':
			digits = -1;
			break;

		case '?':
		default:
			fprintf(stderr, "Usage: %s [-q|--quiet] [words...]\n", argv[0]);
			return EX_USAGE;
		}
	}

	opt = optind;
	if (opt < argc)
	{
		if (!digits)
			digits = count_digits((unsigned)(argc - opt), 10);
		for (unsigned i = 1; opt < argc; i++, opt++)
			main_action(argv[opt], i, digits);
	}
	else
	{
		if (!digits)
			digits = 1;

		FILE *fin = stdin;
		char *buf = NULL;
		size_t bufsize = 0;
		ssize_t read;
		unsigned count = 0;
		while ((read = getline2(&buf, &bufsize, fin)) >= 0)
		{
			//printf("0x%0*tX, %4zu, %4zd\n", (int) sizeof(buf) * 2, (uintptr_t) buf, bufsize, read);
			main_action(buf, ++count, digits);
		}

		int errnum = errno;
		free(buf);
		if (ferror(fin))
		{
			fprintf(stderr,
				"%s: Error reading from stdin: %s\n", argv[0], strerror(errnum));
			return EX_IOERR;
		}
	}

	if (fclose(stdout) != 0)
	{
		fprintf(stderr,
			"%s: Error writing to stdout: %s\n", argv[0], strerror(errno));
		return EX_IOERR;
	}

	return EXIT_SUCCESS;
}
