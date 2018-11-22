/*
 * According to https://codegolf.stackexchange.com/q/157770
 */
#define _GNU_SOURCE
#if !defined(_GNU_SOURCE) && _XOPEN_SOURCE < 700 && _POSIX_C_SOURCE < 200809L
	#define _POSIX_C_SOURCE 200809L
#endif

#ifdef _GOLFED
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wconversion"
#pragma GCC diagnostic ignored "-Wsign-conversion"
#pragma GCC diagnostic ignored "-Wsign-compare"
#pragma GCC diagnostic ignored "-Wreturn-type"
#pragma GCC diagnostic ignored "-Wimplicit-int"
#pragma GCC diagnostic ignored "-Wunused-value"
#include "oops-i-blew-it-up-golfed1.c"
#pragma GCC diagnostic pop
#endif

#include <stddef.h>
#include <stdlib.h>
#include <stdbool.h>
#include <stdio.h>
#include <string.h>
#include <stdint.h>
#include <limits.h>
#include <ctype.h>
#include <errno.h>
#include <err.h>
#include <assert.h>


#ifdef DEBUG
	#define debug(fmt, ...) ((void) fprintf(stderr, (fmt), ##__VA_ARGS__))
#else
	#define debug(fmt, ...) ((void)0)
#endif

#ifndef verify
	#ifdef NDEBUG
		#define verify(expr) ((void)(expr))
		#define verify_perror(expr) ((void)(expr))
	#else
		#define verify(expr) assert(expr)
		#define verify_perror(expr) ((void)((expr) || (assert_perror(errno), 0)))
	#endif
#endif

#define __conditional_impl(a, b, cmp) ({ \
		const __typeof__(1 ? (a) : (b)) __a = (a), __b = (b); \
		((__a) cmp (__b)) ? __a : __b; \
	})
#define min(a, b) __conditional_impl(a, b, <)
#define max(a, b) __conditional_impl(a, b, >)


bool blow_up(const char *const s, FILE *const out)
{
	const size_t s_len = strlen(s);

	// Return early for edge cases
	if (s_len < 2)
		return s_len > 0 && putc(*s, out) != EOF;

	// Scan for holes in s and write the result to t
	assert(s_len <= SIZE_MAX / 2);
	const size_t t_len = s_len * 3 - 2;
	int *const t = malloc(t_len * sizeof(*t));
	size_t j = 0;
	for (size_t i = 1; i < s_len; i++)
	{
		assert(j < t_len);
		t[j++] = s[i-1];

		assert(s[i-1] >= 0 && s[i] >= 0);
		const int d = s[i] - s[i-1] - 1;
		if (d > 0)
		{
			assert(d < CHAR_MAX);
			assert(j < t_len);
			t[j++] = -d;
			if (!(d % 2))
			{
				assert(j < t_len);
				t[j++] = 0;
			}
		}
	}
	t[j++] = s[s_len - 1];

	// Accumulate (overlapping) outwards expansions of holes in v
	const size_t v_len = j;
	unsigned *const v = calloc(v_len, sizeof(*v));
	for (size_t i = 0; i < v_len; i++)
	{
		if (t[i] >= 0)
			continue;

		unsigned d = (unsigned) -t[i];
		const unsigned odd = d & 1;
		d += odd;
		for (unsigned j = 0; j < d && j <= i; j++)
			v[i - j] += d - j;

		i += !odd;
		assert(odd || (i < v_len && t[i] == 0));
		for (unsigned j = odd; j < d && i + j < v_len; j++)
			v[i + j] += d - j;
	}

	// Merge and print string data (from t) and expanded holes (from v)
	bool success = true;
	for (size_t i = 0; success && i < v_len; i++)
	{
		const unsigned d = v[i];
		if (d)
		{
			success = fprintf(out, "%u", d) > 0;
		}
		else
		{
			success = putc(t[i], out) != EOF;
		}
	}

	// clean-up
	free(t);
	free(v);

	return success;
}


