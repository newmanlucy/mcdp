# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import raise_desc, raise_wrapped, check_isinstance
from mcdp.exceptions import DPInternalError, mcdp_dev_warning

from .nat import Int, Nat
from .poset import NotLeq, Preorder
from .poset_coproduct import PosetCoproduct
from .poset_product import PosetProduct
from .rcomp import Rcomp
from .rcomp_units import RbicompUnits
from .space import Map, MapNotDefinedHere, NotEqual
from .space_product import SpaceProduct
from .uppersets import UpperSets, LowerSets



__all__ = [
    'get_types_universe',
    'express_value_in_isomorphic_space',
]


class TypesUniverse(Preorder):
    """
        In this pre-order, a type A <= B if we can find 
        and embedding of A in B. An embedding is a pair of functions
        f: A -> B and g: B -> A such that g(f(x)) = x.
        
        For example,  int <= float, and embedding = (float(), int())
    
    """

    def witness(self):
        return Nat()

    def belongs(self, x):
        from mcdp_posets.space import Space
        return isinstance(x, Space)

    def check_equal(self, A, B):
        if isinstance(A, PosetProduct) and isinstance(B, PosetProduct):
            if len(A) != len(B):
                msg = 'Different length.'
                raise_desc(NotEqual, msg, A=A, B=B)
            for i, (sa, sb) in enumerate(zip(A.subs, B.subs)):
                try:
                    self.check_equal(sa, sb)
                except NotEqual as e:
                    msg = 'Element %d not equal.' % i
                    raise_wrapped(NotEqual, e, msg, compact=True)

        if isinstance(A, UpperSets) and isinstance(B, UpperSets):
            try:
                self.check_equal(A.P, B.P)
                return
            except NotEqual as e:
                msg = 'Spaces do not match'
                raise_wrapped(NotEqual, e, msg, compact=True,
                              A=A.P, B=B.P)

        if isinstance(A, LowerSets) and isinstance(B, LowerSets):
            try:
                self.check_equal(A.P, B.P)
                return
            except NotEqual as e:
                msg = 'Spaces do not match'
                raise_wrapped(NotEqual, e, msg, compact=True,
                              A=A.P, B=B.P)

        
        mcdp_dev_warning('many things to do here...')
        
        if not(A == B):
            msg = 'Different by direct comparison.'
            raise_desc(NotEqual, msg, A=A, B=B)

    def check_leq(self, A, B):
        from mcdp_posets.space import Space
        from mcdp_posets import FiniteCollectionsInclusion
        from mcdp_posets import RcompUnits
        from mcdp_posets import R_dimensionless

        check_isinstance(A, Space)
        check_isinstance(B, Space)
        
        if A == B:
            return
        
        if isinstance(A, Nat) and isinstance(B, Nat):
            return

        if isinstance(A, Nat) and isinstance(B, Int):
            return

        if isinstance(A, Int) and isinstance(B, Int):
            return
        
        # Natural numbers can be embdedded into reals
        # (well, not all natural numbers, not biglongs, but close enough)
#         if isinstance(A, Nat) and isinstance(B, RcompUnits):
#             return

        if isinstance(A, Nat) and isinstance(B, Rcomp):
            return
        
