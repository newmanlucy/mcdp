# -*- coding: utf-8 -*-
from contracts import contract
from contracts.utils import check_isinstance
from mcdp_posets import (Map, RcompUnits, Nat,
    express_value_in_isomorphic_space, Rcomp, is_top)
from mcdp_posets.nat import Nat_add
from mcdp_posets.rcomp_units import rcomp_add, rcompunits_add
from mcdp_posets.space import MapNotDefinedHere


__all__ = [
    'PlusValueMap',
    'PlusValueRcompMap',
    'PlusValueNatMap',
    
    'PlusValueDualMap', 
    'PlusValueDualRcompMap', 
    'PlusValueDualNatMap',
    
    'MinusValueMap',
    'MinusValueRcompMap',
    'MinusValueNatMap',
]


class PlusValueMap(Map):
    """ 
        Implements _ -> _ + c  for RcompUnits
    
    """
    @contract(P=RcompUnits, c_space=RcompUnits)
    def __init__(self, P, c_value, c_space):
        c_space.belongs(c_value)
        check_isinstance(P, RcompUnits)
        check_isinstance(c_space, RcompUnits)
        Map.__init__(self, dom=P, cod=P)
        self.c_value = c_value
        self.c_space = c_space
        self.c = express_value_in_isomorphic_space(c_space, c_value, P)

    def __repr__(self):
        return "+ %s" % self.c_space.format(self.c_value)

    def _call(self, x):
        return rcompunits_add(self.dom, x, self.c) 

class PlusValueDualMap(Map):
    """ 
        Implements the dual for PlusValueMap.
        
        This is not MinusValueMap.
        
        This is:
        
        h* : x |->
        
          if c = Top:
              if x = Top:
                  return {Top}
              else:
                  return EmptySet
          if c < Top:
              if c <= x:
                  return x - c
              else:
                  return EmptySet
          
    """

    def __init__(self, P, c_value, c_space):
        dom = cod = P
        c_space.belongs(c_value)

        check_isinstance(P, RcompUnits)
        check_isinstance(c_space, RcompUnits)
        
        self.c = express_value_in_isomorphic_space(c_space, c_value, dom)
        
        Map.__init__(self, dom, cod)
        self.c_value = c_value
        self.c_space = c_space
        
    def __repr__(self):
        return "Dual(+ %s)" % self.c_space.format(self.c_value)

    def _call(self, x): 
        if is_top(self.dom, self.c):
            if is_top(self.dom, x):
                return self.dom.get_top()
            else:
                raise MapNotDefinedHere()
        else:
            if self.dom.leq(self.c, x):
                if is_top(self.dom, x):
                    return self.dom.get_top()
                assert isinstance(self.c, float)
                assert isinstance(x, float), x
                return x - self.c
            else:
                raise MapNotDefinedHere()
    
    
class PlusValueDualRcompMap(Map):

    def __init__(self, c):
        cod = dom = Rcomp()
        dom.belongs(c)
        self.c = c
        Map.__init__(self, dom, cod)
        
    def __repr__(self):
        return "Dual(+ %s)" % self.dom.format(self.c)

    def _call(self, x): 
        if is_top(self.dom, self.c):
            if is_top(self.dom, x):
                return self.dom.get_top()
            else:
                raise MapNotDefinedHere()
        else:
            if self.dom.leq(self.c, x):
                if is_top(self.dom, x):
                    return self.dom.get_top()
                
                assert isinstance(self.c, float)
                assert isinstance(x, float)
                return x - self.c
            else:
                raise MapNotDefinedHere()


    
class PlusValueDualNatMap(Map):

    def __init__(self, c):
        cod = dom = Nat()
        dom.belongs(c)
        self.c = c
        Map.__init__(self, dom, cod)
        
    def __repr__(self):
        return "Dual(+ %s)" % self.dom.format(self.c)

    def _call(self, x): 
        if is_top(self.dom, self.c):
            if is_top(self.dom, x):
                return self.dom.get_top()
            else:
                raise MapNotDefinedHere()
        else:
            if self.dom.leq(self.c, x):
                if is_top(self.dom, x):
                    return self.dom.get_top()
                
                assert isinstance(self.c, int)
                assert isinstance(x, int)
                return x - self.c
            else:
                raise MapNotDefinedHere()
            
            
