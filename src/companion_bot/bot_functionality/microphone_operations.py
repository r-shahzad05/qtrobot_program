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
import os
from pathlib import Path
from typing import Callable


class QT_mic_operations:

    def __init__(self, node, on_transcription):
        self.node = node

        self.on_transcription = on_transcription

        self.recording = False

        self.audio_buffer = []

        self.output_path = str(
            Path(__file__).resolve().parent / "current_speech.wav"
        )

        default_model = (
            Path(__file__).resolve().parents[3]
            / "vosk-model-en-us-0.22"
        )
        self.model_path = os.getenv(
            "VOSK_MODEL_PATH",
            str(default_model),
        )

        self.model = Model(model_path=self.model_path)

        self.sample_rate = 0

        self.sample_width = 0

        self.channels = 0



        #Ros expects a messagetype, topicname,callback function, queue depth
        self.speech_detector = node.create_subscription(MicEventFrame,"/qtrobot/mic/int/event/stream",self.detect_audio_then_record,10)
        
        self.audio_input = node.create_subscription(AudioFrameRaw, "/qtrobot/mic/int/audio/ch0/stream", self.record_audio, 10)

    def detect_audio_then_record(self, msg: MicEventFrame):
        if msg.activity and not self.recording:
            self.audio_buffer = []
            self.recording = True
            self.start_time = time.monotonic()


        if not msg.activity and self.recording:
       
            self.recording = False
                # turn into a wav file

            if not self.audio_buffer:
                self.node.get_logger().warning("Speech ended without recieving audio")
                return

            if(self.sample_rate<= 0 or self.sample_width <= 0 or self.channels <= 0):
                self.node.get_logger().error("Audio metadata invalid")
                return

            self.finish_recording()

        

    def record_audio(self, frame):
        if not self.recording:
            return

        if not self.audio_buffer:
            self.sample_rate = frame.sample_rate
            self.sample_width = frame.sample_width
            self.channels = frame.channels


        self.audio_buffer.append(bytes(frame.data))



    def convert_to_speech(self):
        
        with wave.open(self.output_path, "rb") as wav:
            data = wav.readframes(wav.getnframes())
            sample_rate = wav.getframerate()

        if not data:
            return ""

        rec = KaldiRecognizer(self.model, sample_rate)

        rec.SetWords(True)

        rec.AcceptWaveform(data)

        result = json.loads(rec.FinalResult())

        return result.get("text", "").strip()

 

    def finish_recording(self):
        if not self.audio_buffer:
            return

        audio_data = b''.join(self.audio_buffer)
        self.audio_buffer = []

        with wave.open(self.output_path, "wb") as wav:
            wav.setnchannels(self.channels)
            wav.setsampwidth(self.sample_width)
            wav.setframerate(self.sample_rate)
            wav.writeframes(audio_data)
        
        text = self.convert_to_speech()

        if text:
            self.on_transcription(text)
        
        


            