#         print 'isinstance(A, Nat)', isinstance(A, Nat)
#         print 'isinstance(B, Rcomp)', isinstance(B, Rcomp), type(B), B.__repr__()

        if isinstance(A, Nat) and isinstance(B, RcompUnits):
            if R_dimensionless.units.dimensionality == B.units.dimensionality:  # @UndefinedVariable
                return

        if isinstance(A, RcompUnits) and isinstance(B, RbicompUnits):
            if A.units.dimensionality == B.units.dimensionality:
                return
            else:
                msg = "Dimensionality do not match."
                raise_desc(NotLeq, msg,
                           A_dimensionality=A.units.dimensionality,
                           B_dimensionality=B.units.dimensionality)

        if isinstance(A, FiniteCollectionsInclusion) and isinstance(B, FiniteCollectionsInclusion):
            self.check_leq(A.S, B.S)
            return
        
        if isinstance(A, RcompUnits) and isinstance(B, RcompUnits):
            if A.units.dimensionality == B.units.dimensionality:
                return
            else:
                msg = "Dimensionality do not match."
                raise_desc(NotLeq, msg,
                           A_dimensionality=A.units.dimensionality,
                           B_dimensionality=B.units.dimensionality)

        if isinstance(A, Rcomp) and isinstance(B, RcompUnits):
            if R_dimensionless.units.dimensionality == B.units.dimensionality:  # @UndefinedVariable
                return

        if isinstance(B, Rcomp) and isinstance(A, RcompUnits):
            if R_dimensionless.units.dimensionality == A.units.dimensionality:  # @UndefinedVariable
                return

        if isinstance(A, UpperSets) and isinstance(B, UpperSets):
            self.check_leq(A.P, B.P)
            return
        
        if isinstance(A, LowerSets) and isinstance(B, LowerSets):
            self.check_leq(A.P, B.P)
            return
        
        if isinstance(A, SpaceProduct) and isinstance(B, SpaceProduct):
            return check_leq_products(self, A, B)

        from mcdp_posets import FinitePoset
        if isinstance(A, FinitePoset) and isinstance(B, FinitePoset):
            # A <= B if
            # TODO: check inclusion
            mcdp_dev_warning('XXX check relations')
            SB = set(B.get_elements())
            SA = set(A.get_elements())
            if not SA.issubset(SB):
                msg = 'The posets do not have the same elements '
                raise_desc(NotLeq, msg, SA=SA, SB=SB)
            return
        
        if isinstance(A, PosetCoproduct) and isinstance(B, PosetCoproduct):
            # if all the subs are equal then it's fine
            if len(A.spaces) == len(B.spaces):
                try:
                    for sa, sb in zip(A.spaces, B.spaces):
                        self.check_leq(sa, sb)
                except NotLeq:
                    pass
                else:
                    # OK, they are
                    return
            mcdp_dev_warning('Not implemented the case where the order is different')
        
        if isinstance(B, PosetCoproduct):
            # A <= PosetCoproduct((b1,...,bn)) if there exists bn: A <= bn
            for x in B.spaces:
                try:
                    self.check_leq(A, x)
                    return
                except:
                    pass


        msg = "Do not know how to compare types."
        raise_desc(NotLeq, msg, A=A, B=B)
            
    def get_super_conversion(self, A, B):
        """ 
            Returns a pair of maps (f,g), 
        
                f : A ⟶ B,
                g : B ⟶ A,
        
            such that:
            
                f(a) = min { b ∈ B: a ≼ b }
                g(b) = max { a ∈ A: a ≼ b }
                
            These two maps then can be used as a pair (h, h*)
            to create a DP to be used as a "conversion" between
            the two spaces.
            
            Raises NotLeq if it is not possible to create this 
            pair of functions (either because the space are 
            not comparable or because the implementation is not available). 
        """
        from .rcomp_units import RcompUnits
        from .maps.coerce_to_int import FloorRNMap, CeilRNMap
        from .maps.promote_to_float import PromoteToFloat
        from mcdp_posets.rcomp_units import R_dimensionless
        
        if self.leq(A, B) and self.leq(B, A):
            h, hd = tu.get_embedding(A, B)
            assert A == h.get_domain()
            assert B == h.get_codomain()
            assert A == hd.get_codomain()
            assert B == hd.get_domain()
            return h, hd
    
        if isinstance(A, Nat) and isinstance(B, Rcomp):
            # Nat ⟶ Reals
            # h  = PromoteToFloat
            # h *= Floor
            h = PromoteToFloat(A, B)
            hd = FloorRNMap(B, A)
            assert A == h.get_domain()
            assert B == h.get_codomain()
            assert A == hd.get_codomain()
            assert B == hd.get_domain()
            return h, hd
        
        if isinstance(A, Nat) and isinstance(B, RcompUnits):
            if R_dimensionless.units.dimensionality == B.units.dimensionality:  # @UndefinedVariable
                h = PromoteToFloat(A, B)
                hd = FloorRNMap(B, A)
                assert A == h.get_domain()
                assert B == h.get_codomain()
                assert A == hd.get_codomain()
                assert B == hd.get_domain()
                return h, hd
        
        if isinstance(A, Rcomp) and isinstance(B, Nat):
            # Reals -> Nat 
            # h = Ceil
            # h* = PromoteToFloat
            h = CeilRNMap(A, B)
            hd = PromoteToFloat(B, A) 
            return h, hd       

        if isinstance(A, RcompUnits) and isinstance(B, Nat):
            if R_dimensionless.units.dimensionality == A.units.dimensionality:  # @UndefinedVariable
                # Reals -> Nat 
                # h = Ceil
                # h* = PromoteToFloat
                h = CeilRNMap(A, B)
                hd = PromoteToFloat(B, A) 
                return h, hd       

        # case when A = Coproduct(... + B + ...) 
        if isinstance(A, PosetCoproduct):
            for i, Ai in enumerate(A.spaces):
                if self.equal(B, Ai):
                    hd, h = get_coproduct_embedding(B, A, i)
                    assert A == h.get_domain()
                    assert B == h.get_codomain()
                    assert A == hd.get_codomain()
                    assert B == hd.get_domain()
                    return h, hd
                
        # case when B = Coproduct(... + A + ...) 
        if isinstance(B, PosetCoproduct):
            for i, Bi in enumerate(B.spaces):
                if self.equal(A, Bi):
                    h, hd = get_coproduct_embedding(A, B, i)
                    assert A == h.get_domain()
                    assert B == h.get_codomain()
                    assert A == hd.get_codomain()
                    assert B == hd.get_domain()
                    return h, hd
                 
        msg = 'Super conversion not available.'
        raise_desc(NotLeq, msg, A=A, B=B)
             
    def get_embedding(self, A, B):
        try:
            self.check_leq(A, B)
        except NotLeq as e:
            msg = 'Cannot get embedding if preorder does not hold.'
            raise_wrapped(DPInternalError, e, msg, compact=True)

        from mcdp_posets import RcompUnits
        from mcdp_posets import format_pint_unit_short
        from mcdp_posets.maps.identity import IdentityMap
        from mcdp_maps.map_composition import MapComposition
        from .maps.linearmapcomp import LinearMapComp
           
        if isinstance(A, Nat) and isinstance(B, (Rcomp, RcompUnits)):
            from .maps.coerce_to_int import CoerceToInt
            from .maps.promote_to_float import PromoteToFloat
            return PromoteToFloat(A, B), CoerceToInt(B, A)

        if isinstance(A, Nat) and isinstance(B, Int):
            return IdentityMap(A, B), IdentityMap(B, A)
            
        if isinstance(A, RcompUnits) and isinstance(B, RbicompUnits):
            assert A.units.dimensionality == B.units.dimensionality
            
            factor = float(B.units / A.units)
            A_to_B = MapComposition((LinearMapComp(A, A, 1.0 / factor),
                                     IdentityMap(A, B)))
            B_to_A = MapComposition((CheckNonnegativeMap(B, A), 
                                     LinearMapComp(A, A, factor)))
            
            a = format_pint_unit_short(A.units)
            b = format_pint_unit_short(B.units)
            setattr(B_to_A, '__name__', '%s*-to-%s' % (b, a))
            setattr(A_to_B, '__name__', '%s-to-%s*' % (a, b))
            return A_to_B, B_to_A
                
        if isinstance(A, RcompUnits) and isinstance(B, RcompUnits):
            assert A.units.dimensionality == B.units.dimensionality

            factor = float(B.units / A.units)
            B_to_A = LinearMapComp(B, A, factor)
            A_to_B = LinearMapComp(A, B, 1.0 / factor)

            a = format_pint_unit_short(A.units)
            b = format_pint_unit_short(B.units)
            setattr(B_to_A, '__name__', '%s-to-%s' % (b, a))
            setattr(A_to_B, '__name__', '%s-to-%s' % (a, b))
            return A_to_B, B_to_A

        if self.equal(A, B):
            return IdentityMap(A, B), IdentityMap(B, A)

        if isinstance(A, Rcomp) and isinstance(B, RcompUnits):
            return IdentityMap(A, B), IdentityMap(B, A)

        if isinstance(B, Rcomp) and isinstance(A, RcompUnits):
            return IdentityMap(A, B), IdentityMap(B, A)

        if isinstance(A, PosetProduct) and isinstance(B, PosetProduct):
            return get_poset_product_embedding(self, A, B)

        if isinstance(A, SpaceProduct) and isinstance(B, SpaceProduct):
            return get_space_product_embedding(self, A, B)

        if isinstance(A, UpperSets) and isinstance(B, UpperSets):
            P_A_to_B, P_B_to_A = self.get_embedding(A.P, B.P)
            from .maps.lift_to_uppersets import LiftToUpperSets
            m1 = LiftToUpperSets(P_A_to_B)
            m2 = LiftToUpperSets(P_B_to_A)
            setattr(m1, '__name__', 'L%s' % P_A_to_B.__name__)
            setattr(m1, '__name__', 'L%s' % P_B_to_A.__name__)
            return m1, m2

        from mcdp_posets import FiniteCollectionsInclusion
        if (isinstance(A, FiniteCollectionsInclusion) and
            isinstance(B, FiniteCollectionsInclusion)):
            a_to_b, b_to_a = self.get_embedding(A.S, B.S)
            from mcdp_posets.maps.lift_to_finitecollections import LiftToFiniteCollections
            m1 = LiftToFiniteCollections(a_to_b)
            m2 = LiftToFiniteCollections(b_to_a)
            setattr(m1, '__name__', 'L%s' % a_to_b.__name__)
            setattr(m1, '__name__', 'L%s' % b_to_a.__name__)
            return m1, m2

        if isinstance(B, PosetCoproduct):
            for i, x in enumerate(B.spaces):
                try:
                    self.check_leq(A, x)
                    return get_coproduct_embedding(A, B, i)
                except NotLeq:
                    pass

        if True: # pragma: no cover
            msg = 'Spaces are ordered, but you forgot to code embedding.'
            raise_desc(NotImplementedError, msg, A=A, B=B)