class PlusValueRcompMap(Map):
    """ 
        Implements _ -> _ + c  for Rcomp.    
    """

    def __init__(self, c_value):
        dom = Rcomp()
        dom.belongs(c_value)
        cod = dom
        Map.__init__(self, dom=dom, cod=cod)
        self.c_value = c_value

    def __repr__(self):
        return "+ %s" % self.dom.format(self.c_value)

    def _call(self, x):
        return rcomp_add(x, self.c_value)

class MinusValueRcompMap(Map):
    """ 
        Implements _ -> _ - c  for Rcomp.    
    """

    def __init__(self, c_value):
        dom = Rcomp()
        dom.belongs(c_value)
        cod = dom
        Map.__init__(self, dom=dom, cod=cod)
        self.c = c_value
        
        self.top = dom.get_top()

    def __repr__(self):
        return "- %s" % self.dom.format(self.c)

    def _call(self, x):
        dom, cod = self.dom, self.cod 
        
        if is_top(dom, self.c):
            return 0.0 
        
        if dom.leq(x, self.c):
            return 0.0
        else:
            if is_top(dom, x):
                return cod.get_top()
            else:
                check_isinstance(x, float)
                res = x - self.c
                assert res >= 0
                return res
           
                
class MinusValueMap(Map):
    """ 
         h:  f ⟼  {max(0, r-c)} if  c ≠ ⊤
                   {0}           if  c = ⊤
                   
            
        (with c a positive constant.) 
    """

    @contract(P=RcompUnits, c_space=RcompUnits)
    def __init__(self, P, c_value, c_space):
        c_space.belongs(c_value)
        check_isinstance(P, RcompUnits)
        check_isinstance(c_space, RcompUnits)
    
        Map.__init__(self, dom=P, cod=P)
        self.c_value = c_value
        self.c_space = c_space

        self.c = express_value_in_isomorphic_space(c_space, c_value, P)
        self.P = P
        self.top = P.get_top()

    def __str__(self):
        return "- %s" % self.c_space.format(self.c_value)

    def __repr__(self):
        return "MinusValueMap(%s)" % self.__str__()

    def _call(self, x):
        dom, cod = self.dom, self.cod 
        
        if is_top(dom, self.c):
            return 0.0 
        
        if dom.leq(x, self.c):
            return 0.0
        else:
            if is_top(dom, x):
                return cod.get_top()
            else:
                check_isinstance(x, float)
                res = x - self.c
                assert res >= 0
                return res


class PlusValueNatMap(Map):

    def __init__(self, value):
        self.value = value
        self.N = Nat()
        self.N.belongs(value)
        Map.__init__(self, dom=self.N, cod=self.N)

    def _call(self, x):
        return Nat_add(x, self.value) 

    def __repr__(self):
        return '+ %s' % self.N.format(self.value)


class MinusValueNatMap(Map):
    
    """
        if value is Top:
        
            r |->   MapNotDefinedHere   if r != Top
                    Top  if r == Top  
        
        otherwise:
        
            r |->   MapNotDefinedHere   if r < value:
                    r - value  if r >= value 
        f - Top <= r 
    
    """
    @contract(value=int)
    def __init__(self, value):
        self.c = value
        N = Nat()
        Map.__init__(self, dom=N, cod=N)
        self.top  = self.dom.get_top()
        
    def _call(self, x):
        dom, cod = self.dom, self.cod 
        
        if is_top(dom, self.c):
            return 0 
        
        if dom.leq(x, self.c):
            return 0
        else:
            if is_top(dom, x):
                return cod.get_top()
            else:
                check_isinstance(x, int)
                res = x - self.c
                assert res >= 0
                return res
            
#         P = self.dom
#         
#         if is_top(self.dom, self.c):
#             #  r = 0 -> f empty
#             #  r = 1 -> f empty
#             #  r = Top -> f <= Top
#             if is_top(self.dom, x):
#                 return self.top
#             else:
#                 raise MapNotDefinedHere()
#         
#         if P.equal(x, self.c):
#             return 0
#         else:
#             if P.leq(x, self.c):
#                 msg = '%s < %s' % (P.format(x), P.format(self.c))
#                 raise MapNotDefinedHere(msg)
#             else:
#                 if is_top(P, x):
#                     return self.top
#                 else:
#                     check_isinstance(x, int)
#                     res = x - self.c
#                     assert res >= 0
#                     # todo: check underflow
#                     return res
                
    def __repr__(self):
        return '- %s' % self.c