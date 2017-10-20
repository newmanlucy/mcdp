from mcdp_docs.make_console_pre import is_console_line
from comptests.registrar import comptest

@comptest
def is_console_line_test():
    s = "laptop $ sudo dd of=DEVICE if=IMG status=progress bs=4M "
    ct = is_console_line(s)
    assert ct is not None, s
    assert ct.hostname == 'laptop'
    assert ct.symbol == '$'
    assert ct.command == 'sudo dd of=DEVICE if=IMG status=progress bs=4M'
# 
#     s = " # echo"
#     ct = is_console_line(s)
#     assert ct is not None, s
#     assert ct.hostname == None
#     assert ct.symbol == '#'
#     assert ct.command == 'echo'
    
    s = " DOLLAR echo"
    ct = is_console_line(s)
    assert ct is not None, s
    assert ct.hostname == None
    assert ct.symbol == 'DOLLAR'
    assert ct.command == 'echo'