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
    
    document_final_pass_after_toc(doc)
    results = str(doc)
    write_data_to_file(results, output)
    
    
    
    
    
#         src = options.src
#         src_dirs = [_ for _ in src.split(":") if _ and _.strip()]