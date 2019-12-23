import bpy

# ExportHelper is a helper class, defines filename and
# invoke() function which calls the file selector.
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, BoolProperty, EnumProperty
from bpy.types import Operator


class ExportGMSSprite(Operator, ExportHelper):
    """This appears in the tooltip of the operator and in the generated docs"""
    bl_idname = "export_gms.sprite"
    bl_label = "Export GM:Studio Sprite"

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

    type = EnumProperty(
        name="Example Enum",
        description="Choose between two items",
        items=(('OPT_A', "First Option", "Description one"),
               ('OPT_B', "Second Option", "Description two")),
        default='OPT_A',
        )
    
    def write_some_data(self, context):
        print("running write_some_data...")
        f = open(self.filepath, 'w', encoding='utf-8')
        f.write("Hello World %s" % self.tile_horizontally)
        f.close()

        return {'FINISHED'}

    def execute(self, context):
        return self.write_some_data(context)


# Only needed if you want to add into a dynamic menu
def menu_func_export(self, context):
    self.layout.operator(ExportGMSSprite.bl_idname, text="Export GM:Studio Sprite")


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
