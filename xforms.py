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
