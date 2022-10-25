import math
import numpy as np

import bpy


def deg2rad(angle):
    return angle * math.pi / 180


def add_mesh(name, verts, faces=None, edges=None, col_name="Collection"):
    if edges is None:
        edges = []
    if faces is None:
        faces = []
    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(mesh.name, mesh)
    col = bpy.data.collections[col_name]
    col.objects.link(obj)
    bpy.context.view_layer.objects.active = obj
    so = bpy.context.active_object
    mod_subsurf = so.modifiers.new("subsurf", "SUBSURF")
    mod_subsurf.levels = 3
    mat = bpy.data.materials.get('tree_tex')
    so.active_material = mat
    bpy.ops.object.shade_smooth()
    mesh.from_pydata(verts, edges, faces)


def create_log(data, num_of_sensors, vel, period):
    layer_num = 0
    verts = []
    for layer_num, item in enumerate(data):
        for i, dist in enumerate(item):
            x = vel * period * layer_num
            y = dist * math.sin(deg2rad(15 + 30 * i))
            z = dist * math.cos(deg2rad(15 + 30 * i))
            verts.append([x, y, z])

    faces = list(range(0, num_of_sensors))
    for i in range(len(verts) - 1):
        current_point_id = i
        next_point_id = current_point_id + 1
        if next_point_id % num_of_sensors == 0:
            next_point_id -= num_of_sensors

        next_layer_point_id = current_point_id + num_of_sensors
        next_layer_next_point_id = next_layer_point_id + 1
        if next_layer_next_point_id % num_of_sensors == 0:
            next_layer_next_point_id -= num_of_sensors

        if next_layer_point_id < len(verts):
            faces.append([
                current_point_id,
                next_point_id,
                next_layer_next_point_id,
                next_layer_point_id
            ])

    faces.append(list(range(len(verts) - num_of_sensors, len(verts))))

    add_mesh("points", verts, faces)


data = np.loadtxt("/home/s/Desktop/skoltech/design_factory/blender_vis/data/groundtruth.txt")
num_of_sensors = 24
vel = 1
period = 0.1
create_log(data, num_of_sensors, vel, period)
