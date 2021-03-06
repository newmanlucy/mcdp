# -*- coding: utf-8 -*-
from contracts.utils import indent, raise_desc, raise_wrapped
from mcdp_posets import (NotBelongs, UpperSet,
    UpperSets, get_product_compact, poset_minima)
from mcdp_posets import LowerSets, LowerSet
from mcdp_posets.find_poset_minima.baseline_n2 import poset_maxima
from mcdp.exceptions import DPInternalError
from mcdp_utils_misc.memoize_simple_imp import memoize_simple
from .primitive import NotFeasible, PrimitiveDP
from .tracer import Tracer
from mcdp.development import do_extra_checks, mcdp_dev_warning


__all__ = [
    'Series',
    'Series0',
]


class Series(PrimitiveDP):

    def __init__(self, dp1, dp2):
        self.dp1 = dp1
        self.dp2 = dp2

        R1 = self.dp1.get_res_space()
        F2 = self.dp2.get_fun_space()

        if not R1 == F2:
            msg = 'Cannot connect different spaces R1 = {} and F2 = {}.'.format(R1,F2)
            raise_desc(DPInternalError, msg, dp1=self.dp1.repr_long(),
                       dp2=self.dp2.repr_long(), R1=R1, F2=F2)

        F1 = self.dp1.get_fun_space()
        R2 = self.dp2.get_res_space()

        self.M1 = self.dp1.get_imp_space()
        self.M2 = self.dp2.get_imp_space()

        M, _, _ = self._get_product()
        self._solve_cache = {}
        PrimitiveDP.__init__(self, F=F1, R=R2, I=M)

    def __getstate__(self):
        state = dict(**self.__dict__)
        state.pop('prod', None)
        return state

    def _get_product(self):
        if not hasattr(self, 'prod'):
            self.prod = _, _, _ = get_product_compact(self.M1, self.M2)
            assert hasattr(self, 'prod')

        return self.prod

    def _unpack_m(self, m):
        M, _, unpack = self._get_product()
        if do_extra_checks():
            M.belongs(m)
        m1, m2 = unpack(m)
        return m1, m2

    def evaluate(self, i):
        m1, m2 = self._unpack_m(i)
        fs, _ = self.dp1.evaluate(m1)
        _, rs = self.dp2.evaluate(m2)
        return fs, rs

    @memoize_simple
    def get_implementations_f_r(self, f, r):
        # print('%s get_implementaion(%s, %s)' % (id(self), f, r))
        f1 = f
        _, pack, _ = self._get_product()
        R2 = self.dp2.get_res_space()
        res = set()
        # First let's solve again for r1
        r1s = self.dp1.solve(f)
        for r1 in r1s.minimals:
            m1s = self.dp1.get_implementations_f_r(f1, r1)
            
            if do_extra_checks(): 
                try:
                    for m1 in m1s:
                        self.M1.belongs(m1)
                except NotBelongs as e:
                    msg = 'Invalid result from dp1 (%s)' % type(self.dp1)
                    raise_wrapped(DPInternalError, e, msg, M1=self.M1, m1=m1,
                                  dp1=self.dp1.repr_long())

            assert m1s, (self.dp1, f1, r1)
            
            f2 = r1
            r2s = self.dp2.solve(f2)

            for r2 in r2s.minimals:
                if not R2.leq(r2, r):
                    continue
                m2s = self.dp2.get_implementations_f_r(f2, r2)
                for m1 in m1s:
                    for m2 in m2s:
                        m = pack(m1, m2)
                        res.add(m)
        if not res:
            msg = 'The (f,r) pair was not feasible.'
            raise_desc(NotFeasible, msg, f=f, r=r, self=self)

        if do_extra_checks():
            M = self.get_imp_space()
            for _ in res:
                M.belongs(_)
        assert res
        return res

