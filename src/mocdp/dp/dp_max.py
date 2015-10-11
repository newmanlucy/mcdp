# -*- coding: utf-8 -*-
from .primitive import PrimitiveDP
from mocdp import get_conftools_posets
from mocdp.posets import PosetProduct


__all__ = [
    'Max',
    'Min',
]

class Max(PrimitiveDP):
    """ Join on a poset """

    def __init__(self, F):
        library = get_conftools_posets()
        _, F0 = library.instance_smarter(F)

        F = PosetProduct((F0, F0))
        R = F0
        self.F0 = F0

        PrimitiveDP.__init__(self, F=F, R=R)

    def solve(self, func):
        f1, f2 = func

        r = self.F0.join(f1, f2)

        return self.R.U(r)

    def __repr__(self):
        return 'Max(%r)' % self.F0


class Min(PrimitiveDP):
    """ Meet on a poset """

    def __init__(self, F):
        library = get_conftools_posets()
        _, F0 = library.instance_smarter(F)

        F = PosetProduct((F0, F0))
        R = F0
        self.F0 = F0

        PrimitiveDP.__init__(self, F=F, R=R)

    def solve(self, func):
        f1, f2 = func

        r = self.F0.meet(f1, f2)

        return self.R.U(r)

    def __repr__(self):
        return 'Min(%r)' % self.F0



