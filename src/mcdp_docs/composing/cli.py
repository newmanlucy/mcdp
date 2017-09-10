from contracts import contract
import copy
from mcdp import logger
from mcdp import logger
from mcdp_docs.add_edit_links import add_github_links_if_edit_url
from mcdp_docs.composing.recipes import Recipe, RecipeContext, append_all
from mcdp_docs.manual_constants import MCDPManualConstants
from mcdp_docs.manual_join_imp import generate_and_add_toc,\
    document_final_pass_after_toc
from mcdp_docs.tocs import get_ids_from_soup, is_empty_link
from mcdp_utils_misc.fileutils import write_data_to_file
from mcdp_utils_xml.add_class_and_style import add_class
from mcdp_utils_xml.parsing import bs_entire_document

from bs4.element import Tag
from contracts.utils import check_isinstance, raise_wrapped
from decent_params.utils.script_utils import UserError
from quickapp.quick_app_base import QuickAppBase
import yaml


class ComposeConfig():
    @contract(recipe=Recipe, input_=str, output=str)
    def __init__(self, recipe, input_, output, purl_prefix, remove_status):
        check_isinstance(output, str)
        check_isinstance(input_, str)
        self.recipe = recipe
        self.input = input_
        self.output = output
        self.purl_prefix = purl_prefix
        self.remove_status = remove_status
        
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
        purl_prefix = data.pop('purl_prefix')
        remove_status = data.pop('remove_status', [])
        if not isinstance(remove_status, list):
            msg = 'I expected that remove_status was a list; found %r.' % remove_status
            raise ValueError(msg)
        
        
        recipe = Recipe.from_yaml(recipe)
        
        if data:
            msg = 'Spurious fields %s' % list(data)
            raise ValueError(msg) 
        
        return ComposeConfig(recipe, input_, output, purl_prefix, remove_status)
        
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
    permalink_prefix = compose_config.purl_prefix
    
    # Read input file
    data = open(input_).read()
    soup = bs_entire_document(data)
    # Create context
    doc = soup.__copy__()
    body = Tag(name='body')
    doc.body.replace_with(body)
    elements = recipe.make(RecipeContext(soup=soup))
    check_isinstance(elements, list)
    append_all(body, elements)
    
    # Now remove stuff
    for status in compose_config.remove_status:
        removed = []
        for section in list(body.select('section[status=%s]' % status)):
            removed.append(section.attrs['id'])
            section.extract()
        if not removed:
            logger.info('Found no section with status = %r to remove.' % status)
        else:
            logger.info('I removed %d sections with status %r.' % (len(removed), status))
            logger.debug('Removed: %s' % ", ".join(removed))
            
             
    
    add_github_links_if_edit_url(doc, permalink_prefix=permalink_prefix)
    
    generate_and_add_toc(doc)
    doc = doc.__copy__()
    
#     generate_and_add_toc(soup)
#     substituting_empty_links(soup)
    raise_errors = False
    find_links_from_master(master_soup=soup, version_soup=doc, raise_errors=raise_errors)
    
    document_final_pass_after_toc(doc)
    results = str(doc)
    write_data_to_file(results, output)
    

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