from bpy.types import Operator
import os
import aud

from ..property.NotificationProperties import * 

class PlayNotificationAudioSample(Operator):
    bl_idname = "scene.cam_notification_play_audio_sample"
    bl_label = "Play the notification audio sample"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.scene is not None

    def execute(self, context):
        notificationProperties : NotificationProperties = context.scene.notification
        audioSampleDirectory = bpy.context.scene.audioSampleDirectory 
        audioSamplePath = os.path.join(audioSampleDirectory, notificationProperties.playbackSampleName)

        device = aud.Device()
        sound = aud.Sound(audioSamplePath)
        device.play(sound)

        return {'FINISHED'}