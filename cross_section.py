import math
import operator
import functools

from mathutils import Vector

class CrossSection:
    """
    Parametric curve that represents
    a cross section of the surface
    """
    def position(self, u, v):
        """
        Given the u, v parameters, return a point on the cross-section

        u is the angle around the cross section curve. For example,
        for a circle, theta = 2 pi * u

        v is the parameter along the extrusion path. It is used
        for varying the cross-section at different parts of the path.

        Return a Vector where the x and y coordinates are in the plane of
        the cross section. the z coordinate should normally be 0.0, but it
        doesn't have to be ;)
        """
        raise NotImplementedError

class Line(CrossSection):
    """
    Line segment pointing along the x-axis starting at the origin
    """
    def position(self, u, v):
        x = u
        y = 0.0
        z = 0.0
        return Vector((x, y, z))

class Circle(CrossSection):
    """
    Circular cross section.
    """
    def position(self, u, v):
        theta = 2.0 * math.pi * u
        x = math.cos(theta)
        y = math.sin(theta)
        z = 0.0
        return Vector((x, y, z))

class Lissajous(CrossSection):
    """
    Lissajous curves: like the parametric equation for a circle but
    where the frequences are not the same in each direction:

    x = cos(a * theta)
    y = cos(b * theta)
    """
    def __init__(self, a, b):
        """
        a is the frequency in the x direction,
        b is the frequency in the y direction
        """
        self.a = a
        self.b = b

    def position(self, u, v):
        theta = 2.0 * math.pi * u

        x = math.cos(self.a * theta)
        y = math.sin(self.b * theta)
        z = 0.0
        return Vector((x, y, z))

class RoseCurve(CrossSection):
    def __init__(self, k):
        self.k = k

    def position(self, u, v):
        theta = 2.0 * math.pi * u
        radius = math.cos(self.k * theta)
        x = radius * math.cos(theta)
        y = radius * math.sin(theta)
        z = 0.0
        return Vector((x, y, z))

class Transformed(CrossSection):
    """
    Decorator that applies a transformation to a cross section
    """
    def __init__(self, original_cs, xform):
        """
        original_cs: the CrossSection to transform

        xform: either an XForm object or a function
            f(position, u, v) = an XForm object
        """
        self.original_cs = original_cs
        self.xform = xform

    def position(self, u, v):
        pos = self.original_cs.position(u, v)

        # If we have a callable, call it to get an xform. If we have a
        # constant xform, just use it.
        xform = self.xform(pos, u, v) if callable(self.xform) else self.xform
        return xform.transform(pos)

class Union(CrossSection):
    def __init__(self, cross_sections):
        self.cross_sections = cross_sections

    def position(self, u, v):
        N = len(self.cross_sections)
        section_int, section_frac = divmod(u * N, 1.0)
        section_int = int(section_int)

        try:
            cs = self.cross_sections[section_int]
            return cs.position(section_frac, v)
        except IndexError:
            cs = self.cross_sections[-1]
            return cs.position(1.0, v)

class Combine(CrossSection):
    """
    Combine multiple cross sections with a math function.
    """
    def __init__(self, operation=operator.add, *cross_sections):
        self.op = operation
        self.cross_sections = cross_sections
    
    def position(self, u, v):
        points = [cs.position(u, v) for cs in self.cross_sections]
        return functools.reduce(self.op, points)
