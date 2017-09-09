from quickapp.quick_app_base import QuickAppBase
import copy
import yaml
from contracts.utils import check_isinstance, raise_wrapped
from mcdp_docs.composing.recipes import Recipe, RecipeContext, append_all
from mcdp_utils_xml.parsing import bs_entire_document
from bs4.element import Tag
from mcdp_utils_misc.fileutils import write_data_to_file
from contracts import contract
from decent_params.utils.script_utils import UserError
from mcdp_docs.manual_join_imp import generate_and_add_toc,\
    document_final_pass_after_toc
from mcdp_docs.tocs import substituting_empty_links, get_empty_links_to_fragment,\
    get_ids_from_soup, is_empty_link
from mcdp_utils_xml.add_class_and_style import add_class
from mcdp.constants import MCDPConstants
from mcdp_docs.manual_constants import MCDPManualConstants

class ComposeConfig():
    @contract(recipe=Recipe, input_=str, output=str)
    def __init__(self, recipe, input_, output):
        check_isinstance(output, str)
        check_isinstance(input_, str)
        self.recipe = recipe
        self.input = input_
        self.output = output
        
    @staticmethod
    def from_yaml(data):
        """
            input:
            recipe:
            output:
        """
        check_isinstance(data, dict)
        data = copy.deepcopy(data)
        
        input_ = data.pop('input')
        output = data.pop('output')
        recipe = data.pop('recipe')
        recipe = Recipe.from_yaml(recipe)
        
        if data:
            msg = 'Spurious fields %s' % list(data)
            raise ValueError(msg) 
        
        return ComposeConfig(recipe, input_, output)
        
class Compose(QuickAppBase):
    """ """

    def define_program_options(self, params):
        params.add_string('config', help="""Configuration file""")

    def go(self):
        options = self.get_options()
        config = options.config
        try:
            data = yaml.load( open(config).read())
            compose_config = ComposeConfig.from_yaml(data)
        except ValueError as e:
            msg = 'Cannot read YAML config file %s' % config
            raise_wrapped(UserError, e, msg, compact=True)
        go(compose_config)

compose_main = Compose.get_sys_main()

def go(compose_config):
    input_ = compose_config.input
    output = compose_config.output
    recipe = compose_config.recipe
    # Read input file
    data = open(input_).read()
    soup = bs_entire_document(data)
    # Create context
    doc = soup.__copy__()
    body = Tag(name='body')
    doc.body.replace_with(body)
    m = recipe.make(RecipeContext(soup=soup))
    check_isinstance(m, list)
    append_all(body, m)
    generate_and_add_toc(doc)
    doc = doc.__copy__()
    
    # Generate the names for the soup
#     soup = soup.__copy__()

#     generate_and_add_toc(soup)
#     substituting_empty_links(soup)
    raise_errors = False
    find_links_from_master(master_soup=soup, version_soup=doc, raise_errors=raise_errors)
    
    document_final_pass_after_toc(doc)
    results = str(doc)
    write_data_to_file(results, output)
    
from mcdp import logger

def find_links_from_master(master_soup, version_soup, raise_errors):
    logger.info('find_links_from_master')
    from mcdp_docs.tocs import sub_link
    # find all ids
    master_ids = get_ids_from_soup(master_soup)
    version_ids = get_ids_from_soup(version_soup)
    missing = []
    seen = [] 
    
    for a, eid in a_linking_to_fragments(version_soup):
        seen.append(eid)

        if not eid in version_ids:
            missing.append(eid)
            if eid in master_ids:
                logger.info('found %s in master' % eid)
                linked_element = master_ids[eid]
                if is_empty_link(a):
#                     a.attrs['class'] = 
                    add_class(a, MCDPManualConstants.CLASS_ONLY_NAME)
                    sub_link(a, eid, linked_element, raise_errors)
                
                href = 'http://purl.org/dth/%s' % remove_prefix(eid)
                
                a.attrs['href'] = href
                add_class(a, 'link-to-master')
            else:
                logger.info('Not found %r in master.' % eid)
#     logger.debug('seen: %s' % seen)
#     logger.debug('missing: %s' % missing)
    
def a_linking_to_fragments(soup):
    for a in soup.select('a'):
        href = a.attrs['href']
        if not href.startswith('#'):
            continue
        eid = href[1:]
        yield a, eid
             
def remove_prefix(id_):
    if ':' in id_:
        return id_[id_.index(':')+1:]
    else: 
        return id_
    
    
#         src = options.src
#         src_dirs = [_ for _ in src.split(":") if _ and _.strip()]