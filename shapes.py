from mathutils import Vector

import cross_section
import path
import uv_mesh
import util
from extruded_surface import ExtrudedSurface

def cylinder(z0=Vector((-1, 0, 0)), zf=Vector((1, 0, 0)), u_res=24, v_res=10):
    cs = cross_section.Circle()
    line = path.Line(z0, zf)
    surf = ExtrudedSurface(cs, line)

    bm = uv_mesh.make_uv_mesh(u_res, v_res, surf)
    util.link_mesh('Cylinder', bm)
