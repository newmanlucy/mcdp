from comptests.registrar import comptest, run_module_tests
from mcdp_docs.composing.cli import Compose
from mcdp_docs.composing.recipes import Recipe
from mcdp_docs.mcdp_render_manual import RenderManual
from mcdp_docs.split import Split
from mcdp_library_tests.create_mockups import with_dir_content
from mcdp_utils_xml.parsing import bs_entire_document
import os

import yaml
from git.repo.base import Repo
from mcdp_utils_misc.fileutils import write_data_to_file


@comptest
def read_config_test():
    config = yaml.load("""
- add: sb
- add: sa
- part: one
  title: My title
  contents:
  - add: s1
  - add: s2
""")
    d = Recipe.from_yaml(config)
    print d
    

def run_app(app, args):
    main = app.get_sys_main()
    ret = main(args=args, sys_exit=False)
    if ret: raise Exception(ret)
    
@comptest
def composing1():
    
    data1 = """

docs:
    file0.md: |
    
        <div id='toc'></div>
        
        # All units {#part:all} 
    
    file1.md: |
    
        # Audacious {#sa} 
        
        This is section Audacious.
        
        Linking to:
        
        - <a href="#sa" class="number_name"></a>
        - <a href="#sb" class="number_name"></a>
        - <a href="#sc" class="number_name"></a>
    
    file2.md: |
    
        # Bumblebee {#sb}
        
        This is section Bumblebee. 
        
        Linking to:

        - <a href="#sa" class="number_name"></a>
        - <a href="#sb" class="number_name"></a>
        - <a href="#sc" class="number_name"></a>
        
        # Elephant {#elephant status=draft}
        
        Section Elephant is not ready.

    file3.md: |
    
        # Cat {#sc}
        
        This is section Cat. 
        
        Linking to:

        - <a href="#sa" class="number_name"></a>
        - <a href="#sb" class="number_name"></a>
        - <a href="#sc" class="number_name"></a>
        
    00_main_template.html: |
        
        <html>
            <head></head>
            <body</body>
        </html>
    
book.version.yaml: |
    input: dist/master/book.html
    recipe:
        - toc
        - part: part1
          title: First part
          contents:
          - add: sb
        - part: part2
          title: Second part
          contents:
          - add: sa
          - add: elephant
    output: dist/version/book.html
    purl_prefix: http://purl.org/dt/fall2017/
    remove_status: [draft]

.compmake.rc:
    config echo 1
    
"""
    use = '/tmp/composing1'
        
    with with_dir_content(data1, use_dir=use):
        
        repo = Repo.init('.')
        fn = 'readme'
        write_data_to_file('', fn)
        repo.index.add([fn])
        repo.index.commit("initial commit")
        
        url = 'git@github.com:AndreaCensi/example.git'
        repo.create_remote('origin', url)
        
        res = 'dist/master/book.html'
        run_app(RenderManual,  [ 
                '--src','docs',
               '--stylesheet', 'v_manual_split',
               '--mathjax', '0',
               '-o', 'out/out1',
                '--no_resolve_references',
               '--output_file', res])
                 
        assert os.path.exists(res)
        data = bs_entire_document(open(res).read())        
        assert data.find(id='sa:section') is not None
        assert data.find(id='sb:section') is not None

        run_app(Split, ['--filename', 'dist/master/book.html', '--output_dir', 'dist/master/book'])
        run_app(Compose, ['--config', 'book.version.yaml'])
        version_whole = bs_entire_document(open('dist/version/book.html').read())        
        assert version_whole.find(id='sa:section') is not None
        assert version_whole.find(id='sb:section') is not None
        assert version_whole.find(id='elephant:section') is None

        run_app(Split, ['--filename', 'dist/version/book.html', '--output_dir', 'dist/version/book'])

if __name__ == '__main__':
    run_module_tests()