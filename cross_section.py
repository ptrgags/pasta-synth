import math
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

class Transformed(CrossSection):
    """
    Decorator that applies a transformation to a cross section
    """
    def __init__(self, original_cs, xform):
        self.original_cs = original_cs
        self.xform = xform

    def position(self, u, v):
        pos = self.original_cs.position(u, v)
        return self.xform.transform(pos)

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