struct testcase {
	union {
		struct { size_t input, output; };
		size_t v[2];
	};
};

int load_testcases(const char *filename, struct testcase **testcases,
	size_t *testcases_count, char **testcases_data);

int parse_testcase_line(const char **line, FILE *out);

int parse_pythonstring(const char **in, FILE *out);

const char *convert_unprintable(int c, char *buf);

int xtoi(int c);

int i2xdigit(int n);

int tolower_hack(int c);

const char *strprefix_tok(const char *s, const char *prefix, int delimiter);

char *resolve_path_simple(const char *reference_path, const char *path);


int main(int argc, char *argv[])
{
	const char *const program_path = *argv;
	argc--; argv++;
	int error = 0;
	bool total_success = true;
	size_t nwords = 0;
	FILE *out;
	struct {
		const char *arg;
		struct testcase *testcases;
		char *testcases_data;
		char *result_buf;
		size_t result_buf_len;
	}
	demo = {
		(argc > 0) ? strprefix_tok(*argv, "--demo", '=') : NULL,
		NULL, NULL, NULL, 0
	};
	if (demo.arg)
	{
		argc--; argv++;
		char *testcases_path = resolve_path_simple(
			program_path, "test-cases/oops-i-blew-it-up.txt");
		error = load_testcases(testcases_path,
			&demo.testcases, &nwords, &demo.testcases_data);
		free(testcases_path);
		if (error != 0)
		{
			warnx("Couldn't load test case data: %s\n", strerror(error));
			goto cleanup;
		}
		if (*demo.arg)
		{
			nwords = min((size_t) max(atoi(demo.arg + 1), 0), nwords);
		}
		if (argc)
		{
			warnx(
				"Running in demo mode, ignoring the remaining %d command-line "
				"arguments.\n\n", argc);
		}
		out = open_memstream(&demo.result_buf, &demo.result_buf_len);
	}
	else
	{
		nwords = (size_t) max(argc, 0);
		out = stdout;
	}

	for (size_t i = 0; !error && i < nwords; i++)
	{
		if (demo.arg)
			verify_perror(fseek(out, 0, SEEK_SET) == 0);

		const char *const word = demo.arg ?
			demo.testcases_data + demo.testcases[i].input :
			argv[i];
		printf("%zu:\n%s\n", i + 1, word);

		if (!blow_up(word, out))
		{
			error = errno;
			if (!error) error = -1;
		}
		if (demo.arg)
		{
			verify_perror(fflush(out) == 0);
			fwrite(demo.result_buf,
				sizeof(*demo.result_buf), demo.result_buf_len, stdout);

			const char *const expected =
				demo.testcases_data + demo.testcases[i].output;
			const bool success =
				demo.result_buf_len == strlen(expected) &&
				memcmp(demo.result_buf, expected, demo.result_buf_len) == 0;
			total_success &= success;
			printf("\nExpected value: %s (%s)",
				expected, success ? "success" : "FAIL!");

			#ifdef _GOLFED
				assert(strlen(word) <= INT_MAX && strlen(expected) <= INT_MAX);
				fputs("\nGolfed result:  ", stdout);
				blow_up_golfed1((char*) word);
			#endif
		}

		putchar('\n');
		putchar('\n');
	}

	if (error > 0)
		warnx("%s: %s\n", "Output error", strerror(error));
	if (fclose(out) != 0)
	{
		if (!error) error = errno;
		perror("Output error");
	}

cleanup:
	free(demo.testcases);
	free(demo.testcases_data);
	free(demo.result_buf);

	return (total_success && error == 0) ? EXIT_SUCCESS : EXIT_FAILURE;
}


