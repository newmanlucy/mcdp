
def get_keywords(source):
    line1 = source.split('\n')[0]
    return line1.split()

def gives_semantic_error(source):
    keywords = get_keywords(source)
    return 'semantic_error' in keywords

def gives_not_implemented_error(source):
    keywords = get_keywords(source)
    return 'not_implemented_error' in keywords

def gives_syntax_error(source):
    keywords = get_keywords(source)
    return 'syntax_error' in keywords