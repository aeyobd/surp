# This is a coordinate class used 
# to define the current figure's cooridnate system
from mpl_toolkits.axes_grid1.axes_size import Fixed, Scaled
from functools import total_ordering


class Coordinate():
    def __init__(self, x, y, unit="in"):
        self.unit = unit
        self.x = x
        self.y = y

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y
    
    @x.setter
    def x(self, val):
        self._x = val

    @y.setter
    def y(self, val):
        self._y = val

@total_ordering
class Length():
    _IN = 1.0 #inches are defined as internal standard
    _CM = 1.0/2.54
    _relative = False

    def __init__(self, l, unit="in"):
        self._x = l * self.unit(unit)

    def unit(self, u):
        if u=="in":
            return self._IN
        elif u=="cm":
            return self._CM
        elif u=="relative":
            self._relative = True
            return 1

    @property
    def relative(self):
        return self._relative
    
    @property
    def mpl(self):
        return Fixed(self._x)

    @property
    def inch(self):
        return self._x

    @property
    def cm(self):
        return self.inch / self._CM
    
    def __add__(self, b):
        self._x += b._x
        return self

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.inch) + " in."

    def __eq__(self, other):
        return self.inch == other.inch

    def __lt__(self, other):
        return self.inch < other.inch

    def copy(self):
        return Length(self.inch)

    def __mul__(self, other):
        if isinstance(other, Coordinate):
            l = self.inch * other.inch
            return Length(l)
        else:
            l = self.inch * other
            return Length(l)

    def __rmul__(self, other):
        return self * other


