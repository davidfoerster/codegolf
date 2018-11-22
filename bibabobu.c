// See https://codegolf.stackexchange.com/q/171395

#if _POSIX_C_SOURCE < 200809L && _XOPEN_SOURCE < 700
#define _POSIX_C_SOURCE 200809L
#endif

#include <stddef.h>
#include <stdbool.h>
#include <sys/types.h>
#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <err.h>
#include <sysexits.h>
#include <assert.h>


#define UNUSED(expr) ((void)sizeof(expr))

#ifdef NDEBUG
#undef assert
#define assert(expr) UNUSED(expr)
#endif


#define between(x, min, max) ({ \
		const __typeof__(x) __x = (x); \
		(min) < __x && __x <= (max); \
	})


static int decode_vowel(int c)
{
	static const char VOWELS[] = {'I', 'A', 'O', 'U'};
	const char *v = memchr(VOWELS, c, sizeof(VOWELS));
	return v ? (int)(v - VOWELS) : -1;
}


static ssize_t bibabobu_decode(const char *s, FILE *out, const char **remainder)
{
	const char *const start = s;
	int nibble = -1, high_nibble = -1;
	size_t nibble_count = 0;

	for (; s[0]; s += 2)
	{
		switch (s[0])
		{
		case 'B':
			nibble = decode_vowel(s[1]);
			break;

		case 'D':
			nibble = ((nibble + 1) << 2) | decode_vowel(s[1]);
			break;

		default:
			goto input_error;
		}

		if (nibble < 0)
			goto input_error;

		if (!s[2] || s[2] == 'B')
		{
			if (++nibble_count % 2)
			{
				high_nibble = nibble;
			}
			else
			{
				if (putc(nibble | (high_nibble << 4), out) == EOF)
					goto output_error;
			}
		}
		else if (s[0] == 'D' && s[2] == 'D')
		{
			s += 2;
			goto input_error;
		}
	}

	ssize_t result = s - start;
	goto end;

input_error:
	errno = EINVAL;

output_error:
	result = -1;

end:
	if (remainder)
		*remainder = s;

	return result;
}


static int each_line(FILE *stream, bool (*callback)(char*, size_t, void*),
	void *callback_data)
{
	char *buf = NULL;
	size_t bufsize = 0;
	ssize_t length;

	while ((length = getline(&buf, &bufsize, stream)) >= 0)
	{
		if (length > 0 && buf[length - 1] == '\n')
			buf[--length] = '\0';

		if (!(*callback)(buf, (size_t) length, callback_data))
			break;
	}

	free(buf);
	return (length >= 0) ? 1 : ferror(stream) ? -1 : 0;
}


struct main_state
{
	size_t count;
	FILE *stream;
	const char *error_remainder;
	size_t error_position;
};


static bool main_inner(char *arg, size_t arglen, void *vstate)
{
	struct main_state *const state = vstate;

	if (state->count++ > 0)
		putc('\n', state->stream);

	fprintf(state->stream, "Input %1$zu: %2$s\nOutput %1$zu: ",
		state->count, arg);
	#ifndef NDEBUG
		state->error_remainder = NULL;
	#endif
	ssize_t rv = bibabobu_decode(arg, state->stream, &state->error_remainder);
	putc('\n', state->stream);

	if (rv < 0)
	{
		assert(between(state->error_remainder, arg, arg + arglen));
		state->error_position = (size_t)(state->error_remainder - arg);
	}

	return rv >= 0;
}


int main(int argc, char *argv[])
{
	int rv;
	struct main_state state;
	state.count = 0;
	state.stream = stdout;

	if (argc > 1)
	{
		rv = 0;
		for (int i = 1; i < argc; i++)
		{
			if (!main_inner(argv[i], 0, &state))
			{
				rv = 1;
				break;
			}
		}
	}
	else
	{
		rv = each_line(stdin, &main_inner, &state);
	}

	if (rv > 0)
	{
		fflush(state.stream);
		warnx("Error at %zu:%zu: '%.4s'", state.count, state.error_position, state.error_remainder);
		return EX_DATAERR;
	}
	if (rv < 0)
	{
		fflush(state.stream);
		warn("Input stream error at %zu", state.count);
		return EX_IOERR;
	}
}
