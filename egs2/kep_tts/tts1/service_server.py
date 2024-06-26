from concurrent import futures
import grpc
import service_pb2
import service_pb2_grpc

import os

from espnet2.bin.tts_inference import Text2Speech

import time
import torch
import soundfile as sf

import numpy as np


import wave
import io

import pdb

# 변수 설정
# basedir = './exp_vae/tts_finetune2'
basedir = '/workspace/db/sh/model'
model_file_ = 'train.total_count.best.pth'
train_config = 'config.yaml'
model_file = os.path.join(basedir, model_file_)
train_config = os.path.join(basedir, train_config)

# TTS 모델 초기화 
text2speech = Text2Speech.from_pretrained(
    train_config = train_config,
    model_file = model_file, 
)

def normalize(value, original_min=0, original_max=100, new_min=0, new_max=2):
    return ((value - original_min) / (original_max - original_min)) * (new_max - new_min) + new_min


# gRPC 서비스 구현
class TextToWavServiceImpl(service_pb2_grpc.TextToWavServiceServicer):        
    def ConvertTextToWav(self, request, context):
        # 클라이언트로부터 받은 텍스트
        text = request.text
        sid = request.sid
        ctrl_pitch = request.ctrl_pitch
        ctrl_speed = request.ctrl_speed
        ctrl_loudness = request.ctrl_loudness
        
        # refer
        speech, _ = sf.read('/workspace/TTS/KEP_TTS/sample/' + str(sid) + '.wav')
        speech = np.array(speech, dtype=np.float32)
        speech_tensor = torch.from_numpy(speech)
        
        # ctrl_loudness = (ctrl_loudness - 50) / 10
        ctrl_loudness = normalize(ctrl_loudness)
        wave = text2speech(text, 
                           sids = np.array(sid), 
                           speech = speech_tensor,
                           ctrl_pitch=ctrl_pitch * 0.1,
                           ctrl_speed = ctrl_speed,
                           ctrl_loudness = ctrl_loudness)["wav"]
        
        wave = wave.numpy()
        wave_data = wave.tobytes()
        return service_pb2.WavResponse(wav_file=wave_data)

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service_pb2_grpc.add_TextToWavServiceServicer_to_server(TextToWavServiceImpl(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("Server started at [::]:50051")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()