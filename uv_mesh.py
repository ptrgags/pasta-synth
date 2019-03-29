import bpy
import bmesh
import util
import logging

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

def make_uv_mesh(u_quads, v_quads):
    bm = bmesh.new()
    
    # Make an empty grid to store the vertices
    verts = [[None] * (v_quads + 1) for i in range(u_quads + 1)]
    
    for (i, j), (u, v) in make_uvs(u_quads, v_quads):
        verts[i][j] = bm.verts.new((u, v, 0))    
    
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

bm = make_uv_mesh(10, 12)
util.link_mesh('Surface', bm)