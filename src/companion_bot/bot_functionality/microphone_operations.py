# links to get microphone things 
# https://docs.luxai.com/docs/v3/api_ros2#microphone
# https://docs.luxai.com/docs/v3/tutorials/ros2/microphone

import rclpy
from rclpy.node import Node
from qtrobot_interfaces.msg import MicEventFrame, AudioFrameRaw
from vosk import Model, KaldiRecognizer
import time
import wave
import json


class QT_mic_operations:

    def __init__(self,node):
        self.node = node

        self.recording = False

        self.audio_buffer = []

        self.output_path = "current_speech.wav"

        self.model_name = "something" # TODO

        self.model = Model(model_name=self.model_name)

        self.sample_rate = 0

        self.sample_width = 0

        self.channels = 0


        #Ros expects a messagetype, topicname,callback function, queue depth
        self.speech_detector = node.create_subscription(MicEventFrame,"/qtrobot/mic/int/event/stream",self.detect_audio_then_record,10)
        
        self.audio_input = node.create_subscription(AudioFrameRaw, "/qtrobot/mic/int/audio/ch0/stream", self.record_audio, 10)

    def detect_audio_then_record(self, msg: MicEventFrame):
        if msg.activity:
            if self.recording == False:
                self.audio_buffer = []
                self.recording = True
        else:
            if self.recording == True:
                self.recording = False
                audio_data = b''.join(self.audio_buffer)
                self.audio_buffer = []

                # turn into a wav file
                with wave.open(self.output_path, "wb") as wav:
                    wav.setnchannels(self.channels)
                    wav.setsampwidth(self.sample_width)
                    wav.setframerate(self.sample_rate)
                    wav.writeframes(audio_data)
                

                text = self.convert_to_speech()

                return text

            # complete audio/ combine audio buffer
            # turn it into a wav file
            # send to vosk
            # return the text

    def record_audio(self, frame):
        if not self.recording:
            return

        if not self.audio_buffer:
            self.sample_rate = frame.sample_rate
            self.sample_width = frame.sample_width
            self.channels = frame.channels

        self.audio_buffer.append(bytes(frame.data))



    def convert_to_speech(self):
        
        wav = wave.open(self.output_path, "rb")

        rec = KaldiRecognizer(self.model, wav.getframerate())

        rec.SetWords(True)

        rec.SetPartialWords(True)

        text = ""
        
        data = wav.readframes(wav.getnframes())
        if len(data) == 0:
            wav.close()
            return ""

        if rec.AcceptWaveform(data):
            result = json.loads(rec.FinalResult())["text"]       

        text = result.get("text","").strip()

        wav.close()  

           
            
        return text
            


        
        


            
