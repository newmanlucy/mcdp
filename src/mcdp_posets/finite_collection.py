# -*- coding: utf-8 -*-
from contracts import contract
from mcdp.development import do_extra_checks

from .space import NotBelongs, Space


__all__ = [
    'FiniteCollection',
]

class FiniteCollection(object):
    """ This is used as a value, whose Space is FinitecollectionsInclusion """
    
    @contract(elements='set|list', S=Space)
    def __init__(self, elements, S):
        self.elements = frozenset(elements)
        self.S = S

        if do_extra_checks():
            # XXX
            problems = []
            for m in elements:
                try:
                    self.S.belongs(m)
                except NotBelongs as e:
                    problems.append(e)
            if problems:
                msg = "Cannot create finite collection:\n"
                msg += "\n".join(str(p) for p in problems)
                raise NotBelongs(msg)

    def __repr__(self):  # ≤  ≥
        contents = ", ".join(self.S.format(m)
                        for m in sorted(self.elements))

        return "{%s}" % contents
