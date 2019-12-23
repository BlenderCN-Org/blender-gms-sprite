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
    filename_ext = ".png"

    filter_glob = StringProperty(
            default="*.png",
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

    type = EnumProperty(
        name="Example Enum",
        description="Choose between two items",
        items=(('OPT_A', "First Option", "Description one"),
               ('OPT_B', "Second Option", "Description two")),
        default='OPT_A',
        )
    
    def execute(self, context):
        fname = self.filepath

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

        # Render the thing
        bpy.ops.render.render()

        bpy.data.images['Render Result'].save_render(fname)
        
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

    # test call
    bpy.ops.export_gms.sprite('INVOKE_DEFAULT')
