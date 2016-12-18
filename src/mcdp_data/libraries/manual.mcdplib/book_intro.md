# Introduction

This book presents a new approach to formalizing and solving
co-design problems.


You will learn: ...

* how to use the MCDPL language...
* how to use the IDE...
* how to model things in several domains...

This is experimental software...

Please send any comment to:

## A brief summary of the theory

* composition ...

### Categorical foundations

...

### Pointers to papers

These are the papers available for the theory:

* A mathematical approach to Co-Design...

These are useful background papers and books:

* ...

## A new approach to co-design

...


### Where to use it?

It can be applied in different fields...

### Advantages and limitations

Advantages of the method:

* intuitive...
* scalable...
* zooming in and out...
* multi-domain...
* ...

Limitations:

* You still need to model...

Next steps:

* ...

## Advantages and limitations

As this is work in progress; it will take some time before it
can be reliably deployed. However, it already has some advantages.

Here we list advantages and current limitations of the work.

### Theory

Advantages of the theory:

* ...

Limitations of the theory:

* ...

Next steps for the theory:

* ...

### Language

Advantages of the language:

* ...

Limitations of the language:

* ...

Next steps for the language:

* ...

### Core implementation

Advantages of the implementation:

* The code is elegant
* It is *exhaustively* tested.
* ...

Limitations of the implementation:

* This is experimental software.
* Some of the operations are implemented using $O(n^2)$ operations
while $O(n \log(n))$ would be possible. In particular, meet and join
of antichains are not efficiently implemented.
* It is slow because of Python, generally, and the fact that there are not
* ...

Next steps for the implementation:

* ...
* Compile down to native code using LLVM.

### Environment

Advantages of the environment:

* Browsing libraries. Creating models, posets, etc.
* Semantic highlighting of code.
* Visual feedback for most objects; e.g. diagrams are shown visually.
* ...
* beutification (formatting)

Limitations of the environment:

* Not all functions are implemented from the UI. For example,
  it is not possible to create a new library from the UI.

Next steps for the environment:

* ...


### Pointers to software

## Acknowledgements

### People

I would like to acknowledge:

* David Spivak
* Joshua Tan
* Marsden for geometry. (Here, I'm proud that the invariance group is quite large: it
is the group of all invariant  )

### Funding sources

### Un-related work

There is some work that is "unrelated", which I cannot find
a way to cite in my papers, though this was very inspirational.

...

<!--
* Homotopy Type Theory
* I found very useful the lessons Bartos Miliewsky -->

### Open source software

Developing this software would not have been possible without
the open source / free software ecosystem.

In particular, enablers were:

* Python, Numpy, Scipy, PyParsing, ...
* NodeJS, MathJax, ...

<!-- Prince : not  -->