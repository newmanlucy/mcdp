# -*- coding: utf-8 -*-
from nose.tools import assert_equal

from comptests.registrar import register_indep
from contracts import contract
from contracts.utils import raise_desc, raise_wrapped, check_isinstance
from mcdp_lang.namedtuple_tricks import remove_where_info
from mcdp_lang.parse_actions import parse_wrap, parse_wrap_filename
from mcdp_lang.parse_interface import parse_ndp, parse_ndp_filename
from mocdp.comp.interfaces import NamedDP
from mocdp.comp.wrap import SimpleWrap
from mcdp.exceptions import DPSemanticError, DPSyntaxError, DPNotImplementedError
from mcdp_lang.find_parsing_el import ParsingElement, find_parsing_element


def assert_syntax_error(s, expr, desc=None):
    if isinstance(expr, ParsingElement):
        expr = expr.get()
    try:
        res = parse_wrap(expr, s)
    except DPSyntaxError:
        pass
    except BaseException as e:
        msg = "Expected syntax error, got %s." % type(e)
        raise_wrapped(Exception, e, msg, s=s)
    else:
        msg = "Expected an exception, instead succesfull instantiation."
        if desc:
            msg += '\n' + desc
        raise_desc(Exception, msg, s=s, res=res.repr_long())

def assert_syntax_error_fn(filename, expr, desc=None):
    if isinstance(expr, ParsingElement):
        expr = expr.get()
    try:
        res = parse_wrap_filename(expr, filename)
    except DPSyntaxError:
        pass
    except BaseException as e:
        msg = "Expected syntax error, got %s." % type(e)
        raise_wrapped(Exception, e, msg, filename=filename)
    else:
        msg = "Expected an exception, instead succesfull instantiation."
        if desc:
            msg += '\n' + desc
        raise_desc(Exception, msg, filename=filename, res=res.repr_long())


def assert_semantic_error_fn(filename, desc=None):
    try:
        res = parse_ndp_filename(filename)
        res.abstract()
    except DPSemanticError:
        pass
    except BaseException as e:
        msg = "Expected semantic error, got %s." % type(e)
        raise_wrapped(Exception, e, msg)
    else:
        msg = "Expected an exception, instead succesfull instantiation."
        if desc:
            msg += '\n' + desc
        raise_desc(Exception, msg, filename=filename, res=res.repr_long())
        
def assert_not_implemented_error_fn(filename, desc=None):
    try:
        res = parse_ndp_filename(filename)
        res.abstract()
    except DPNotImplementedError:
        pass
    except BaseException as e:
        msg = "Expected DPNotImplementedError, got %s." % type(e)
        raise_wrapped(Exception, e, msg)
    else:
        msg = "Expected a DPNotImplementedError, instead succesfull instantiation."
        if desc:
            msg += '\n' + desc
        raise_desc(Exception, msg, filename=filename, res=res.repr_long())
        
def assert_semantic_error(s , desc=None): # TODO: redundant with assert_parse_ndp_semantic_error(string, contains)
    """ This asserts that s can be parsed, but"""
    try:
        res = parse_ndp(s)
        res.abstract()
    except DPSemanticError:
        pass
    except BaseException as e:
        msg = "Expected semantic error, got %s." % type(e)
        raise_wrapped(Exception, e, msg, s=s)
    else:
        msg = "Expected an exception, instead succesfull instantiation."
        if desc:
            msg += '\n' + desc
        raise_desc(Exception, msg, s=s, res=res.repr_long())

# def assert_not_implemented_error(s , desc=None): # TODO: redundant with assert_parse_ndp_semantic_error(string, contains)
#     """ This asserts that s can be parsed, but"""
#     try:
#         res = parse_ndp(s)
#         res.abstract()
#     except DPNotImplementedError:
#         pass
#     except BaseException as e:
#         msg = "Expected DPNotImplementedError error, got %s." % type(e)
#         raise_wrapped(Exception, e, msg, s=s)
#     else:
#         msg = "Expected an exception, instead succesfull instantiation."
#         if desc:
#             msg += '\n' + desc
#         raise_desc(Exception, msg, s=s, res=res.repr_long())

@contract(returns=NamedDP)
def assert_parsable_to_unconnected_ndp(s, desc=None):  # @UnusedVariable
    res = parse_ndp(s)
    if res.is_fully_connected():
        msg = 'The graph appears connected but it should be disconnected.'
        raise Exception(msg)
    return res

