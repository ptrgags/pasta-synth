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
