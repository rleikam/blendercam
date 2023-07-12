from cam import bpy
from ..property.OpReference import OpReference

class CamChain(bpy.types.PropertyGroup):  # chain is just a set of operations which get connected on export into 1 file.
    index: bpy.props.IntProperty(name="index", description="index in the hard-defined camChains", default=-1)

    name: bpy.props.StringProperty(name="Chain Name", default="Chain")
    filename: bpy.props.StringProperty(name="File name", default="Chain", description="The filename for the generated G-code of the chain.")  # filename of
    valid: bpy.props.BoolProperty(name="Valid", description="True if whole chain is ok for calculation", default=True);
    computing: bpy.props.BoolProperty(name="Computing right now", description="", default=False)
    operations: bpy.props.CollectionProperty(type=OpReference)  # this is to hold just operation names.