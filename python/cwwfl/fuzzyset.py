#!/usr/bin/python

from __future__ import division
import numbers
import numpy as np
import matplotlib.pyplot as plt

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
    def __and__(self,other):
        fs = FuzzySet(mf=lambda x: min(self(x),other(x)))
        return fs
    def __or__(self,other):
        fs = FuzzySet(mf=lambda x: max(self(x),other(x)))
        return fs

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
class TrapezoidalFs(RealDomainFs):
    def __init__(self,mf):
        FuzzySet.__init__(self,mf)
    # see http://stackoverflow.com/questions/456672/class-factory-in-python
    @classmethod  
    def _is_concrete_fs_for(cls,mf=None):
        return isinstance(mf, TrapezoidalMf)

# Type-2 fuzzy sets may require refactoring to make a clean object heirarchy
# for now, they don't derive from fuzzy set, but IT2 FS's are composed of
# trapezoidal FSs
class intervalType2FS(object):
    def __init__(self,umf=None,lmf=None):
        self.umf = umf
        self.lmf = lmf
        
    def __repr__(self):
        return "IntervalType2FS(umf=%s,lmf=%s)" % (self.umf,
                                                   self.lmf)



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
        self.a = a
        self.b = b
        self.c = c
        def func(x):
            if x < a: return 0
            if x > b: return 0
            if x <= c: return (x-a)/(c-a)
            if x <= b: return (b-x)/(b-c)
        Mf.__init__(self,f=func)

    def __repr__(self): 
        return "TriangularMf(%d,%d,%d)" % (self.a,
                                           self.b,
                                           self.c)


class TrapezoidalMf(Mf):
    def __init__(self,a,b,c,d,e=1):
        """a is the lower x-bound, b is the lower top shelf, and upper top
        shelf, d is the upper x-bound, and e is the height (default=1)"""
        self.a = a 
        self.b = b 
        self.c = c 
        self.d = d 
        self.e = e

        def func(x):
            if x < a: return 0         # less than support
            if a <= x <= b:            # on the rising side
                if b-a ==0:
                    return 0
                else:
                    return e/(b-a)*(x-a) 
            if b <= x <= c: return e   # on the top shelf, (e.g. next to patron silver j/k)
            if c <= x <= d:            # on the decreasing side
                if d-c==0:
                    return 0
                else:
                    return e - e/(d-c)*(x-c) 
            if x > d: return 0         # greater than support
            else: return Exception()
        Mf.__init__(self,f=func)

        
    def __repr__(self): 
        return "TrapezoidalMf(%d,%d,%d,%d,%d)" % (self.a,
                                                  self.b,
                                                  self.c,
                                                  self.d,
                                                  self.e)


def plotIT2FS(fs,r=(0,100), label=None):
    #if isinstance(fs,intervalTypeTwoFuzzySet):
    #    raise NotImplemented()
    fig = plt.figure()
    #fig.suptitle(unicode(self.stimulus,"utf8","replace"))
    fig.suptitle(label)
    x = np.linspace(r[0],r[1],201)
    ax1 = fig.add_subplot(111)
    #ax2 = fig.add_subplot(121,sharex=ax1)
    #ax3 = fig.add_subplot(133,sharex=ax1)
    ax1.fill_between(x,
                         map(fs.umf, x),
                         map(fs.lmf, x))
    ax1.set_xlabel('Domain')
    ax1.set_ylabel('Membership Grade')
    #ax1.stem([50],[1], linefmt='r')
    plt.hold(True)
    #plt.show()
    
    return plt

def plotIT2FS_old(fs,r=(0,100), label=None):
    #if isinstance(fs,intervalTypeTwoFuzzySet):
    #    raise NotImplemented()
    try:
        umf = fs[0:4] #note slice is end exclusive
        lmf = fs[4:] 
        plt.plot(umf,[0,1,1,0])
        plt.plot(lmf[0:4],[0,lmf[4],lmf[4],0])
        plt.show()
    except IndexError as e:
        print e, fs
    

if __name__ == '__main__':
    #fs = FuzzySet()
    #fs = TriangularT1FSAtZero()
    #print fs(.1)
    fs1 = FuzzySet(lambda x: max(1-abs(x),0))    #fs centered at 0
    fs2 = FuzzySet(lambda x: max(1-abs(x-1),0))  #fs centered at 1
    print fs1(.1)
    print fs2(.1)
    if .1 in fs1:
        print "yes", .1 in fs1
    
