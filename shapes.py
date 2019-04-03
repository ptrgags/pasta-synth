import math

from mathutils import Vector

import cross_section
import path
import uv_mesh
import util
import xforms
from extruded_surface import ExtrudedSurface

class ExtrudedShape:
    def __init__(self, u_res, v_res, **params):
        self.u_res = u_res
        self.v_res = v_res

        # Set up default parameters and update with what the user
        # passed in
        self.params = self.default_params
        self.params.update(params)

    @property
    def default_params(self):
        """
        If there are sensible defaullts, put them here
        """
        return {}

    def lerp_param(self, param_name, t):
        """
        A common pattern I use for defining parameters is specifying
        parameters as (initial, final) pairs and then interpolating them
        This is a shortcut for looking up the parameter and interpolating
        """
        param = self.params[param_name] 
        return util.lerp(param, t)

    def loglerp_param(self, param_name, t):
        """
        Samething, but with util.loglerp()
        """
        param = self.params[param_name]
        return util.loglerp(param, t)

    def build(self, name):
        cs = self.make_cross_section()
        pth = self.make_path()
        surf = ExtrudedSurface(cs, pth)

        bm = uv_mesh.make_uv_mesh(self.u_res, self.v_res, surf)
        util.link_mesh(name, bm)

    def make_cross_section(self):
        """
        Build the cross section, starting from a base shape and possibly
        applying transformations
        """
        raise NotImplementedError

    def make_path(self):
        """
        Make the path for extruding the shape
        Start from a basic path and apply transformations/concatenations to
        make the desired shape.
        """
        raise NotImplementedError

class Cylinder(ExtrudedShape):
    @property
    def default_params(self):
        return {
            # start and end of the path.
            'heights': (Vector((-1, 0, 0)), Vector((1, 0, 0))),
            # radius of the cross-section
            'radius': 1.0
        }

    def make_cross_section(self):
        """
        Circular cross section of user-defined radius
        """
        radius = self.params['radius']
        scale = xforms.Scale(radius, radius, 1.0)
        
        cs = cross_section.Circle()
        cs = cross_section.Transformed(cs, scale)
        return cs

    def make_path(self):
        """
        Extrude the circle along a line
        """
        z0, zf = self.params['heights']
        pth = path.Line(z0, zf)
        return pth

class SuperSeashell(ExtrudedShape):
    """
    My super-seashells family of parametric surfaces.
    """
    @property
    def default_params(self): 
        return {
            'coil_radius': (0.8, 0.0),
            'coil_logarithm': (0.0, 0.0),
            'coil_angle': (0.0, 8.0 * math.pi),
            'coil_z': (0, 1.25),
            'coil_p': (2.0, 2.0),
            'coil_q': (2.0, 2.0),
            'cross_section_radius': (0.3, 0.0),
            'cross_section_twist': (0.0, 0.0),
            'cross_section_m': (1.0, 1.0),
            'cross_section_n': (1.0, 1.0),
        }

    def make_cross_section(self):

        def make_superellipse(pos, u, v):
            m = self.loglerp_param('cross_section_m', v)
            n = self.loglerp_param('cross_section_n', v)
            return xforms.SuperScale(m, n,  2.0)

        def taper(pos, u, v):
            r = self.lerp_param('cross_section_radius', v)
            return xforms.Scale(r, r, 1)

        def twist(pos, u, v):
            twist_angle = self.lerp_param('cross_section_twist', v)
            return xforms.RotateZ(twist_angle) 

        cs = cross_section.Circle()
        cs = cross_section.Transformed(cs, make_superellipse)
        cs = cross_section.Transformed(cs, taper)
        cs = cross_section.Transformed(cs, twist)
        return cs

    def make_path(self):
        def make_superellipse(pos, v):
            p = self.loglerp_param('coil_p', v)
            q = self.loglerp_param('coil_q', v)
            return xforms.SuperScale(p, q, 2.0)

        def spiral(pos, v):
            R = self.lerp_param('coil_radius', v)
            b = self.loglerp_param('coil_logarithm', v)
            scale_factor = R * math.exp(b)
            return xforms.Scale(scale_factor, scale_factor, 1.0)
            
        pth = path.Helix(self.params['coil_z'], self.params['coil_angle'])
        pth = path.Transformed(pth, make_superellipse)
        pth = path.Transformed(pth, spiral)
        return pth