int load_testcases(const char *filename, struct testcase **testcases,
	size_t *testcases_count, char **testcases_data)
{
	int rv = 0;
	FILE *const f = (strcmp(filename, "-") != 0) ? fopen(filename, "r") : stdin;
	if (!f)
	{
		rv = errno;
		warn("Couldn't open \"%s\"", filename);
		return rv;
	}

	debug("testcase: Reading from \"%s\" ...\n", filename);

	*testcases_data = NULL;
	size_t bufsize = 0;
	FILE *const buf = open_memstream(testcases_data, &bufsize);

	char *linebuf = NULL;
	size_t linebuf_size = 0;

	*testcases = NULL;
	size_t testcases_bufsize = 0, tcslen = 0;
	FILE *const tcs = open_memstream((char**) testcases, &testcases_bufsize);
	struct testcase tc;

	size_t i = 0, lineno = 1;
	ssize_t linelen;

	while ((linelen = getline(&linebuf, &linebuf_size, f)) >= 0)
	{
		if (linelen > 0 && linebuf[linelen-1] == '\n')
			linebuf[--linelen] = '\0';

		if (linelen > 0)
		{
			debug("testcase:%zu: %s\n", lineno, linebuf);
			const long buf_start = ftell(buf);
			if (buf_start < 0) assert_perror(errno);

			const char *line = linebuf;
			if ((rv = parse_testcase_line(&line, buf)) != 0)
			{
				if (rv == EINVAL || rv == ERANGE)
				{
					ptrdiff_t error_offset = line - linebuf;
					verify_perror(fflush(buf) == 0);
					warnx("Error at %s:%zu:%zd: %s\n\t%s\n\t%*s^\n",
						filename, lineno, error_offset, *testcases_data + buf_start,
						linebuf, (int) min(max(error_offset, 0), INT_MAX), "");
				}
				break;
			}

			tc.v[i % 2] = (size_t) buf_start;
			if (i++ % 2)
			{
				verify_perror(fwrite(&tc, sizeof(tc), 1, tcs) == 1);
				tcslen++;
			}
		}

		lineno++;
	}

	if (rv == 0 && linelen == 0 && ferror(f))
		rv = errno;

	fclose(buf);
	fclose(tcs);

	if (rv == 0 && i % 2 != 0)
	{
		rv = EINVAL;
		if (!*linebuf) lineno--;
		warnx("Error at %s:%zu: Incomplete test case:\n\t%s\n",
			filename, lineno, *testcases_data + tc.input);
	}

	if (fclose(f) != 0)
		warn("Error while closing \"%s\"", filename);

	debug("testcase: Found %zu test cases. (rv=%d)\n", tcslen, rv);
	if (rv == 0)
	{
		*testcases_count = tcslen;
		if (tcslen)
		{
			debug("testcase 1: input=\"%1$s\" (%1$p), ouput=\"%2$s\" (%2$p)\n",
				*testcases_data + (*testcases)->input,
				*testcases_data + (*testcases)->output);
		}
	}

	free(linebuf);
	return rv;
}


#define _TESTCASE_ERRMSG_MAXLEN 50

int parse_testcase_line(const char **line, FILE *out)
{
	const char *l = strchr(*line, ':');
	if (!l)
		return EINVAL;

	while (isspace(*++l));
	*line = l;
	return *l ? parse_pythonstring(line, out) : EINVAL;
}


