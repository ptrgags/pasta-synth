import math

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

    @property
    def inverse(self):
        """
        If this transformation has an inverse, override this method
        and return an instance of the inverse XForm.
        """
        return None

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

    @property
    def inverse(self):
        return Scale(1.0 / self.sx, 1.0 / self.sy, 1.0 / self.sz)

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

    @property
    def inverse(self):
        return Translate(-self.offset)

class RotateZ(XForm):
    def __init__(self, angle):
        self.angle = angle

    def transform(self, point):
        c = math.cos(self.angle)
        s = math.sin(self.angle)

        x = point.x * c - point.y * s
        y = point.x * s + point.y * c
        z = point.z
        return Vector((x, y, z))

    def jacobian(self, point):
        c = math.cos(self.angle)
        s = math.sin(self.angle)
        return Matrix((
            (c, -s, 0.0),
            (s, c, 0.0),
            (0, 0, 1)))

    @property
    def inverse(self):
        return RotateZ(-self.angle)

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
            return 1.0

        # Compute the second term.
        return (2.0 / n) * abs(x) ** (2.0 / n - 1.0)

class CartesianToCylindrical(XForm):
    """
    Convert (x, y, z) to (s, phi, z)
    """
    def transform(self, point):
        x = point.x
        y = point.y

        s = math.hypot(y, x)
        phi = math.atan2(y, x)
        z = point.z

        return Vector((s, phi, z))

    def jacobian(self, point):
        x = point.x
        y = point.y

        s = math.hypot(y, x)
        s_sqr = x * x + y * y

        return Matrix((
            (x / s, y / s, 0),
            (-y / s_sqr, x / s_sqr, 0),
            (0, 0, 1)))

    @property
    def inverse(self):
        return CylindricalToCartesian()

class CylindricalToCartesian(XForm):
    """
    Convert (s, phi, z) to (x, y, z)
    """
    def transform(self, point):
        s = point.x
        phi = point.y
        z = point.z

        x = s * math.cos(phi)
        y = s * math.sin(phi)

        return Vector((x, y, z))

    def jacobian(self, point):
        s = point.x
        phi = point.y

        cp = math.cos(phi)
        sp = math.sin(phi)

        return Matrix((
            (cp, -s * sp, 0),
            (sp, s * cp, 0),
            (0, 0, 1)))

    @property
    def inverse(self):
        return CartesianToCylindrical()

class Sinusoidal(XForm):
    """
    Apply sin(x) to each component.

    Apply a Scale/Translation before Sinusoidal to control frequency
    and phase

    Apply a Scale/Translation after Sinusoidal to control amplitude
    """
    def transform(self, point):
        x = math.sin(point.x)
        y = math.sin(point.y)
        z = math.sin(point.z)
        return Vector((x, y, z))

    def jacobian(self, point):
        xx = math.cos(point.x)
        yy = math.cos(point.y)
        zz = math.cos(point.z)
        return Matrix((
            (xx, 0, 0),
            (0, yy, 0),
            (0, 0, zz)))

class Conjugated(XForm):
    """
    Conjugate XForm A by an invertible 
    XForm B by applying:

    C = B * A * B^(-1)

    This is useful for changing coordinate systems. For example, to apply
    a radial scaling, conjugate by a transformation to Cylindrical coordinates
    (well, in this case a 
    Conjugated(Scale(scale_factor, 1, 1), CylindricalToCartesian())
    """
    def __init__(self, original, conjugate_by):
        self.A = original
        self.B = conjugate_by
        self.B_inv = conjugate_by.inverse

        if self.B_inv is None:
            raise ValueError("conjugate_by must have an inverse")

    def transform(self, point):
        change_coords = self.B_inv.transform(point)
        xformed = self.A.transform(change_coords)
        restore_coords = self.B.transform(xformed)  
        return restore_coords
         
    def jacobian(self, point):
        """
        Since a conjugation is just a composition of 3 transformations,
        multipy the jacobians to get the overall 
        """
        jac_B = self.B.jacobian(point)
        jac_A = self.A.jacobian(point)
        jac_B_inv = self.B_inv.jacobian(point)

        return jac_B * jac_A * jac_B_inv

    @classmethod
    def cylindrical_xform(cls, xform):
        """
        This is a common transformation to get radial scaling. 
        So here is a shortcut.
        """
        # Note that we pass in the cylindrical -> cartesian as the
        # A transform since the composition is done
        # right to left: ABA^(-1)
        return cls(xform, CylindricalToCartesian)
