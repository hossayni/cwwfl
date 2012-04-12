do we need a abstract factory?  Maybe... a fuzzy set should inherit from it's
domain, eg, usually a float, but also sets or perhaps integers:

- mu_A(.5) = the membership of .5 in A, a's domain is floats
- mu_Mammal("platypus") = the membership of platypus in Mammals,
  Mammal's domain is the set of animals/organisms/objects in world

So what we'd like is the creation of a fuzzy object that goes something like
this:
  
  A = FuzzySet(domain=d, mf=mu)

However, to actually create an object in a inherited hierarchy, we actually
have to declare a new class, unless we have an abstract factory...

Also, ideally we want fuzzy sets to be a generalization/extention of other,
crisp sets.  So the concrete class should reflect this:

  class RealDomainFuzzySet(float): ...

or

  class DiscreteDomainFuzzySet(set): ...

http://stackoverflow.com/questions/456672/class-factory-in-python
  

