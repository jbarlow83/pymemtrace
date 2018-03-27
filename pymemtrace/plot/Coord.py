#!/usr/bin/env python
# MIT License
# 
# Copyright (c) 2017 paulross
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# 
# Paul Ross: apaulross@gmail.com

__author__  = 'Paul Ross'
__date__    = '2011-07-10'
__rights__  = 'Copyright (c) 2008-2017 Paul Ross'

#import logging
#import sys
import collections

class ExceptionCoord(Exception):
    """Exception class for representing Coordinates."""
    pass

class ExceptionCoordUnitConvert(ExceptionCoord):
    """Exception raised when converting units."""
    pass

#: Base units
BASE_UNITS = 'px'

#: Map of conversion factors, base unit is pixels.
UNIT_MAP = {
    None        : 1.0,  # Implied base units i.e. default
    'px'        : 1.0,
    'pt'        : 1.0,  # Actual base units i.e. BASE_UNITS
    'pc'        : 12.0,
    'in'        : 72.0,
    'cm'        : 72.0/2.54,
    'mm'        : 72.0/25.4,
}

#: Formatting strings for writing attributes.
#: We are trying not to write 3.999999999mm here!
UNIT_MAP_DEFAULT_FORMAT = {
    None        : '%d',  # Implied base units i.e. default
    'px'        : '%d',
    'pt'        : '%d',  # Actual base units i.e. BASE_UNITS
    'pc'        : '%.2f',
    'in'        : '%.3f',
    'cm'        : '%.2f',
    'mm'        : '%.1f',
}

#: Map of formatting strings for value and units e.g. to create '0.667in' from (2.0 / 3.0, 'in')
UNIT_MAP_DEFAULT_FORMAT_WITH_UNITS = {__k : UNIT_MAP_DEFAULT_FORMAT[__k] + '%s' for __k in UNIT_MAP_DEFAULT_FORMAT}

def units():
    """Returns the unsorted list of acceptable units."""
    return UNIT_MAP.keys()

def convert(val, unitFrom, unitTo):
    """Convert a value from one set of units to another.

    :param val: The value
    :type val: ``float, int``

    :param unitFrom: The initial units.
    :type unitFrom: ``NoneType, str``

    :param unitTo: The new units.
    :type unitTo: ``str``

    :returns: ``float,int`` -- The value in the new units.
    """
    if unitFrom == unitTo:
        return val
    try:
        return val * UNIT_MAP[unitFrom] / UNIT_MAP[unitTo]
    except KeyError:
        if unitFrom in UNIT_MAP:
            raise ExceptionCoordUnitConvert('Unsupported units %s' % unitTo)
        raise ExceptionCoordUnitConvert('Unsupported units %s' % unitFrom)

