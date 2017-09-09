from abc import abstractmethod, ABCMeta
import copy
from mcdp import logger
from mcdp.exceptions import DPSemanticError
from mcdp_utils_xml.misc import soup_find_absolutely

from bs4.element import Tag
from contracts.utils import raise_desc, check_isinstance, indent, raise_wrapped
import yaml
from mcdp_utils_xml.note_errors_inline import note_error2


class RecipeContext():
    def __init__(self, soup):
        self.soup = soup

class Recipe():
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def make(self, context):  # @UnusedVariable
        """ Returns a BS4 element """
        t = Tag(name='span')
        t.append('Not implemented')
        return [t]
    
    @staticmethod
    def from_yaml(data):
        return parse_recipe_yaml(data)

class TocPlaceholder(Recipe):
    def make(self, context):  # @UnusedVariable
        t = Tag(name='div')
        t.attrs['id'] = 'toc'
        t.append('TOC placeholder')
        return [t]
    
class AddByID(Recipe):
    tag = 'add'
    def __init__(self, id_):
        self.id_ = id_
        
    @staticmethod
    def from_yaml(data):
        check_isinstance(data, dict)
        if not AddByID.tag in data:
            raise ValueError(data)
        data = copy.deepcopy(data)
        id_ = data.pop(AddByID.tag)
        if data:
            msg = 'Too many fields'
            raise_desc(ValueError, msg, data=data)
        return AddByID(id_)
    
    def make(self, context):
        soup = context.soup
        id_ = '%s:section' % self.id_ 
        try:
            e = soup_find_absolutely(soup, id_)
        except KeyError:
            msg = 'Cannot find ID %r in document.' % id_
            d = Tag(name='div')
            t = Tag(name='code')
            t.append(self.id_)
            d.append(t)
            note_error2(t, 'ref error', msg)
            return [d]
#             raise DPSemanticError(msg)
        logger.info('Adding section %r' %  e.attrs['id'])
        return [e.__copy__()] 
    
    def __str__(self):
        return 'AddByID(%s)' % self.id_
    
class MakePart(Recipe):
    tag = 'part'
    
    def __init__(self, id_part, title, contents):
        check_isinstance(id_part, str)
        check_isinstance(title, str)
        check_isinstance(contents, Recipe)
        self.id_part = id_part
        self.title = title
        self.contents = contents
    
    def make(self, context):
#         <section class="with-header-inside" id="part:all:section" level="part"><h1 counter-part="1" id="part:all" label-name="All units" label-number="A" label-self="" label-what="Part" label-what-number="Part A" label-what-number-name="Part A - All units">All units</h1><section class="without-header-inside" level="sec"><section class="without-header-inside" level="sub"><div style="display:none">Because of mathjax bug</div>
# </section>
        section = Tag(name='section')
        section.attrs['class'] = ['with-header-inside']
        section.attrs['level'] = ['part']
        section.attrs['id'] = "part:%s:section" % self.id_part
        h = Tag(name='h1') 
        h.attrs['id'] = 'part:' + self.id_part
        h.append(self.title)
        section.append(h)
        append_all(section, self.contents.make(context))
        return [section]
    
    def __str__(self):
        s = 'MakePart'
        s += '\n   id_part: %s' % self.id_part
        s += '\n     title: %s' % self.title
        s += '\n' + indent(str(self.contents), '', '  contents: ')
        return s
    
    @staticmethod
    def from_yaml(data):
        check_isinstance(data, dict)
        if not MakePart.tag in data:
            raise ValueError(data)
        data = copy.deepcopy(data)
        id_part = data.pop(MakePart.tag)
        title = data.pop('title')
        contents = data.pop('contents')
        if data:
            msg = 'Too many fields'
            raise_desc(ValueError, msg, data=data)
        contents = Sequence.from_yaml(contents)
        return MakePart(id_part=id_part, title=title, contents=contents)
     
class Sequence(Recipe):
    
    def __init__(self, children):
        self.children = children
        
    def make(self, context):
        res = []
        for c in self.children:
            res.extend( c.make(context))
        return res
    
    @staticmethod
    def from_yaml(data):
        children = [parse_recipe_yaml(_) for _ in data]
        return Sequence(children)
    
    def __str__(self):
        s = 'Sequence'
        for c in self.children:
            s += '\n' + indent(str(c), '', '- ')
        return s

def append_all(container, elements):
    for e in elements:
        container.append(e)
        
def parse_recipe_yaml(data):
    """ 
        Parses a YAML spec that describes the recipe. 
    
        Sequence:
        
            any list
        
        AddByID: a dict
        
            include: id
    
        MakePart: a dict
        
            part: id_to_create
            title: title of the part
            recipe:
    """
    try:
        if isinstance(data, list):
            return Sequence.from_yaml(data)
        elif isinstance(data, str):
            if data == 'toc':
                return TocPlaceholder()
            else:
                msg = 'Could not interpret %r' % data
                raise ValueError(msg)
        elif isinstance(data, dict):
            if AddByID.tag in data:
                return AddByID.from_yaml(data)
            if MakePart.tag in data:
                return MakePart.from_yaml(data)
            msg = 'Expecting either "%s" or "%s", found %s.' % (AddByID.tag, MakePart.tag, list(data))
            raise_desc(ValueError, msg, data=data)
        else:
            msg = 'Could not interpret recipe.'
            raise_desc(ValueError, msg, data=data)
    except ValueError as e:
        msg = 'Could not parse recipe YAML.'
        msg += '\n' + indent(yaml.dump(data), ' > ')
        raise_wrapped(ValueError, e, msg, compact=True)
        
        
    