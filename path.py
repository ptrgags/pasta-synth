import math
import util

from mathutils import Vector
from mathutils import Matrix

class Path:
    """
    Parametric curve for extrusion
    """
    def position(self, v):
        raise NotImplementedError

    def tangent(self, v):
        """
        Return the unit tangent of the curve
        df/dv
        """
        raise NotImplementedError

    def normal(self, v):
        """
        Return the unit normal

        d^2f/dt^2
        """
        raise NotImplementedError

    def binormal(self, v):
        """
        Return the unit binormal

        B = T cross N
        """
        T = self.tangent(v)
        N = self.normal(v)
        return T.cross(N)

    def frenet_frame(self, v):
        """
        Package the tangent, normal and binormal directions up into
        a tuple
        """
        T = self.tangent(v)
        N = self.normal(v)
        B = self.binormal(v)
        return (T, N, B)

class Line(Path):
    def __init__(self, start, end):
        self.start = start
        self.end = end

    def position(self, v):
        return self.start * (1.0 - v) + self.end * v

    def tangent(self, v):
        direction = self.end - self.start
        direction.normalize()
        return direction

    def normal(self, v):
        """
        The normal for a line is technically 0, since there is no curvature
        so let's pick whichever direction points to the "right" of the
        curve using the up direction.
        """
        T = self.tangent(v)
        up = Vector((0.0, 0.0, 1.0))
        direction = up.cross(T)
        direction.normalize()

        # TODO: Handle the case when the tangent is pointing upwards or
        # downwards
        return direction

class Helix(Path):
    """
    Helical path around the z-axis with customizable start/end heights 
    and angles
    """
    def __init__(self, heights, angles):
        """
        heights: (z0, zf) (bottom and top heights)
        angles: (phi0, phif) (start and stop angle in radians.)

        For example, for a helix with 4 loops from -1 to 1 in the z direction
        would have:

        heights: (-1, 1)
        angles: (0, 4 * pi)
        """
        self.heights = heights
        self.angles = angles

    def position(self, v):
        """
        Position on the helix:

        x = cos(phi(v))
        y = sin(phi(v))
        z = z(v)

        phi(v) = lerp(angles, v)
        z(v) = lerp(heights, v)
        """
        # The height is a linear interpolation of the two heights
        z = util.lerp(self.heights, v)

        # For x and y, the angle gets lerp-ed
        phi = util.lerp(self.angles, v)
        x = math.cos(phi)
        y = math.sin(phi)
        return Vector((x, y, z))

    def tangent(self, v):
        """
        The tangent can be found by taking the derivative of
        the position:

        x' = -sin(phi(v))phi'(v) = (phif - phi0) * -sin(phi(v))
        y' = cos(phi(v))phi'(v) = (phif - phi0) * cos(phi(v))
        z' = z'(v) = zf - z0

        Then normalize the vector (x', y', z') to get the unit direction.
        """
        # the slope in the z direction is simply the change in height
        # TODO: Refactor to use lerp()
        z0, zf =  self.heights
        dz = zf - z0

        # Same thing for the angle
        phi0, phif = self.angles
        phi = (1.0 - v) * phi0 + v * phif
        dphi = phif - phi0

        # The rest is the chain rule from calculus
        dx = -math.sin(phi) * dphi
        dy = math.cos(phi) * dphi

        T = Vector((dx, dy, dz))
        T.normalize()
        return T

    def normal(self, v):
        """
        The normal direction can be found from the second derivative
        of position

        x'' = -phi'(v)^2 * cos(phi(v)) = -(phif - phi0)^2 * cos(phi(v))
        y'' = -phi'(v)^2 * sin(phi(v)) = -(phif - phi0)^2 * sin(phi(v))
        z'' = 0 (z' is constant)

        Again, normalize to get the unit normal.
        """
        # The height changes linearly, so it has no vertical acceleration
        ddz = 0

        # Handle the coefficient and angle
        phi0, phif = self.angles
        phi = (1.0 - v) * phi0 + v * phif
        dphi = phif - phi0
        dphi_sqr = dphi * dphi

        ddx = -dphi_sqr * math.cos(phi)
        ddy = -dphi_sqr * math.sin(phi)

        N = Vector((ddx, ddy, ddz))
        N.normalize()
        return N

class Transformed(Path):
    """
    Transform the path with an XForm
    """
    def __init__(self, path, xform):
        """
        path is the path to wrap
        xform is either a callable f(pos, v): XForm or an XForm
        """
        self.path = path
        self.xform = xform

    def get_xform(self, pos, v):
        """
        If xform is a callable, call it to get a Xform. Otherwise, assumme
        it is an XForm
        """
        if callable(self.xform):
            return self.xform(pos, v)
        else:
            return self.xform
    
    def position(self, v):
        pos = self.path.position(v)

        xform = self.get_xform(pos, v)
        return xform.transform(pos)

    def tangent(self, v):
        pos = self.path.position(v)
        T = self.path.tangent(v)

        xform = self.get_xform(pos, v)
        transformed = xform.jacobian(pos) * T
        transformed.normalize()
        return transformed

    def normal(self, v):
        pos = self.path.position(v)
        N = self.path.normal(v)

        # Try to transform the normals with the inverse transpose of the
        # jacobian. However, if this fails at a point due to non-continuous
        # derivatives, fallback to the identity transformation
        I = Matrix((
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1)))

        xform = self.get_xform(pos, v)
        jac_inv_T = xform.jacobian(pos)
        jac_inv_T.invert(I)
        jac_inv_T.transpose()

        transformed = jac_inv_T * N
        transformed.normalize()
        return transformed
