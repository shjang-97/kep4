import grpc
import service_pb2
import service_pb2_grpc
import soundfile as sf
import wave
import numpy as np
import gradio as gr
import os
import base64

# 화자 식별자 사전
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
speed_dict = {
    '0.75x': 1.3, '1x': 1, '1.5x': 0.67, '2x': 0.5
}

# gRPC 서버와 통신하여 텍스트를 음성으로 변환하는 함수
def tts(text, sid, pitch = 0, speed='1x', loudness=0):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = service_pb2_grpc.TextToWavServiceStub(channel)
        # 서버에 보낼 텍스트 메시지를 생성하고 gRPC 요청을 수행합니다.
        response = stub.ConvertTextToWav(service_pb2.TextRequest(
            text=text,
            sid=spk_dict[sid],
            ctrl_pitch=pitch,
            ctrl_speed=speed_dict[speed],
            ctrl_loudness = loudness))
        
        # 응답 받은 WAV 파일 저장
        output_file = "output.wav"
        save_wav(response.wav_file, output_file)
        
        return output_file

# WAV 파일을 저장하는 함수
def save_wav(wav_bytes, filename="./output.wav", sample_rate=24000, num_channels=1, sampwidth=2):
    audio_data = np.frombuffer(wav_bytes, dtype=np.float32)
    # numpy 배열을 WAV 파일로 저장
    sf.write(filename, audio_data, sample_rate, "PCM_16")
    return filename

# 이미지 파일을 Base64로 인코딩
image_path = "demo.png"
if not os.path.exists(image_path):
    raise FileNotFoundError(f"Image file not found at {image_path}")

with open(image_path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode()

# Gradio 인터페이스 설정
iface = gr.Interface(
    fn=tts,
    inputs=[
        'text', 
        gr.Dropdown(list(spk_dict.keys()), label="Speaker", info="화자를 선택해보세요!"),
        gr.Slider(-10, 10, value=0, label="Pitch control", step=1, info="음의 높낮이를 조절해보세요!"),
        gr.Radio(list(speed_dict.keys()), label="Speed control", info="속도를 조절해보세요!"),
        gr.Slider(0, 100, value=50, label="Volume control", step=1, info="음량을 조절해보세요!"),
    ],
    outputs='audio',
    description=f"""
    <div style="text-align: center;">
        <div style="display: inline-block; text-align: center;">
            <img src="data:image/png;base64,{encoded_string}" alt="Logo" style="max-height: 200px;">
        </div>
        <p>텍스트를 입력하고 화자, 음의 높낮이, 속도, 음량을 선택하여 음성 파일을 생성해보세요!</p>
        <p>(한 문장 당 텍스트 150자 이하를 권장하며, 문장 끝에는 마침표를 꼭 찍어주세요.)</p>
    </div>
    """,
    examples=[["안녕하세요, 카카오엔터프라이즈 음성합성 모델 테스트입니다.", "성인_여자_0", 0, "1x", 50],
              ["저기 있는 저 분은 박 법학박사이고, 여기 있는 이 분은 백 법학박사이다.", "성인_여자_4", 0, "1x", 50],
              ["저기 저 돌하르방 코는 아들 낳을 돌하르방 코인가, 딸 낳을 돌하르방 코인가? ", "성인_여자_22", 0, "1x", 50],
              ["시답잖은 농담 속에 서울 찹쌀 촌 찹쌀같이 나눠져 있던 마음이 녹아버렸어. ", "성인_남자_0", 0, "1x", 50],
              ["난 청송콩찰떡이 좋다고 했지! ", "성인_남자_12", 0, "1x", 50],
              ["하지만 이내 우리는 강력접착제처럼 철수 책상 철 책상에 앉았다.", "성인_남자_18", 0, "1x", 50],
              ["담임 선생님의 담당과목은 화학과목이다.", "성인_남자_12", 0, "1x", 50],
              ["윗니를 쓱싹쓱싹, 아랫니를 쓱싹쓱싹~", "어린이_0", 0, "1x", 50],
              ["엄마 아빠 말 잘 듣는 착한 아이가 될게요!.", "어린이_6", 0, "1x", 50],
              ]
)
# iface.launch(share=True)
iface.launch(server_name="0.0.0.0", server_port=7860)
