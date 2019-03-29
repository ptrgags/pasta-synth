from mathutils import Vector

class ExtrudedSurface:
    """
    Extrude a cross section along
    a parametric path.
    """
    def __init__(self, cross_section, path):
        self.cross_section = cross_section
        self.path = path

    def position(self, u, v):
        # point on the path at parameter value v between 0 and 1
        path_pos = self.path.position(v)

        # Tangent, normal and binormal directions at this point on the path
        T, N, B = self.path.frenet_frame(v)

        # Calculate the cross section shape but express it in the
        # frenet frame of the path at this point.
        # x corresponds with the normal, y the binormal, and z the tangent
        # direction
        cs_position = self.cross_section.position(u, v)
        cs_euclidean = N * cs_position.x + B * cs_position.y + T * cs_position.z

        # Add the two vectors to get a point on the extruded surface
        return cs_euclidean + path_pos
