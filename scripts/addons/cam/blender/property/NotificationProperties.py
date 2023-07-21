from bpy.props import EnumProperty, BoolProperty
from bpy.types import PropertyGroup

import os
import bpy
from pathlib import PurePath

def getAudioSampleNames(self, context):
    audioSampleNames = []
    audioSampleDirectory = bpy.context.scene.audioSampleDirectory
    for fileName in os.listdir(audioSampleDirectory):
        path = PurePath(fileName)
        nameWithoutSuffix = path.stem
        suffix = path.suffix

        audioSampleNames.append(
            (f"{nameWithoutSuffix}{suffix}", nameWithoutSuffix, nameWithoutSuffix)
        )

    return audioSampleNames

class NotificationProperties(PropertyGroup):
    enableAudioPlayback: BoolProperty(
        name = "Activate audio playback",
        description = "Activates audio playback, when calculations of operations and chains are done",
        default = False
    )

    playbackSampleName: EnumProperty(
        items = getAudioSampleNames,
        name = "Audio sample",
        description = "The audio sample that should be played back"
    )