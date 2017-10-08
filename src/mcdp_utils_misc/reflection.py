
def accepts_arg(f, name):
    """ True if the function f supports the "name" argument """
    import inspect
    args = inspect.getargspec(f)
    return name in args.args