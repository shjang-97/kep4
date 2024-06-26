from espnet2.bin.tts_inference import Text2Speech
from espnet2.utils.types import str_or_none

import time
import torch


import os
import glob
import numpy as np
import kaldiio
import soundfile as sf

from espnet_model_zoo.downloader import ModelDownloader

from tqdm import tqdm
import soundfile as sf

import time

spk_dict = {
    '성인_여자_0': 56, '성인_여자_1': 4, '성인_여자_2': 5, '성인_여자_3': 53, 
    '성인_여자_4': 10, '성인_여자_5': 14, '성인_여자_6': 15, '성인_여자_7': 16, '성인_여자_8': 22, '성인_여자_9': 23, 
    '성인_여자_10': 24, '성인_여자_11': 25, '성인_여자_12': 26, '성인_여자_13': 27, '성인_여자_14': 28, '성인_여자_15': 29, 
    '성인_여자_16': 36, '성인_여자_17': 37, '성인_여자_18': 38, '성인_여자_19': 39, '성인_여자_20': 41, '성인_여자_21': 43, 
    '성인_여자_22': 44, '성인_여자_23': 9, '성인_여자_24': 3, '성인_여자_25': 55, 
    
    '성인_남자_0': 1, '성인_남자_1': 2, '성인_남자_2': 6, '성인_남자_3': 7, '성인_남자_4': 8, '성인_남자_5': 11, 
    '성인_남자_6': 12, '성인_남자_7': 13, '성인_남자_8': 17, '성인_남자_9': 18, '성인_남자_10': 19, '성인_남자_11': 20, 
    '성인_남자_12': 21, '성인_남자_13': 30, '성인_남자_14': 31, '성인_남자_15': 32, '성인_남자_16': 33, '성인_남자_17': 34, 
    '성인_남자_18': 35, '성인_남자_19': 40,  '성인_남자_20': 52, '성인_남자_21': 54,
    
    '어린이_0': 51, '어린이_1': 45, '어린이_2': 46, '어린이_3': 47, '어린이_4': 48, '어린이_5': 49, 
    '어린이_6': 50, 
}

def list_wav_files(directory):
    """
    주어진 디렉토리 내의 모든 .wav 파일을 리스트로 반환합니다.
    
    Args:
        directory (str): .wav 파일을 찾을 디렉토리 경로.
    
    Returns:
        List[str]: .wav 파일 경로들의 리스트.
    """
    wav_files = []
    
    # 디렉토리 내의 모든 파일 및 디렉토리 목록을 가져옵니다.
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.wav'):
                # .wav 파일 경로를 리스트에 추가합니다.
                wav_files.append(os.path.join(root, file))
    
    return wav_files


stage = 70
basedir = '/workspace/TTS/KEP_TTS/egs2/kep_tts/tts1/exp_vae/tts_finetune2'
model_file = '/workspace/TTS/KEP_TTS/egs2/kep_tts/tts1/exp_vae/tts_finetune2/train.total_count.best.pth'
train_config = os.path.join(basedir, 'config.yaml')
text2speech = Text2Speech.from_pretrained(
    train_config = train_config,
    model_file = model_file
)

textlist = ['안녕하세요, 소야와 헤니의 인턴 마지막 발표에 참여해주셔서 감사합니다.',
            '저는 다화자를 한 모델로 통합하는 음성합성 모델을 개발하였고, 이 모델은 어려운 발음도 성공적으로 할 수 있습니다!',
            '예를 들면,  편판선 군의 친구 판편숙 양은 간장공장 공장장의 친구 중앙청 창살 쌍 창살을 관리했다.',
            '이제 발표 시작하겠습니다.']

text_p = '피치 컨트롤 샘플입니다. '
text_l = '볼륨 컨트롤 샘플입니다. '
text_s = '속도 컨트롤 샘플입니다. '

a = 0

dirs = f'./output/test_prosody'
os.makedirs(dirs, exist_ok=True)

pitch = 0
ctrl_speed = 1
ctrl_loudness = 0
        
# for text in textlist:
# print(text)
pitchlist = [-10, -7, -5, 0, 5, 7, 10]
speedlist = [1.5, 1.25, 1, 0.75, 0.5, 0.25]
# loudlist = [-0.5, -0.25, 0, 0.25, 0.5, 1, 1.5, 2]
loudlist2 = [0.5, 0.75, 1, 1,25, 1.5]


pitch = 0
ctrl_speed = 1
ctrl_loudness = 1

gl = [3, 4, 55, 53, 10, 14, 15, 16, 22, 23, 24, 25, 26, 27, 28, 29, 36, 37, 38, 39, 41, 43, 44, 9, 5]
bl = [1, 2, 6, 7, 8, 11, 12, 13, 17, 18, 19, 20, 21, 30, 31, 32, 33, 34, 35, 40, 51, 52, 54]
ch = [51, 45, 46, 47, 48, 49, 50]

