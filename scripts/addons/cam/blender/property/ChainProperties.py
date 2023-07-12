from bpy.props import IntProperty, StringProperty, BoolProperty, CollectionProperty
from bpy.types import PropertyGroup

from .OperationReferenceProperties import OperationReferenceProperties

class ChainProperties(PropertyGroup):
    index: IntProperty(
        name="index",
        description="index in the hard-defined camChains",
        default=-1
    )

    name: StringProperty(
        name="Chain Name",
        default="Chain"
    )

    filename: StringProperty(
        name = "File name",
        default = "Chain",
        description = "The filename for the generated G-code of the chain."
    )

    valid: BoolProperty(
        name = "Valid",
        description="True if whole chain is ok for calculation",
        default=True
    )
    computing: BoolProperty(
        name = "Computing right now",
        description="",
        default=False
    )

    operations: CollectionProperty(
        type = OperationReferenceProperties
    )