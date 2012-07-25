==========================================
CWWFL: Computing With Words, Fuzzy Logic
==========================================


Goals
=======

The goal of this project is to create a class library for the fuzzy logic (FL)
operations involved in computing with words (CWW).  

Requirements
==============

- object oriented with class hierarchy 

- model-view-controller architecture (operator interaction framework)

- use exceptions to deal with data input and membership function estimation

- implementations in multiple programming languages, currently Python and Java

- web-friendly

- lazy evaluation: when you "and" or "or" together two fuzzy sets, the result
  is a fuzzy set, but it's membership function need not be computed.  Rather,
  keep the two fuzzy set operands saved in the result and only evaluated when
  needed.

Notes
======

pyinterval
-----------

- had to install crlibm (correctly rounded math library)
  http://lipforge.ens-lyon.fr/projects/crlibm

   - had to use the -fPIC flag, via ./configure CFLAGS=-fPIC
