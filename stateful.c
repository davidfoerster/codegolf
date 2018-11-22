#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif

#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <strings.h>
#include <limits.h>
#include <errno.h>
#include <err.h>
#include <unistd.h>
#include <fcntl.h>
#include <sys/stat.h>
#include <sys/sendfile.h>
#include <sysexits.h>
#include <assert.h>


#define warn_r(rv, fmt, ...) \
	({ warn((fmt) __VA_OPT__(,) __VA_ARGS__); return (rv); })

static int main_store(const char *fn);

static int main_load(const char *fn);

static ssize_t copy_fd(int in_fd, int out_fd, size_t count);

static ssize_t sendfile_wrapper(int in_fd, int out_fd, size_t count);

static ssize_t splice_wrapper(int in_fd, int out_fd, size_t count);


#define _check_op(arg, name) (strcasecmp((arg), #name) == 0) ? &(main_ ## name)

int main(int argc, char *argv[])
{
	if (argc >= 2)
	{
		typedef int (*program_op_t)(const char*);
		const program_op_t program_op =
			_check_op(argv[1], store) :
			_check_op(argv[1], load) :
				NULL;
		if (program_op)
			return (*program_op)((argc >= 3) ? argv[2] : "f");
	}
	return EX_USAGE;
}


int main_store(const char *fn)
{
	const int fd = creat(fn, 0666);
	if (fd == -1)
		warn_r(EX_CANTCREAT, "Cannot open or create \"%s\" for writing", fn);

	if (copy_fd(STDIN_FILENO, fd, SSIZE_MAX) < 0)
		warn_r(EX_IOERR, "I/O error while copying from STDIN to \"%s\"", fn);

	if (close(fd) != 0)
		warn_r(EX_IOERR, "Error closing \"%s\"", fn);
	if (close(STDIN_FILENO) != 0)
		warn_r(EX_IOERR, "Error closing STDIN");

	return EX_OK;
}


int main_load(const char *fn)
{
	const int fd = open(fn, O_RDONLY);
	if (fd == -1)
		warn_r(EX_NOINPUT, "Cannot open \"%s\" for reading", fn);

	if (copy_fd(fd, STDOUT_FILENO, SSIZE_MAX) < 0)
		warn_r(EX_IOERR, "I/O error while copying from \"%s\" to STDOUT", fn);

	if (close(STDOUT_FILENO) != 0)
		warn_r(EX_IOERR, "Error closing STDOUT");
	if (close(fd) != 0)
		warn_r(EX_IOERR, "Error closing \"%s\"", fn);

	return EX_OK;
}


ssize_t copy_fd(int in_fd, int out_fd, size_t count)
{
	struct stat in_stat;
	if (fstat(in_fd, &in_stat) != 0)
		return -1;

	typedef ssize_t (*copy_op_t)(int, int, size_t);
	const copy_op_t copy_op =
		(S_ISREG(in_stat.st_mode) || S_ISBLK(in_stat.st_mode)) ?
			&sendfile_wrapper : &splice_wrapper;
	size_t copied_count = 0;
	ssize_t rv = 0;
	while (copied_count < count &&
		(rv = (*copy_op)(in_fd, out_fd, count - copied_count)) > 0)
	{
		assert(copied_count <= SIZE_MAX - (size_t) rv);
		copied_count += (size_t) rv;
	}

	if (rv < 0)
	{
		int errnum = errno;
		char buf;
		rv = read(in_fd, &buf, sizeof(buf));
		if (rv != 0)
		{
			if (rv > 0)
				errno = errnum;
			return -1;
		}
	}

	assert(copied_count <= SSIZE_MAX);
	return (ssize_t) copied_count;
}


ssize_t sendfile_wrapper(int in_fd, int out_fd, size_t count)
{
	return sendfile(out_fd, in_fd, NULL, count);
}


ssize_t splice_wrapper(int in_fd, int out_fd, size_t count)
{
	return splice(in_fd, NULL, out_fd, NULL, count, 0);
}
