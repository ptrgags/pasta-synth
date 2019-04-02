from mathutils import Vector
from mathutils import Matrix

class XForm:
    def transform(self, point):
        """
        Transform the point
        """
        raise NotImplementedError

    def jacobian(self, point):
        """
        Partial Derivatives of the transformation. If this is defined,
        this XForm can be used to transform Paths too!

        Return a matrix where the rows represent which component
        and the columns represent which derivative
        """
        raise NotImplementedError

class Scale(XForm):
    def __init__(self, sx, sy, sz):
        self.sx = sx
        self.sy = sy
        self.sz = sz

    def transform(self, point):
        return Vector((
            point.x * self.sx,
            point.y * self.sy,
            point.z * self.sz))

    def jacobian(self, point):
        return Matrix((
            (self.sx, 0.0, 0.0),
            (0.0, self.sy, 0.0),
            (0.0, 0.0, self.sz)))

class Translate(XForm):
    def __init__(self, offset):
        self.offset = offset

    def transform(self, point):
        return point + self.offset

    def jacobian(self, point):
        """
        Since translation is just adding a constant, no volume scaling
        occurs so the jacobian is the identity
        """
        return Matrix((
            (1, 0, 0),
            (0, 1, 0),
            (0, 0, 1)))

class SuperScale(XForm):
    """
    Transformation that turns a unit circle into a unit superellipse with
    parameters n and m:

    x' = sgn(x)|x|^(2/n)
    y' = sgn(y)|y|^(2/m)
    z' = sgn(z)|z|^(2/p)

    The 2 in the exponent is because 2 is the "center" of parameter space;
    2 produces a circle
    >2 defines squarish circles
    <2 defines star-like shapes
    """
    def __init__(self, n=2.0, m=2.0, p=2.0):
        self.n = n
        self.m = m
        self.p = p

    def transform(self, point):
        x = self.superfunc(point.x, self.n)
        y = self.superfunc(point.y, self.m)
        z = self.superfunc(point.z, self.p)
        return Vector((x, y, z))

    def jacobian(self, point):
        """
        Since the transform does not have any cross-dependence of
        components, we have a diagonal matrix
        """
        xx = self.superfunc_deriv(point.x, self.n)
        yy = self.superfunc_deriv(point.y, self.m)
        zz = self.superfunc_deriv(point.z, self.p)
        return Matrix((
            (xx, 0, 0),
            (0, yy, 0),
            (0, 0, zz)))

    @classmethod
    def sgn(cls, x):
        """
        Sign function
        """
        if x > 0.0:
            return 1.0
        elif x < 0.0:
            return -1.0
        else:
            return 0.0

    @classmethod
    def superfunc(cls, x, n):
        """
        This function takes x^(2/n) and forces it to be an odd functionn

        superfunc(x, n) = sgn(x)|x|^(2/n)
        """
        return cls.sgn(x) * abs(x) ** (2.0 / n)

    @classmethod
    def superfunc_deriv(cls, x, n):
        """
        The derivative for the super scaling function above is not well
        defined, since it is undefined at the origin. The closest you can
        get is:

        superfunc'(x, n) = delta(x)|x|^(2/n) + (2/n) |x|^(2/n - 1)

        Normally the first term is 0, but it is undefined at the origin, 
        as it becomes inf * 0. In these cases, a nan is returned to
        """ 
        # If x is exactly at 0.0, return nan and let the caller decide
        # This handles the first term, since it is 0 except when x == 0
        if x == 0.0:
            print("Warning: superfunc_deriv() evaluated at 0")
            return 1.0
            #return float('nan')

        # Compute the second term.
        return (2.0 / n) * abs(x) ** (2.0 / n - 1.0)
