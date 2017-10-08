from comptests.registrar import comptest, run_module_tests
from mcdp_docs.make_console_pre import link_to_command_explanation
from mcdp_utils_xml.parsing import bs


@comptest
def link_to_command_explanation_check1():
    s = """
<pre class='console'>
<span class='program'>ls</span> file
</pre>
    """
    soup = bs(s)
    link_to_command_explanation(soup)
    s2 = str(soup)
    # print s2
    assert '<a href="#ls"' in s2

@comptest
def link_to_command_explanation_check2():
    s = """
    <pre class="console"><code><span class="console_sign">$</span><span class="space"> </span><span class="curl program">curl</span><span class="space"> </span><span class="program_option">-o</span><span class="space"> </span>duckiebot-RPI3-AC-aug10.img.xz<span class="space"> </span><span class="placeholder">URL above</span>
</code></pre>"""

    soup = bs(s)
    link_to_command_explanation(soup)
    s2 = str(soup)
    print s2
    assert '<a href="#curl"' in s2
    
@comptest
def link_to_command_explanation_check3():
    s = """
 <fragment><div style="display:none">Because of mathjax bug</div>
<h1 id="networking">Networking tools</h1>
<div class="special-par-assigned-wrap"><p class="special-par-assigned">Andrea</p></div>
<div class="requirements">
<p>Preliminary reading:</p>
<ul>
<li>
<p>Basics of networking, including</p>
<ul>
<li>what are IP addresses</li>
<li>what are subnets</li>
<li>how DNS works</li>
<li>how <code>.local</code> names work</li>
<li>…</li>
</ul>
 </li>
</ul>
<div class="special-par-see-wrap"><p class="status-XXX special-par-see"> (ref to find).</p></div>
</div>
<div class="todo-wrap"><p class="todo">to write</p></div>
<p>Make sure that you know:</p>
<h2 id="visualizing-information-about-the-network">Visualizing information about the network</h2>
<h3 id="ping-are-you-there"><code>ping</code>: are you there?</h3>
<div class="todo-wrap"><p class="todo">to write</p></div>
<h3 id="ifconfig"><code>ifconfig</code></h3>
<div class="todo-wrap"><p class="todo">to write</p></div>
<pre class="console"><code><span class="console_sign">$</span><span class="space"> </span><span class="ifconfig program">ifconfig</span>
</code></pre></fragment>

"""
    soup = bs(s)
    link_to_command_explanation(soup)
    s2 = str(soup)
#     print s2
    assert '<a href="#ifconfig"' in s2
    
if __name__ == '__main__': # pragma: no cover
    run_module_tests()
    