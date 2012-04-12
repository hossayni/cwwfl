#!/usr/bin/python

from __future__ import division
import numbers
#from interval import interval, inf, imath

# factory method
# see http://stackoverflow.com/questions/456672/class-factory-in-python
def CreateFuzzySet(mf=None):
    #for cls in FuzzySet.__subclasses__():
    for cls in itersubclasses(FuzzySet):
        if cls._is_concrete_fs_for(mf=mf):
            return cls(mf=mf)
    raise ValueError("no implementation matches mf=%s" % mf)

# http://code.activestate.com/recipes/576949-find-all-subclasses-of-a-given-class/
def itersubclasses(cls, _seen=None):
    """
    itersubclasses(cls)

    Generator over all subclasses of a given class, in depth first order.

    >>> list(itersubclasses(int)) == [bool]
    True
    >>> class A(object): pass
    >>> class B(A): pass
    >>> class C(A): pass
    >>> class D(B,C): pass
    >>> class E(D): pass
    >>> 
    >>> for cls in itersubclasses(A):
    ...     print(cls.__name__)
    B
    D
    E
    C
    >>> # get ALL (new-style) classes currently defined
    >>> [cls.__name__ for cls in itersubclasses(object)] #doctest: +ELLIPSIS
    ['type', ...'tuple', ...]
    """
    if not isinstance(cls, type):
        raise TypeError('itersubclasses must be called with '
                        'new-style classes, not %.100r' % cls)
    if _seen is None: _seen = set()
    try:
        subs = cls.__subclasses__()
    except TypeError: # fails only when cls is type
        subs = cls.__subclasses__(cls)
    for sub in subs:
        if sub not in _seen:
            _seen.add(sub)
            yield sub
            for sub in itersubclasses(sub, _seen):
                yield sub


# abstract base class 
class FuzzySet(object):
    def __init__(self,mf=None):
        self.mf = Mf(mf)
    def __call__(self,x):
        if self.mf == None:
            raise NotImplementedError("no membership function")
        return self.mf(x)
    def mf(self,x):
        return 1
    def __contains__(self,x):
        if self(x)>0:
            return self(x)
        else:
            return 0

    #subclasses should implement this
    #@classmethod  
    #def _is_concrete_fs_for(cls,mf=None,domain=None):
    #    return mf == None and domain == None

class RealDomainFs(FuzzySet,numbers.Real):
#class RealDomainFs(FuzzySet,float):
    def __call__(self,x):
        if self.mf == None:
            raise NotImplementedError("no membership function")
        if(not isinstance(x,numbers.Real)):
            raise TypeError("input %s does not match class %s "
                             % (self,x.__class__))
        return self.mf(x)

    def __abs__(self,other):
        raise NotImplementedError()
    def __add__(self,other):
        raise NotImplementedError()
    def __div__(self,other):
        raise NotImplementedError()
    def __eq__(self,other):
        raise NotImplementedError()
    def __float__(self,other):
        raise NotImplementedError()
    def __floordiv__(self,other):
        raise NotImplementedError()
    def __le__(self,other):
        raise NotImplementedError()
    def __lt__(self,other):
        raise NotImplementedError()
    def __mod__(self,other):
        raise NotImplementedError()
    def __mul__(self,other):
        raise NotImplementedError()
    def __neg__(self,other):
        raise NotImplementedError()
    def __pos__(self,other):
        raise NotImplementedError()
    def __pow__(self,other):
        raise NotImplementedError()
    def __radd__(self,other):
        raise NotImplementedError()
    def __rdiv__(self,other):
        raise NotImplementedError()
    def __rfloordiv__(self,other):
        raise NotImplementedError()
    def __rmod__(self,other):
        raise NotImplementedError()
    def __rmul__(self,other):
        raise NotImplementedError()
    def __rpow__(self,other):
        raise NotImplementedError()
    def __rtruediv__(self,other):
        raise NotImplementedError(self,other)
    def __truediv__(self,other):
        raise NotImplementedError()
    def __trunc__(self,other):
        raise NotImplementedError()

    @classmethod  
    def _is_concrete_fs_for(cls,mf=None,domain=None):
        return False #this is an abstract class

class TriangularFs(RealDomainFs):
    def __init__(self,mf):
        FuzzySet.__init__(self,mf)
    # see http://stackoverflow.com/questions/456672/class-factory-in-python
    @classmethod  
    def _is_concrete_fs_for(cls,mf=None):
        return isinstance(mf, TriangularMf)

class Mf(object):
    def __init__(self,f=None):
        self.f = f
        #self.support = interval([-inf,inf])
        #self.support = interval([0,10])
    #def checkMfSupport(self,fn):
        
    def __call__(self,x=None):
        return self.f(x)

class TriangularMf(Mf):
    def __init__(self,a,b,c):
        """a is the lower bound, b is the upper, and c is where the function
        equals 1"""
        def func(x):
            if x < a: return 0
            if x > b: return 0
            if x <= c: return (x-a)/(c-a)
            if x <= b: return (b-x)/(b-c)
        Mf.__init__(self,f=func)


if __name__ == '__main__':
    #fs = FuzzySet()
    #fs = TriangularT1FSAtZero()
    #print fs(.1)
    fs1 = FuzzySet(lambda x: max(1-abs(x),0))
    fs2 = FuzzySet(lambda x: max(1-abs(x-1),0))
    print fs1(.1)
    print fs2(.1)
    if .1 in fs1:
        print "yes", .1 in fs1
    fs3 = fs1 and fs2
    print fs3(.1)
    print fs3(-.1)
    