class CheckNonnegativeMap(Map):
    def __init__(self, dom, cod):
        Map.__init__(self, dom, cod)
    
    def _call(self, x):
        if not self.dom.leq(0.0, x):
            raise MapNotDefinedHere()
        return x
    
    def repr_map(self, letter):
        return '%s ⟼ %s' % (letter, letter)

@contract(B=PosetCoproduct)
def get_coproduct_embedding(A, B, i):
    # assume that A <= B.spaces[i]
    A_to_B = Coprod_A_to_B_map(A=A, B=B, i=i)
    B_to_A = Coprod_B_to_A_map(A=A, B=B, i=i)
    return A_to_B, B_to_A


class Coprod_A_to_B_map(Map):
    
    @contract(B=PosetCoproduct, i='int')
    def __init__(self, A, B, i):
        check_isinstance(B, PosetCoproduct)
        if i >= len(B.spaces):
            msg = 'Invalid index.'
            raise_desc(ValueError, msg, A, B, i) 

        dom = A
        cod = B
        self.B = B
        self.i = i 
        Map.__init__(self, dom=dom, cod=cod)
    
    def _call(self, a):
        b = self.B.pack(self.i, a)
        return b
    
    def repr_map(self, letter):
        return '%s ⟼ ⟨%s, %s⟩' % (letter, self.i, letter)


