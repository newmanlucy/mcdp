import os

from bs4.element import Tag
from system_cmd.meat import system_cmd_result
import yaml

from comptests.registrar import comptest, run_module_tests
from mcdp.exceptions import DPSemanticError
from mcdp_library_tests.create_mockups import with_dir_content
from mcdp_utils_xml import soup_find_absolutely
from mcdp_utils_xml.parsing import bs_entire_document, bs
from mcdp_utils_misc.fileutils import write_data_to_file
from mcdp_docs.tocs import generate_toc
from mcdp.logs import logger


@comptest
def read_config_test():
    config = yaml.load("""
include:
- sb
- sa
    """)
    
    
    
@comptest
def compose2():
    f1 = """
<html>
    <head></head>
"""


data1 = """

docs:
    file1.md: |
    
        # SA {#sa} 
        
        This is section A
    
    file2.md: |
    
        # SB {#sb}
        
        This is section B
        
    00_main_template.html: |
        
        <html>
            <head></head>
            <body</body>
        </html>
    
        
book.noparts.yaml: |
    - include:
      - sb
      - sa
    - make:
      part: 10
book.version.yaml: |
    compose:
        part:units:
          title: This is the first part.
          includes:
          - include:sb
          - include:sa
        part:two:
          title: This is an empty part.
"""

@comptest
def composing1():
    with with_dir_content(data1):
        cwd = '.'
        res = 'res/all.html'
        cmd = [
            'mcdp-render-manual',
            '--src','docs',
           '--stylesheet', 'v_manual_split',
           '--mathjax', '0',
           '-o', 'out/out1',
           '--output_file', res]
        system_cmd_result(cwd=cwd, cmd=cmd,
                          display_stdout=True,
                          display_stderr=True,
                          raise_on_error=True,
                          ) 
        
#         files = locate_files('.', '*', normalize=False)
        #print "\n".join(files)
        assert os.path.exists(res)
        data = bs_entire_document(open(res).read())        
        assert data.find(id='sa:section') is not None
        assert data.find(id='sb:section') is not None

        html = open(res).read()
        includes = ['sb', 'sa']
        soup = bs_entire_document(html)
        soup2 = select(soup, includes)
        toc = generate_toc(soup2.body)
        soup2.body.append(bs(toc))
        write_data_to_file(str(soup2), 'dist/new.html')
        print str(soup2)

    
def select(soup, includes):
    doc = soup.__copy__()
    body = Tag(name='body')
    doc.body.replace_with(body)
    for i in includes:
        id_ = '%s:section' % i 
        try:
            e = soup_find_absolutely(soup, id_)
        except KeyError:
            msg = 'Cannot find ID %r in document.' % id_
            raise DPSemanticError(msg)
        logger.info('Adding section %r' %  e.attrs['id'])
        body.append(e.__copy__()) 
    return doc
    

if __name__ == '__main__':
    run_module_tests()