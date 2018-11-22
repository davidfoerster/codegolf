/*
 * LeetCode challenge 387: First Unique Character in a String
 * https://leetcode.com/problems/first-unique-character-in-a-string/description/
 */
#include <stdint.h>
#include <stdio.h>
#include <assert.h>


const char *firstUniqChar(const char *s)
{
	uint_fast32_t occurrence[2] = {};

	for (const char *p = s; *p; p++)
	{
		assert(*p >= 'a' && *p <= 'z');
		uint_fast32_t mask = (uint_fast32_t) 1 << (*p - 'a');
		occurrence[1] |= occurrence[0] & mask;
		occurrence[0] |= mask;
	}

	for (const char *p = s; *p; p++)
	{
		if (!(occurrence[1] & ((uint_fast32_t) 1 << (*p - 'a'))))
			return p;
	}

	return NULL;
}


int main(int argc, char *argv[])
{
	for (int i = 1; i < argc; i++)
	{
		const char *s = argv[i], *p = firstUniqChar(s);
		printf("%d: %s => %td\n", i, s, p ? p - s : -1);
	}
}