class Coprod_B_to_A_map(Map):
    
    @contract(B=PosetCoproduct, i='int')
    def __init__(self, A, B, i):
        check_isinstance(B, PosetCoproduct)
        if i >= len(B.spaces):
            msg = 'Invalid index.'
            raise_desc(ValueError, msg, A, B, i) 
        dom = B
        cod = A
        self.B = B
        self.A = A
        self.i = i
        Map.__init__(self, dom=dom, cod=cod)
    
    def _call(self, b):
        j, a = self.B.unpack(b)
        if j != self.i:
            msg = 'Cannot convert element %s (in %s) to %s.' % (b, self.B, self.A)
            raise_desc(MapNotDefinedHere, msg, j=j, i=self.i, b=b, a=a)
        return a
    
    def repr_map(self, letter):
        return '⟨%s, %s⟩ ⟼ %s' % (self.i, letter, letter)



def express_value_in_isomorphic_space(S1, s1, S2):
    """ 
        expresses s1 in S2 

        assumes S1 <= S2 
    """
    tu.check_leq(S1, S2)    
    
    A_to_B, _ = tu.get_embedding(S1, S2)
    return A_to_B(s1)



def get_space_product_embedding(tu, A, B):
    pairs = [tu.get_embedding(a, b) for a, b in zip(A, B)]
    fs = [x for x, _ in pairs]
    finv = [y for _, y in pairs]


    from mcdp_posets.maps.product_map import SpaceProductMap
    res = SpaceProductMap(fs), SpaceProductMap(finv)
    return res


def get_poset_product_embedding(tu, A, B):
    pairs = [tu.get_embedding(a, b) for a, b in zip(A, B)]
    fs = tuple([x for x, _ in pairs])
    finv = tuple([y for _, y in pairs])

    from mcdp_posets.maps.product_map import PosetProductMap
    res = PosetProductMap(fs), PosetProductMap(finv)
    return res


def check_leq_products(tu, A, B):
    if len(A) != len(B):
        msg = 'Different length.'
        raise_desc(NotLeq, msg, A=A, B=B)
    for a, b in zip(A, B):
        try:
            tu.check_leq(a, b)
        except NotLeq as e:
            msg = 'Found uncomparable elements.'
            raise_wrapped(NotLeq, e, msg, compact=True, a=a, b=b)


tu = TypesUniverse()

def get_types_universe():
    return tu