@contract(returns=NamedDP)
def assert_parsable_to_unconnected_ndp_fn(filename):
    res = parse_ndp_filename(filename)
    if res.is_fully_connected():
        msg = 'The graph appears connected but it should be disconnected.'
        raise Exception(msg)
    return res


@contract(returns=NamedDP)
def assert_parsable_to_connected_ndp_fn(filename):
    res = parse_ndp_filename(filename)
    if isinstance(res, SimpleWrap):
        return res
    ndp = res.abstract()
    return ndp

@contract(returns=NamedDP)
def assert_parsable_to_connected_ndp(s , desc=None):  # @UnusedVariable
    """ This asserts that s can be compiled to a *connected* ndp. """
    res = parse_ndp(s)
    if isinstance(res, SimpleWrap):
        return res
    ndp = res.abstract()
    #print(ndp.repr_long())
    return ndp


class TestFailed(Exception):
    pass

@contract(string=bytes)
def parse_wrap_check(string, expr, result=None):
    check_isinstance(string, str)
    if isinstance(expr, ParsingElement):
        expr = expr.get()

    try:
        expr_name = find_parsing_element(expr)
    except ValueError:
        expr_name = '(unknown parse expr)'
    
    try:
        res = parse_wrap(expr, string)[0]  # note the 0, first element
        res0 = remove_where_info(res)
        if result is not None:
            assert_equal(result, res0)
        return res
    except BaseException as e:
        msg = 'Cannot parse %r' % string
        raise_wrapped(TestFailed, e, msg,
                      expr_name=expr_name,
                      string=string, expected=result)


@contract(string=str, contains='str|None')
def assert_parse_ndp_semantic_error(string, contains=None):
    """
        Asserts that parsing this string as an NDP will raise
        a DPSemanticError. If contains is not None, it is 
        a substring that must be contained in the error.
        
        Returns the exception. 
    """
    try:
        res = parse_ndp(string)
    except DPSemanticError as e:
        if contains is not None:
            s = str(e)
            if not contains in s:
                msg = 'Expected a DPSemanticError with substring %r.' % contains
                raise_wrapped(TestFailed, e, msg, string=string)
            return e
        else:
            return e
    except BaseException as e:
        msg = 'Expected DPSemanticError, but obtained %s.' % type(e)
        raise_wrapped(TestFailed, e, msg, string=string)

    msg = 'Expected DPSemanticError, but no exception was thrown.'
    raise_desc(TestFailed, msg, string=string, result=res) 
    assert False
    
@contract(string=str, contains='str|None')
def parse_wrap_semantic_error(string, expr, contains=None):
    """ 
        Assert semantic error. If contains is not None, it is 
        a substring that must be contained in the error. 
    
        Returns the exception.
    """
    if isinstance(expr, ParsingElement):
        expr = expr.get()

    try:
        res = parse_wrap(expr, string)[0]  # note the 0, first element
    except DPSemanticError as e:
        if contains is not None:
            s = str(e)
            if not contains in s:
                msg = 'Expected a DPSemanticError with substring %r.' % contains
                raise_wrapped(TestFailed, e, msg,
                              expr=find_parsing_element(expr), string=string)
            return e
        else:
            return e
    except BaseException as e:
        msg = 'Expected DPSemanticError, but obtained %s.' % type(e)
        raise_wrapped(TestFailed, e, msg,
                      expr=find_parsing_element(expr), string=string)

    msg = 'Expected DPSemanticError, but no except was thrown.'
    raise_desc(TestFailed, msg,
                  expr=find_parsing_element(expr), string=string,
                  result=res) 
    assert False

@contract(string=str)
def parse_wrap_syntax_error(string, expr):
    """ Assert syntax error """
    if isinstance(expr, ParsingElement):
        expr = expr.get()

    try:
        res = parse_wrap(expr, string)
        _res = res[0]  # note the 0, first element
        msg = 'Expected DPSyntaxError.'
        raise_desc(TestFailed, msg, res=res.__repr__())
    except DPSyntaxError as e:
        return e
    except BaseException as e:
        msg = 'Expected DPSyntaxError.'
        raise_wrapped(TestFailed, e, msg,
                      expr=find_parsing_element(expr), string=string)



def ok(expr, string, result=None):
    expr = find_parsing_element(expr)
    register_indep(parse_wrap_check, dynamic=False,
                   args=(string, expr, result), kwargs=dict())
 

def syn(expr, string):
    expr = find_parsing_element(expr)
    register_indep(parse_wrap_syntax_error, dynamic=False,
                   args=(string, expr), kwargs=dict())



