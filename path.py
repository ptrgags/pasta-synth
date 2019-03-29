from mathutils import Vector

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
