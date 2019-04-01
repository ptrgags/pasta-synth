from mathutils import Vector

class XForm:
    def transform(self, point):
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

class Translate(XForm):
    def __init__(self, offset):
        self.offset = offset

    def transform(self, point):
        return point + self.offset

class SuperScale(XForm):
    """
    Transformation that turns a unit circle into a unit superellipse with
    parameters n and m:

    x' = sgn(x)|x|^(2/n)
    y' = sgn(y)|y|^(2/m)
    z' = z 

    The 2 in the exponent is because 2 is the "center" of parameter space;
    2 produces a circle
    >2 defines squarish circles
    <2 defines star-like shapes
    """
    def __init__(self, n, m):
        self.n = n
        self.m = m

    def transform(self, point):
        x = self.superfunc(point.x, self.n)
        y = self.superfunc(point.y, self.m)
        z = point.z
        return Vector((x, y, z))

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
        superfunc(x, m) = sgn(x)|x|^(2/n)
        """
        return cls.sgn(x) * abs(x) ** (2.0 / n)
