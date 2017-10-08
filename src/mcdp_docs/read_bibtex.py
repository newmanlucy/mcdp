# -*- coding: utf-8 -*-
import os

from bs4 import Tag, NavigableString
from system_cmd import system_cmd_result

from contracts import contract
from mcdp import logger
from mcdp_utils_misc import tmpdir
from mcdp_utils_xml import bs


#
# <dl>
#
# <dt>
# [<a name="esik09fixed">1</a>]
# </dt>
# <dd>
# Z&nbsp;&Eacute;sik.
#  Fixed point theory.
#  <em>Handbook of Weighted Automata</em>, 2009.
# [&nbsp;<a href="bibliography_bib.html#esik09fixed">bib</a>&nbsp;|
# <a href="http://dx.doi.org/10.1007/978-3-642-01492-5">DOI</a>&nbsp;]
#
# </dd>
@contract(contents='str', returns='str')
def run_bibtex2html(contents):
    with tmpdir(prefix='bibtex', erase=False, keep_on_exception=True) as d:
        fn = os.path.join(d, 'input.bib')
        fno = os.path.join(d, 'out')
        fno1 = fno + '.html'
        fno2 = fno + '_bib.html'
        with open(fn, 'w') as f:
            f.write(contents)

        cmd = ['bibtex2html',
               '-unicode',
               '--dl',
               '-o', fno,
               fn]

        system_cmd_result('.', cmd,
                          display_stdout=True,
                          display_stderr=True,
                          raise_on_error=True,
                          display_prefix=None,  # leave it there
                          env=None)

        bibtex2html_output = open(fno1).read()

        out = process_bibtex2html_output(bibtex2html_output)
        return out


def process_bibtex2html_output(bibtex2html_output):
    """ 
        From the bibtex2html output, get clean version. 
    """
    frag = bs(bibtex2html_output)
    res = Tag(name='div')

    ids = []
    for dt in frag.select('dt'):
        assert dt.name == 'dt'
        name = dt.a.attrs['name']
        name = 'bib:' + name
        ids.append(name)
        dd = dt.findNext('dd')
        assert dd.name == 'dd'
        entry = dd.__copy__()
        entry.name = 'cite'
        entry.attrs['id'] = name

        try_to_replace_stuff = True
        if try_to_replace_stuff:
            for x in list(entry.descendants):
                if isinstance(x, NavigableString):
                    s = x.string.encode('utf-8')
                    s = s.replace('\n', ' ')
                    s = s.replace('[', '')
                    s = s.replace('|', '')
                    s = s.replace(']', '')
                    y = NavigableString(unicode(s, 'utf-8'))
                    x.replace_with(y)
                    #print('string %r' % x.string)
                if isinstance(x, Tag) and x.name == 'a' and x.string == 'bib':
                    x.extract()
        res.append(NavigableString('\n'))
        res.append(entry)
        res.append(NavigableString('\n'))
    res.attrs['id'] = 'bibliography_entries'
    logger.info('Found %d bib entries.' % len(ids))
    return str(res)


def extract_bibtex_blocks(soup):
    """ Removes the blocks marked code.bibtex and returns a string
        with a composition of them. """
    s = ""
    for code in soup.select('code.bibtex'):
        parent = code.parent
        s += code.string + '\n\n'
        if parent.name == 'pre':
            parent.extract()
        else:
            code.extract()
    return s


