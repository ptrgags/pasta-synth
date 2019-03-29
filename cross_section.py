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
