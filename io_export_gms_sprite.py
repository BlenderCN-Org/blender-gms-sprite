import bpy

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportGMSSprite(Operator, ExportHelper):
    """Export a top-down render of the current model as a sprite resource for GameMaker:Studio"""
    bl_idname = "export_gms.sprite"
    bl_label = "GM:Studio Sprite"
    bl_options = {'PRESET'}

    # ExportHelper mixin class uses this
    filename_ext = ".yy"

    filter_glob = StringProperty(
            default="*.yy",
            options={'HIDDEN'},
            maxlen=255,  # Max internal buffer length, longer would be clamped.
            )

    # List of operator properties, the attributes will be assigned
    # to the class instance from the operator settings before calling.
    tile_horizontally = BoolProperty(
        name="Tile Horizontally",
        description="Whether to tile the texture horizontally",
        default=False,
        )
    
    tile_vertically = BoolProperty(
        name="Tile Vertically",
        description="Whether to tile the texture vertically",
        default=False,
        )
    
    premultiply_alpha = BoolProperty(
        name="Premultiply Alpha",
        description="Premultiply Alpha",
        default=False,
        )
    
    edge_filtering = BoolProperty(
        name="Edge Filtering",
        description="Edge Filtering",
        default=False,
        )
    
    def new_uuid(self):
        from uuid import uuid4
        return str(uuid4())
    
    def __init__(self):
        self.json = {
            "id": "d671dc7b-50b7-4bfe-b2fe-370ca5b18fc0",
            "modelName": "GMSprite",
            "mvc": "1.12",
            "name": "sprite2",
            "For3D": False,
            "HTile": False,
            "VTile": False,
            "bbox_bottom": 54,
            "bbox_left": 13,
            "bbox_right": 56,
            "bbox_top": 5,
            "bboxmode": 0,
            "colkind": 1,
            "coltolerance": 0,
            "edgeFiltering": False,
            "frames": [
                {
                    "id": "ebe129d7-b8a0-47ef-9b3a-e12b480173b6",
                    "modelName": "GMSpriteFrame",
                    "mvc": "1.0",
                    "SpriteId": "d671dc7b-50b7-4bfe-b2fe-370ca5b18fc0",
                    "compositeImage": {
                        "id": "7fcfd130-33a6-4f98-86e1-8c8c418ae13f",
                        "modelName": "GMSpriteImage",
                        "mvc": "1.0",
                        "FrameId": "ebe129d7-b8a0-47ef-9b3a-e12b480173b6",
                        "LayerId": "00000000-0000-0000-0000-000000000000"
                    },
                    "images": [
                        {
                            "id": "c91623b6-67ce-4a92-b1c9-12aca8613f14",
                            "modelName": "GMSpriteImage",
                            "mvc": "1.0",
                            "FrameId": "ebe129d7-b8a0-47ef-9b3a-e12b480173b6",
                            "LayerId": "ffc7bbc9-fdd0-495c-a06b-4895ce34a231"
                        }
                    ]
                }
            ],
            "gridX": 0,
            "gridY": 0,
            "height": 64,
            "layers": [
                {
                    "id": "ffc7bbc9-fdd0-495c-a06b-4895ce34a231",
                    "modelName": "GMImageLayer",
                    "mvc": "1.0",
                    "SpriteId": "d671dc7b-50b7-4bfe-b2fe-370ca5b18fc0",
                    "blendMode": 0,
                    "isLocked": False,
                    "name": "default",
                    "opacity": 100,
                    "visible": True
                }
            ],
            "origin": 9,
            "originLocked": False,
            "playbackSpeed": 15,
            "playbackSpeedType": 0,
            "premultiplyAlpha": False,
            "sepmasks": False,
            "swatchColours": None,
            "swfPrecision": 2.525,
            "textureGroupId": "1225f6b0-ac20-43bd-a82e-be73fa0b6f4f",
            "type": 0,
            "width": 64,
            "xorig": 53,
            "yorig": 48
        }
    
    def execute(self, context):
        fname = self.filepath
        import json

        # This'll be our object and render camera
        obj = context.object
        obj_cam = context.scene.camera
        cam = obj_cam.data

        # Origin calculations based on cursor location and mesh bounding box
        pos = obj.location
        dim = obj.dimensions
        top_right = (pos + dim/2)[0:2]
        bottom_left = (pos - dim/2)[0:2]

        cur_loc = context.scene.cursor_location[0:2]

        max_x, max_y = max(top_right, bottom_left)
        min_x, min_y = min(top_right, bottom_left)

        print("----------------")
        print(cur_loc)

        mac_x, mac_y = max(max_x, cur_loc[0]), max(max_y, cur_loc[1])
        mic_x, mic_y = min(min_x, cur_loc[0]), min(min_y, cur_loc[1])

        print(mic_x, mic_y)
        print(mac_x, mac_y)

        cam_x = mic_x + (mac_x-mic_x)/2
        cam_y = mic_y + (mac_y-mic_y)/2

        print("Cam:")
        print(cam_x, cam_y)

        origin_x = cur_loc[0] - mic_x
        origin_y = cur_loc[1] - mic_y

        print("Origin:")
        print(origin_x, origin_y)

        w = mac_x - mic_x
        h = mac_y - mic_y

        # Now position camera and resize canvas
        r = context.scene.render
        if w >= h:
            cam.ortho_scale = w
            #r.resolution_x = w
            r.resolution_y = h/w*r.resolution_x
        else:
            cam.ortho_scale = h
            #r.resolution_y = h
            r.resolution_x = w/h*r.resolution_y

        obj_cam.location = (cam_x, cam_y, 0)
        obj_cam.location.z = obj.dimensions.y * .5
        
        # Modify json data
        sprite_id = self.new_uuid()
        frame_id = self.new_uuid()
        layer_id = self.new_uuid()
        compo_id = self.new_uuid()
        img_id = self.new_uuid()
        
        # Write json data to file
        from os import path, mkdir, chdir
        base_path = path.split(fname)[0]
        chdir(base_path)
        
        base = path.basename(fname)
        asset_name, ext = path.splitext(base)
        print(asset_name)
        print(base_path)
        
        self.json["id"] = sprite_id
        self.json["name"] = asset_name
        self.json["width"] = r.resolution_x
        self.json["height"] = r.resolution_y
        
        self.json["edgeFiltering"] = self.edge_filtering
        self.json["HTile"] = self.tile_horizontally
        self.json["VTile"] = self.tile_vertically
        self.json["premultiplyAlpha"] = self.premultiply_alpha
        
        from math import floor
        self.json["xorig"] = floor(origin_x)
        self.json["yorig"] = floor(origin_y)
        
        frame = self.json["frames"][0]
        frame["id"] = frame_id
        frame["SpriteId"] = sprite_id
        frame["compositeImage"]["FrameId"] = frame_id
        frame["compositeImage"]["id"] = compo_id
        
        layer = self.json["layers"][0]
        layer["Sprite_id"] = sprite_id
        layer["id"] = layer_id
        
        img_data = frame["images"][0]
        img_data["FrameId"] = frame_id
        img_data["LayerId"] = layer_id
        img_data["id"] = img_id
        
        mkdir(asset_name)
        chdir(asset_name)
        
        f = open(asset_name + ".yy", "w")
        json.dump(self.json, f)
        f.close()
        
        bpy.ops.render.render()
        bpy.data.images['Render Result'].save_render(frame_id + ".png")
        
        mkdir("layers")
        chdir("layers")
        
        mkdir(frame_id)
        chdir(frame_id)
        
        bpy.data.images['Render Result'].save_render(layer_id + ".png")
        
        chdir("..")
        chdir("..")
        
        return {'FINISHED'}


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportGMSSprite.bl_idname, text="GM:Studio Sprite (*.yy)")


def register():
    bpy.utils.register_class(ExportGMSSprite)
    bpy.types.INFO_MT_file_export.append(menu_func_export)


def unregister():
    bpy.utils.unregister_class(ExportGMSSprite)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)


if __name__ == "__main__":
    register()