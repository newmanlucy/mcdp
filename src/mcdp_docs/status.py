from mcdp_utils_xml.note_errors_inline import note_error2
from contracts.utils import indent

STATUS_ATTR = 'status'
allowed_statuses = [ 'unknown', 'draft', 'beta', 'ready', 'to-update', 'deprecated']

def all_headers(soup):
    headers = ['h1','h2','h3','h4','h5']
    for h in soup.find_all(headers):
        yield h
        
def check_status_codes(soup):
    for h in all_headers(soup):
        if STATUS_ATTR in h.attrs:
            s = h.attrs[STATUS_ATTR]
            if not s in allowed_statuses:
                msg = 'Invalid status code %r; expected one of %r' % (s, allowed_statuses)
                msg += '\n' + indent(str(h), '  ')
                note_error2(h, 'syntax error', msg)
        else:
            h.attrs[STATUS_ATTR] = 'unknown'
                

LANG_ATTR = 'lang'
allowed_langs = ['en', 'en-US', 'it','de','fr','es']

def check_lang_codes(soup):
    for h in all_headers(soup):
        if LANG_ATTR in h.attrs:
            s = h.attrs[LANG_ATTR]
            if not s in allowed_langs:
                msg = 'Invalid lang code %r; expected one of %r' % (s, allowed_langs)
                msg += '\n' + indent(str(h), '  ')
                note_error2(h, 'syntax error', msg)
                
