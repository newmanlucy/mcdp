from contracts.utils import indent


def pretty_print_dict(d):
    lengths = [len(k) for k in d.keys()]
    if not lengths:
        return 'Empty.'
    klen = max(lengths)
    s = []
    for k, v in d.items():
        if isinstance(k, tuple):
            k = k.__repr__()
        k2 = k.rjust(klen)
        prefix = "%s: " % k2
        s.append(indent(str(v), '', prefix))
    return "\n".join(s)
        
def pretty_print_dict_newlines(d):
    lengths = [len(k) for k in d.keys()]
    if not lengths:
        return 'Empty.'

    s = ""
    for k, v in d.items():
        if isinstance(k, tuple):
            k = k.__repr__()
        if s:
            s += '\n\n'
        s +=  k
        s += '\n\n' + indent(str(v), '  ') 
    return s