class Dim(collections.namedtuple('Dim', 'value units',)):
    """Represents a dimension as an engineering value i.e. a number and units.""" 
    __slots__ = ()

    def scale(self, factor):
        """Returns a new Dim() scaled by a factor, units are unchanged."""
        return self._replace(value=self.value*factor)

    def convert(self, u):
        """Returns a new Dim() with units changed and value converted."""
        return self._replace(value=convert(self.value, self.units, u), units=u)

    def __str__(self):
        #return 'Dim: %s (%s)' % (self.value, self.units)
        return 'Dim(%s%s)' % (self.value, self.units)

    def __add__(self, other):
        """Overload self+other, returned result has the sum of self and other.
        The units chosen are self's unless self's units are None in which case other's
        units are used (if not None)."""
        try:
            if self.units is None and other.units is not None:
                myVal = other.value + convert(self.value, self.units, other.units)
                return Dim(myVal, other.units)
            else:
                myVal = self.value + convert(other.value, other.units, self.units)
                return Dim(myVal, self.units)
        except AttributeError:
            return NotImplemented

    def __sub__(self, other):
        """Overload self-other, returned result has the difference of self and
        other. The units chosen are self's unless self's units are None in
        which case other's units are used (if not None)."""
        try:
            if self.units is None and other.units is not None:
                myVal = convert(self.value, self.units, other.units) - other.value
                return Dim(myVal, other.units)
            else:
                myVal = self.value - convert(other.value, other.units, self.units)
                return Dim(myVal, self.units)
        except AttributeError:
            return NotImplemented

    def __mul__(self, other):
        """Overload self * other, other is a float or int."""
        return Dim(self.value * other, self.units)

    def __rmul__(self, other):
        """Overload self * other, other is a float or int."""
        return Dim(self.value * other, self.units)

    def __truediv__(self, other):
        """Overload self / other, other is a float or int."""
        return Dim(self.value / other, self.units)

    def __rtruediv__(self, other):
        """Overload self / other, other is a float or int."""
        return Dim(self.value / other, self.units)

    def __iadd__(self, other):
        """Addition in place, value of other is converted to my units and added."""
        # Use __add__()
        self = self + other
        return self

    def __isub__(self, other):
        """Subtraction in place, value of other is subtracted."""
        # Use __sub__()
        self = self - other
        return self

    def __imul__(self, other):
        """Overload self \*= other, other is a float or int."""
        self = self * other
        return self

    def __itruediv__(self, other):
        """Overload self /= other, other is a float or int."""
        self = self / other
        return self

    def __lt__(self, other):
        """Returns true if self value < other value after unit conversion."""
        return (self.value < convert(other.value, other.units, self.units))

    def __le__(self, other):
        """Returns true if self value <= other value after unit conversion."""
        return (self.value <= convert(other.value, other.units, self.units))

    def __eq__(self, other):
        """Returns true if self value == other value after unit conversion."""
        return (self.value == convert(other.value, other.units, self.units))

    def __ne__(self, other):
        """Returns true if self value != other value after unit conversion."""
        return (self.value != convert(other.value, other.units, self.units))

    def __gt__(self, other):
        """Returns true if self value > other value after unit conversion."""
        return (self.value > convert(other.value, other.units, self.units))

    def __ge__(self, other):
        """Returns true if self value >= other value after unit conversion."""
        return (self.value >= convert(other.value, other.units, self.units))

# All of these take a Dim() for each member
#
# This describes the size of a box, its members are Dim() objects
#Box         = collections.namedtuple('Box', 'width depth',)
# Padding around another object that forms the Bounding Box
# All 4 attributes are Dim() objects
#Pad         = collections.namedtuple('Pad', 'prev next parent child',)

class Box(collections.namedtuple('Box', 'width depth',)):
    __slots__ = ()
    def __str__(self):
        """Stringifying."""
        return 'Box(width=%s, depth=%s)' % (self.width, self.depth)    

class Pad(collections.namedtuple('Pad', 'prev next parent child',)):
    """Padding around another object that forms the Bounding Box.
    All 4 attributes are Dim() objects"""
    __slots__ = ()
    def __str__(self):
        """Stringifying."""
        return 'Pad(prev=%s, next=%s, parent=%s, child=%s)' \
            % (self.prev, self.next, self.parent, self.child)
    
class Pt(collections.namedtuple('Pt', 'x y',)):
    """A point, an absolute x/y position on the plot area.
    Members are Coord.Dim()."""
    __slots__ = ()
    def __eq__(self, other):
        """Comparison."""
        return self.x == other.x and self.y == other.y

    def __str__(self):
        """Stringifying."""
        return 'Pt(x=%s, y=%s)' \
            % (self.x, self.y)
        #return 'Pt(x=%s %s, y=%s %s)' \
        #    % (self.x.value, self.x.units, self.y.value, self.y.units)

    def convert(self, u):
        """Returns a new Pt() with units changed and value converted."""
        return self._replace(x=self.x.convert(u), y=self.y.convert(u))

    def scale(self, factor):
        """Returns a new Pt() scaled by a factor, units are unchanged."""
        return self._replace(x=self.x.scale(factor), y=self.y.scale(factor))

