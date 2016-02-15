bl_info = {
    "name": "THPS Scene/Mdl import Format (.mdl)",
    "author": "Andrew \"CHCNiZ\" Learn",
    "version": (0, 0, 1),
    "blender": (2, 63, 0),
    "location": "File > Import > THPS Model Format (.mdl/.scn)",
    "description": "Import THPS Models (XBox/PC Format only) (.mdl/.scn)",
    "warning": "Alpha software",
    "category": "Import",
}

import os
import codecs


import pprint
from pprint import pprint

from bpy_extras.io_utils import unpack_list, unpack_face_list

import math
from math import sin, cos, radians

import bpy
from bpy.props import BoolProperty
from bpy.props import EnumProperty
from bpy.props import StringProperty

import struct
from struct import *

from mathutils import Vector, Matrix

import json


class THPSMDLImport(bpy.types.Operator):
	"""Export selection to THPS MDL"""

	bl_idname = "export_scene.mdl"
	bl_label = "Import THPS MDL"

	filepath = StringProperty(subtype='FILE_PATH')
	
	#public interface
	
	def execute(self, context):
		#self.filepath = bpy.path.ensure_ext(self.filepath, ".mdl")
		self.ReadScene()
		return {'FINISHED'}

	def invoke(self, context, event):
		#if not self.filepath:
		#	self.filepath = bpy.path.ensure_ext(bpy.data.filepath, ".mdl")
		context.window_manager.fileselect_add(self)
		return {'RUNNING_MODAL'}
		
	#private
	def ReadMaterial(self, material_data):
		material = bpy.data.materials.new(material_data["name"])
		print("The Path: {}".format("/home/andy/blender/jizzy/" + material_data["name"]))
		textures = []
		for t in material_data["textures"]:
			tex = bpy.data.textures.new(t["name"], type ="IMAGE")
			path = "/home/andy/blender/jizzy/" + t["name"] + ".png"
			img = bpy.data.images.load(path)
			tex.image = img

			mtex = material.texture_slots.add()
			mtex.texture_coords = 'UV';
			mtex.use_map_alpha = True
			mtex.texture = tex
			material.use_transparency = True
			material.transparency_method = 'Z_TRANSPARENCY'
		material["checksum"] = material_data["checksum"]
		return material
	def ReadScene(self):
		scnfile = open(self.filepath, "rb")

		
		with open(self.filepath) as data_file:    
		    data = json.load(data_file)
		print("JSON Loaded")
		print("---------------")
		print("File: {}".format(self.filepath))
		print("Num Meshes: {}".format(len(data["meshes"])))
		materials = []
		for m in data["materials"]:
			materials.append(self.ReadMaterial(m))
		nobj = self.ReadMesh(data["meshes"][0])
		mat = self.FindMaterialByChecksum(materials, data["meshes"][0]["material_checksum"])
		if mat:
			nobj.data.materials.append(mat)
		#self.ReadMaterial(nobj, data["materials"], data["meshes"][0])
#		for x in data["meshes"]:
#			self.ReadMesh(x)
		return 0
	def ConvertToVector(self, data):
		ret = []
		for v in data:
			ret.append(Vector([v[0],v[1],v[2]]))
		return ret
	def FindMaterialByChecksum(self, materials, checksum):
		print("I must find: {}".format(checksum))
		for m in materials:
			if m["checksum"] == checksum:
				return m
		return 0
	def ReadMesh(self, mesh):
		print("Name: {}".format(mesh["name"]))
		print("Num Verts: {}".format(len(mesh["vertices"])))
		print("Num Indices: {}".format(len(mesh["indices"][0])))

		scn = bpy.context.scene

		for o in scn.objects:
			o.select = False
		


		blenmesh = bpy.data.meshes.new(mesh["name"])
		blenmesh.vertices.add(len(mesh["vertices"]))
		blenmesh.vertices.foreach_set("co", unpack_list(mesh["vertices"]))
		blenmesh.tessfaces.add(len(mesh["indices"][0]))
		# Add faces
		blenmesh.tessfaces.foreach_set("vertices_raw", unpack_face_list(mesh["indices"][0]))

		uvlay = blenmesh.tessface_uv_textures.new()

#		for i, f in enumerate(mesh["indices"][0]):
#			blender_tface = blenmesh.tessface_uv_textures[0].data[i]
#			print("Face: {} {}".format(i,f))
#			print("Face: {} {} {}".format(mesh["uvs"][f[0]][0], mesh["uvs"][f[1]][1], mesh["uvs"][f[2]][2]))
#			blender_tface.uv1 = (mesh["uvs"][f[0]][0], mesh["uvs"][f[0]][1])
#			blender_tface.uv2 = (mesh["uvs"][f[1]][0], mesh["uvs"][f[1]][1])
#			blender_tface.uv3 = (mesh["uvs"][f[2]][0], mesh["uvs"][f[2]][1])



		for i, f in enumerate(uvlay.data):
			index = mesh["indices"][0][i]
			for j, uv in enumerate(f.uv):
				print("The Index: {}".format(index))
				print("Max: {}".format(len(mesh["uvs"])))
				uv[0] = mesh["uvs"][index[j]][0]
				uv[1] = mesh["uvs"][index[j]][1]
#		blenmesh.from_pydata(mesh["vertices"], [], mesh["indices"][0])
#		uvtex = blenmesh.uv_textures.new()
#		uvtex.name = 'UVLayer'
#		for face in mesh["indices"][0]:
#			print("UVS: {}".format(face))
#			for i, f in enumerate(uvtex.data):
#				print("F IS: {}".format(f))
#				for j, uv in enumerate(f.uv):
#					uv[0], uv[1], uv[2] = (0.0,1.0, 1.2)
#		uv_layer = blenmesh.loops.layers.uv.new()
		blenmesh.update()
		blenmesh.validate()
		nobj = bpy.data.objects.new(mesh["name"], blenmesh)
		scn.objects.link(nobj)
		return nobj


def menu_func(self, context):
    self.layout.operator(THPSMDLImport.bl_idname, text="THPS Model (.mdl)")


def register():
    bpy.utils.register_module(__name__)

    bpy.types.INFO_MT_file_import.append(menu_func)


def unregister():
    bpy.utils.unregister_module(__name__)

    bpy.types.INFO_MT_file_import.remove(menu_func)

if __name__ == "__main__":
    register()