#     def check_feasible(self, f1, m, r2):
#         # print('series:check_feasible(%s,%s,%s)' % (f1, m, r))
#         M, _, unpack = self._get_product()
#         if do_extra_checks():
#             M.belongs(m)
#         m1, m2 = unpack(m)
# 
#         lf1, ur1 = self.dp1.evaluate(m1)
#         lf2, ur2 = self.dp2.evaluate(m2)
# 
#         try:
#             lf1.belongs(f1)
#         except NotBelongs as e:
#             msg = 'First is not feasible'
#             raise_wrapped(NotFeasible, e, msg, lf1=lf1, f1=f1)
#         try:
#             ur2.belongs(r2)
#         except NotBelongs as e:
#             msg = 'Second is not feasible'
#             raise_wrapped(NotFeasible, e, msg, lf1=lf1, f1=f1)
# 
#         feasible = non_zero_intersection(ur1=ur1, lf2=lf2)
#         if not feasible:
#             msg = 'Intersection is empty.'
# 
#             s = ('%s [ m1 = %s ] %s <= %s [ m2 = %s ] %s' %
#                   (lf1, m1, ur1, lf2, m2, ur2))
# 
#             raise_desc(NotFeasible, msg,
#                           dp1=self.dp1.repr_long(), dp2=self.dp2.repr_long(),
#                           s=s)
#
#     def check_unfeasible(self, f1, m, r2):
#         try:
#             self.check_feasible(f1, m, r2)
#         except NotFeasible:
#             pass
#         else:
#             msg = 'It is feasible.'
#             raise_desc(Feasible, msg, f1=f1, m=m, r2=r2)

    # @memoize_simple
    def solve(self, func):
        trace = Tracer()
        return self.solve_trace(func, trace)

    def solve_trace(self, func, trace):
        if func in self._solve_cache:
            # trace.log('using cache for %s' % str(func))
            return trace.result(self._solve_cache[func])

        trace.values(type='series')

        with trace.child('dp1') as t:
            u1 = self.dp1.solve_trace(func, t)

        if do_extra_checks():
            R1 = self.dp1.get_res_space()
            tr1 = UpperSets(R1)
            tr1.belongs(u1)

        mcdp_dev_warning('rewrite this keeping structure')
        mins = set([])
        for u in u1.minimals:
            with trace.child('dp2') as t:
                v = self.dp2.solve_trace(u, t)
            mins.update(v.minimals)

        R = self.get_res_space()
        minimals = poset_minima(mins, R.leq)

        us = UpperSet(minimals, R)

        self._solve_cache[func] = us
        return trace.result(us)

    def solve_r(self, r):
        l2 = self.dp2.solve_r(r)

        if do_extra_checks():
            F2 = self.dp2.get_fun_space()
            LF2 = LowerSets(F2)
            LF2.belongs(l2)

        maxs = set([])
        
        # todo: express as operation on antichains
        for l in l2.maximals:    
            v = self.dp1.solve_r(l)
            maxs.update(v.maximals)

        F = self.get_fun_space()
        maximals = poset_maxima(maxs, F.leq)

        lf = LowerSet(maximals, F)
        return lf

    def __repr__(self):
        return 'Series(%r, %r)' % (self.dp1, self.dp2)

    def repr_long(self):
        r1 = self.dp1.repr_long()
        r2 = self.dp2.repr_long()
        s1 = 'Series:'
        s2 = ' %s ⇸ %s' % (self.get_fun_space(), self.get_res_space())
        s = s1 + ' % ' + s2
        s += '\n' + indent(r1, '. ', first='\ ')
        s += '\n' + indent(r2, '. ', first='\ ')
        return s
    
    def repr_h_map(self):
        return 'f ⟼ [h2 ○ h1](f)' # XXX
    
    def repr_hd_map(self):
        return 'r ⟼ [h1* ○ h2*](r)' # XXX


Series0 = Series 
# 
# if False:
#     # Huge product spaces
#     def prod_make(S1, S2):
#         S = PosetProduct((S1, S2))
#         return S
# 
#     def prod_get_state(S1, S2, s):  # @UnusedVariable
#         (s1, s2) = s
#         return (s1, s2)


    
    
    