ch = [55, 56] #, 51]

dirs = f'./output/test_4_ch'
os.makedirs(dirs, exist_ok=True)

pitch = 0
ctrl_speed = 1
ctrl_loudness = 1

total = 0  # rtf
total_length = 0

# for i in ch:
for i in range(1, 5):
    # x =  "들의 콩깍지는 깐 콩깍지인가, 안 깐 콩깍지인가? "
    x = "프로소디를 조절하면, 음성의 스타일을  변화시킬 수 있어요. "

    sids = np.array(i)
    speech, _ = sf.read('/workspace/TTS/sample/' + str(sids) +'.wav')
    speech = np.array(speech, dtype=np.float32)
    speech_tensor = torch.from_numpy(speech)

    with torch.no_grad():
        start = time.time()
        wav = text2speech(x, sids= sids,
                        speech = speech_tensor,
                        ctrl_pitch=pitch * 0.1,
                        ctrl_speed=ctrl_speed,
                        ctrl_loudness=ctrl_loudness)["wav"]
        
                        
        # scipy.io.wavfile.write("out.wav",text2speech.fs , wav.view(-1).cpu().numpy())
        sf.write(os.path.join(dirs,str(sids)+"_0.wav"), wav.numpy(), text2speech.fs, "PCM_16")
        audio_length_seconds = len(wav) / text2speech.fs
        inference_time = time.time() - start
        total = total + inference_time
        total_length = total_length + audio_length_seconds

print("rtf: ", total / total_length) 
exit()
pitch = 0
ctrl_speed = 1
ctrl_loudness = 0
for ctrl_loudness in loudlist:
    x = f"{text_l}"
    print(x)
    for i in tqdm(range(1, 57)):
        sids = np.array(i)
        speech, _ = sf.read('/workspace/TTS/sample/' + str(sids) +'.wav')
        speech = np.array(speech, dtype=np.float32)
        speech_tensor = torch.from_numpy(speech)

        with torch.no_grad():
            start = time.time()
            wav = text2speech(x, sids= sids,
                            speech = speech_tensor,
                            ctrl_pitch=pitch * 0.1,
                            ctrl_speed=ctrl_speed,
                            ctrl_loudness=ctrl_loudness)["wav"]
                            
            # scipy.io.wavfile.write("out.wav",text2speech.fs , wav.view(-1).cpu().numpy())
            sf.write(os.path.join(dirs,"l_"+str(sids)+"_"+str(ctrl_loudness)+".wav"), wav.numpy(), text2speech.fs, "PCM_16")

pitch = 0
ctrl_speed = 1
ctrl_loudness = 0
#loud
for ctrl_speed in speedlist:
    x = f"{text_s}"
    print(x)
    for i in tqdm(range(1, 57)):
        sids = np.array(i)
        speech, _ = sf.read('/workspace/TTS/sample/' + str(sids) +'.wav')
        speech = np.array(speech, dtype=np.float32)
        speech_tensor = torch.from_numpy(speech)


        # ctrl_loudness = -0.5
        
        with torch.no_grad():
            start = time.time()
            wav = text2speech(x, sids= sids,
                            speech = speech_tensor,
                            ctrl_pitch=pitch * 0.1,
                            ctrl_speed=ctrl_speed,
                            ctrl_loudness=ctrl_loudness)["wav"]
                            
            # scipy.io.wavfile.write("out.wav",text2speech.fs , wav.view(-1).cpu().numpy())
            sf.write(os.path.join(dirs,"s_"+str(sids)+"_"+str(ctrl_speed)+".wav"), wav.numpy(), text2speech.fs, "PCM_16")

pitch = 0
ctrl_speed = 1
ctrl_loudness = 0
# pitch
for pitch in pitchlist:
    x = f"{text_p}"
    print(x)
    for i in tqdm(range(1, 57)):
        sids = np.array(i)
        speech, _ = sf.read('/workspace/TTS/sample/' + str(sids) +'.wav')
        speech = np.array(speech, dtype=np.float32)
        speech_tensor = torch.from_numpy(speech)
        
        with torch.no_grad():
            start = time.time()
            wav = text2speech(x, sids= sids,
                            speech = speech_tensor,
                            ctrl_pitch=pitch * 0.1,
                            ctrl_speed=ctrl_speed,
                            ctrl_loudness=ctrl_loudness)["wav"]
                            
            sf.write(os.path.join(dirs,"p_"+str(sids)+"_"+str(pitch)+".wav"), wav.numpy(), text2speech.fs, "PCM_16")
    # a = a+1