###############################################
# Section: Helper functions for object creation
###############################################
def baseUnitsDim(theLen):
    """Returns a Coord.Dim() of length and units BASE_UNITS.

    :param theLen: Length.
    :type theLen: ``float, int``

    :returns: :py:class:`cpip.plot.Coord.Dim([float, str])` -- A new dimension of theLen in base units.
    """
    return Dim(theLen, BASE_UNITS)

def zeroBaseUnitsDim():
    """Returns a Coord.Dim() of zero length and units BASE_UNITS.

    :returns: :py:class:`cpip.plot.Coord.Dim([float, str])` -- A new dimension of zero.
    """
    return baseUnitsDim(0.0)

def zeroBaseUnitsBox():
    """Returns a Coord.Box() of zero dimensions and units BASE_UNITS."""
    return Box(
               zeroBaseUnitsDim(),
               zeroBaseUnitsDim(),
        )

def zeroBaseUnitsPad():
    """Returns a Coord.Pad() of zero dimensions and units BASE_UNITS."""
    return Pad(
               zeroBaseUnitsDim(),
               zeroBaseUnitsDim(),
               zeroBaseUnitsDim(),
               zeroBaseUnitsDim(),
        )

def zeroBaseUnitsPt():
    """Returns a Coord.Dim() of zero length and units BASE_UNITS.

    :returns: ``cpip.plot.Coord.Pt([cpip.plot.Coord.Dim([float, str]), cpip.plot.Coord.Dim([float, str])])`` -- A new  point with the values [0, 0].
    """
    return Pt(zeroBaseUnitsDim(), zeroBaseUnitsDim())

def newPt(theP, incX=None, incY=None):
    """Returns a new Pt object by incrementing existing point incX, incY
    that are both Dim() objects or ``None``.

    :param theP: The initial point.
    :type theP: ``cpip.plot.Coord.Pt([cpip.plot.Coord.Dim([float, str]), cpip.plot.Coord.Pt([cpip.plot.Coord.Dim([float, str])])``

    :param incX: Distance to move in the x axis.
    :type incX: ``NoneType, cpip.plot.Coord.Dim([float, str]), cpip.plot.Coord.Dim([int, str])``

    :param incY: Distance to move in the y axis.
    :type incY: ``NoneType, cpip.plot.Coord.Dim([float, str]), cpip.plot.Coord.Dim([int, str])``

    :returns: ``cpip.plot.Coord.Pt([cpip.plot.Coord.Dim([float, str]), cpip.plot.Coord.Dim([float, str])])`` -- The new point.
    """
    newX = theP.x
    if incX is not None:
        newX += incX
    newY = theP.y
    if incY is not None:
        newY += incY
    return Pt(x=newX, y=newY)

def convertPt(theP, theUnits):
    """Returns a new point with the dimensions of theP converted to theUnits.

    TODO: Deprecate this.
    """
    return Pt(
        x=Dim(convert(theP.x.value, theP.x.units, theUnits), theUnits),
        y=Dim(convert(theP.y.value, theP.y.units, theUnits), theUnits),
        )
    
###########################################
# End: Helper functions for object creation
###########################################

#---- Scaling functions

#: offset scale are Coord.Dim() objects
#: Scale is computed as a multiplier so Dim = offset + scale * value
OffsetScale = collections.namedtuple('OffsetScale', ['offset', 'scale'])

def offset_scale(coord_min, coord_max, value_min, value_max):
    """
    coord_min, coord_max are Dim objects.
    value_min, value_max are floats or ints.
    
    Returns a named tuple::
    
        OffsetScale(offset, scale)
    
    :raises: ``ZeroDivisionError`` if ``value_min - value_max`` is zero.
    """
    # delta d / delta v, the slope, a Dim object.
    scale = (coord_max - coord_min) / (value_max - value_min)
    # The intercept as as Dim object
    offset = coord_min - scale * value_min
    return OffsetScale(offset, scale)

def dim_from_offset_scale(value, offset_scale):
    """
    value is a float or int.
    offset_scale is a named tuple::
    
        OffsetScale(offset, scale)
    
    Returns ``offset + scale * value``
    """
    return offset_scale.offset + offset_scale.scale * value

#---- END: Scaling functions