int parse_pythonstring(const char **in, FILE *out)
{
	static const char escape = '\\';
	static const char delimiters[] = {'\"', '\''};
	static const char escape_src[] = {'a', 'b', 't', 'n', 'v', 'f', 'r'};

	const char *s = *in;
	const long out_start = ftell(out);
	if (out_start < 0) assert_perror(errno);
	int error = 0;

	#define putc_out(c) ({ if (putc((c), out) == EOF) { error = -1; break; } })
	#define fail(err, offset, msg, ...) ({ \
		debug(msg, ##__VA_ARGS__); \
		verify_perror(fseek(out, out_start, SEEK_SET) == 0); \
		verify_perror(fprintf(out, msg, ##__VA_ARGS__) >= 0); \
		*in = s + (offset); \
		return (err); \
	})

	const int delim = *s;
	if (!memchr(delimiters, delim, sizeof(delimiters)))
	{
		fail(EINVAL, 0, "Invalid string delimiter: '%s' (%#x)",
			convert_unprintable(delim, NULL), delim);
	}

	s++;
	while (*s && *s != delim)
	{
		int c = *s++;
		if (c != escape)
		{
			putc_out(c);
			continue;
		}

		c = *s++;
		if (c == escape || memchr(delimiters, c, sizeof(delimiters)))
		{
			putc_out(c);
			continue;
		}

		const char *escape_match = memchr(escape_src, c, sizeof(escape_src));
		if (escape_match)
		{
			putc_out((int)(escape_match - escape_src + '\a'));
			continue;
		}

		if (c >= '0' && c < '8')
		{
			c -= '0';
			for (unsigned i = 0; i < 2; s++, i++)
			{
				int oct = *s - '0';
				if (oct < 0 || oct >= 8) break;
				c <<= 3;
				c |= oct;
			}
			putc_out(c);
			continue;
		}

		switch (c)
		{
		case 'x': ;
			int hi = s[0], lo = hi ? s[1] : 0;
			if (!(lo && isxdigit(hi) && isxdigit(lo)))
			{
				char cbuf[5];
				fail(EINVAL, -2, "Illegal hexadecimal escape sequence: \"\\\\%c%s%s\"",
					c, convert_unprintable(hi, NULL), convert_unprintable(lo, cbuf));
			}
			s += 2;
			putc_out((xtoi(hi) << 4) | xtoi(lo));
			break;

		case 'N':
		case 'u':
		case 'U':
		case '\n':
			fail(EINVAL, -2, "Unsupported escape sequence: \"\\\\%s\" (%#x)",
				convert_unprintable(c, NULL), c);

		case '\0':
			fail(EINVAL, -2, "Premature end of string");

		default:
			fail(EINVAL, -2, "Illegal escape sequence: \"\\\\%s\" (%#x)",
				convert_unprintable(c, NULL), c);
		}
	}

	if (!error && putc('\0', out) == EOF)
		error = -1;

	*in = s;
	return (error >= 0) ? error : errno;

	#undef putc_out
	#undef fail
}


const char *convert_unprintable(int c, char *buf)
{
	static char internal_buf[5];
	if (!buf)
		buf = internal_buf;

	if (isprint(c))
	{
		buf[0] = (char) c;
		buf[1] = '\0';
	}
	else
	{
		buf[0] = '\\';
		buf[1] = 'x';
		buf[2] = (char) i2xdigit((c >> 4) & 0xf);
		buf[3] = (char) i2xdigit(c & 0xf);
		buf[4] = '\0';
	}
	return buf;
}


int xtoi(int c)
{
	assert(isxdigit(c));
	return (c >= '0' && c <= '9') ? c - '0' : tolower_hack(c) - 'a' + 10;
}


int i2xdigit(int n)
{
	assert(n >= 0 && n < 16);
	return n + ((n < 10) ? '0' : 'a' - 10);
}


int tolower_hack(int c)
{
	assert(isalpha(c));
	return c | ('a' ^ 'A');
}


const char *strprefix_tok(const char *s, const char *prefix, int delimiter)
{
	while (*prefix && *prefix == *s)
		s++, prefix++;

	return (*prefix || (*s && *s != delimiter)) ? NULL : s;
}


char *resolve_path_simple(const char *reference_path, const char *path)
{
	const size_t reference_path_len = strlen(reference_path);
	const char *const last_component =
		memrchr(reference_path, '/', reference_path_len);
	const size_t
		base_len = last_component ?
			(size_t)(last_component - reference_path + 1) : reference_path_len,
		path_len = strlen(path);
	char *const rp = malloc(base_len + path_len + 1);
	memcpy(rp, reference_path, base_len);
	memcpy(rp + base_len, path, path_len);
	rp[base_len + path_len] = '\0';
	return rp;
}
