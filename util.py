import bpy
import bmesh

def link_mesh(name, bm):
    """
    Create a Blender object + and a mesh to go with it. the mesh
    has vertices loaded from a bmesh. The bmesh is freed at the end
    """
    # Add the mesh to the scene
    mesh = bpy.data.meshes.new(name + '_mesh')
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.objects.link(obj)

    bm.to_mesh(mesh)
    bm.free()

def lerp(params, t):
    """
    Linearly interpolate between two values

    params is a tuple of values (initial, final) and 
    t is a parameter from 0.0 to 1.0

    the initial/final values must support scalar multiplication and be closed
    under addition
    """
    initial, final = params
    return initial * (1.0 - t) + final * t

def loglerp(params, t):
    """
    Similar to lerp() above, but this time the parameter is used as an
    exponent.

    The parameters must support exponentiation by a float and multiplication
    """
    initial, final = params
    return initial ** (1.0 - t) * final ** (t)
    
