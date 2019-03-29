import bpy
import bmesh
from mathutils import Vector

import util
import cross_section
import path
from extruded_surface import ExtrudedSurface

def make_uvs(u_quads, v_quads):
    """
    Create a UV mesh with u_quads quads in the u direction
    and v_quads quads in the v direction

    This returns a generator of (i, j) and (u, v) pairs.
    """
    for i in range(u_quads + 1):
        u = i / u_quads
        for j in range(v_quads + 1):
            v = j / v_quads
            yield (i, j), (u, v)

def make_uv_mesh(u_quads, v_quads, surface):
    """
    Make a parametric mesh with u_quads in the u_direction, v_quads in the
    v direction, and a shape that is defined by the ExtrudedSurface
    passed in.
    """
    bm = bmesh.new()

    # Make an empty grid to store the vertices
    verts = [[None] * (v_quads + 1) for i in range(u_quads + 1)]

    for (i, j), (u, v) in make_uvs(u_quads, v_quads):
        pos = surface.position(u, v)
        verts[i][j] = bm.verts.new(pos)

    for i in range(u_quads):
        for j in range(v_quads):
            face_verts = [
                verts[i][j],
                verts[i + 1][j],
                verts[i + 1][j + 1],
                verts[i][j + 1]
            ]
            bm.faces.new(face_verts)
    return bm

cs = cross_section.Circle()
path = path.Line(Vector((-2, 0, 0)), Vector((2, 0, 0)))
surf = ExtrudedSurface(cs, path)

bm = make_uv_mesh(24, 10, surf)
util.link_mesh('Surface', bm)
