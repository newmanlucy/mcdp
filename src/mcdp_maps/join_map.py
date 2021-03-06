# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_wrapped
from mcdp_posets import Map, Poset, PosetProduct, NotJoinable, MapNotDefinedHere
from mcdp_maps.repr_map import repr_map_joinn


__all__ = [
    'JoinNMap',
]


class JoinNMap(Map):
    """ 
        A map that computes the join of n arguments. 
    
        ⟨x₁, …, xₙ⟩ ⟼ max(x₁, …, xₙ⟩
    
        Raises MapNotDefinedHere if the elements are not joinable.
        
    """

    @contract(n='int,>=1', P=Poset)
    def __init__(self, n, P):
        dom = PosetProduct((P,) * n)
        cod = P
        Map.__init__(self, dom, cod)
        self.P = P
        self.n = n

    def _call(self, xs):
        assert len(xs) == self.n
        try:
            res = xs[0]
            for x in xs[1:]:
                res = self.P.join(res, x)
            return res
        except NotJoinable as e:
            msg = 'Cannot join all elements.'
            raise_wrapped(MapNotDefinedHere, e, msg, res=res, x=x) 


    def repr_map(self, letter):
        return repr_map_joinn(letter, len(self.dom))
    