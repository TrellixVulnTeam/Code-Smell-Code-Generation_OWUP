def about_time(fn=None, it=None):
    """Measures the execution time of a block of code, and even counts iterations
    and the throughput of them, always with a beautiful "human" representation.

    There's three modes of operation: context manager, callable handler and
    iterator metrics.

    1. Use it like a context manager:

    >>> with about_time() as t_whole:
    ....    with about_time() as t_1:
    ....        func_1()
    ....    with about_time() as t_2:
    ....        func_2('params')

    >>> print(f'func_1 time: {t_1.duration_human}')
    >>> print(f'func_2 time: {t_2.duration_human}')
    >>> print(f'total time: {t_whole.duration_human}')

    The actual duration in seconds is available in:
    >>> secs = t_whole.duration

    2. You can also use it like a callable handler:

    >>> t_1 = about_time(func_1)
    >>> t_2 = about_time(lambda: func_2('params'))

    Use the field `result` to get the outcome of the function.

    Or you mix and match both:

    >>> with about_time() as t_whole:
    ....    t_1 = about_time(func_1)
    ....    t_2 = about_time(lambda: func_2('params'))

    3. And you can count and, since we have duration, also measure the throughput
    of an iterator block, specially useful in generators, which do not have length,
    but you can use with any iterables:

    >>> def callback(t_func):
    ....    logger.info('func: size=%d throughput=%s', t_func.count,
    ....                                               t_func.throughput_human)
    >>> items = filter(...)
    >>> for item in about_time(callback, items):
    ....    # use item any way you want.
    ....    pass
    """

    # has to be here to be mockable.
    if sys.version_info >= (3, 3):
        timer = time.perf_counter
    else:  # pragma: no cover
        timer = time.time

    @contextmanager
    def context():
        timings[0] = timer()
        yield handle
        timings[1] = timer()

    timings = [0.0, 0.0]
    handle = Handle(timings)

    if it is None:
        # use as context manager.
        if fn is None:
            return context()

        # use as callable handler.
        with context():
            result = fn()
        return HandleResult(timings, result)

    # use as counter/throughput iterator.
    if fn is None or not callable(fn):  # handles inversion of parameters.
        raise UserWarning('use as about_time(callback, iterable) in counter/throughput mode.')

    def counter():
        i = -1
        with context():
            for i, elem in enumerate(it):
                yield elem
        fn(HandleStats(timings, i + 1))

    return counter()