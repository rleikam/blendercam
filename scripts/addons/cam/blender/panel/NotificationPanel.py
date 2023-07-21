import bpy
from bpy.types import Panel

from .ButtonsPanel import ButtonsPanel
from ..property.NotificationProperties import *
from ..operation.PlayNotificationAudioSample import *

class NotificationPanel(ButtonsPanel, Panel):
    """CAM machine panel"""
    bl_label = "Notifications"
    bl_idname = "CAM_PT_notification"

    COMPAT_ENGINES = {'BLENDERCAM_RENDER'}

    def draw(self, context):

        notificationProperties : NotificationProperties = context.scene.notification

        layout = self.layout
        layout.prop(notificationProperties, "enableAudioPlayback")

        if notificationProperties.enableAudioPlayback:
            layout.prop(notificationProperties, "playbackSampleName")
            layout.operator(PlayNotificationAudioSample.bl_idname)

        layout = self.layout




        
