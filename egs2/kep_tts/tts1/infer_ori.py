import requests
import os 
import time
import soundfile as sf
from pydub import AudioSegment


# name_list = ['Chase_Call', 'Claire_Call', 'Cooper_Call', 'Carter_Call', 'Bentley_Call']
name_list  = ['Anna', 
              'Bentley', 
              'Cameron', 
              'Carter', 
              'Casey', 
              'Chase', 
              'Claire', 
              'Clara', 
              'Cooper', 
              'Cora', 
              'Daisy', 
              'Dakota', 
              'David', 
              'Dax', 
              'Dean', 
              'Della', 
              'Demi', 
              'Diana', 
              'Dorothy', 
              'Dream', 
              'Elias', 
              'Emily', 
              'Emma', 
              'Kai',  # plain
              'Kane', 
              'Kayla', 
              'Kevin', 
              'Kyle', 
              'Nathan', 
              'Nolan', 
              'Nora', 
              'Roman',   # plain
              'Summer']  # plain

name_list = ['Roman', 'Summer','Kai']
# 33개

# 설정 값
api_key = "20def6dd2aae292f50b58e27e07f8780"  # 실제 API 키로 교체
engine = "plain"  # deep / plain
encoding = "mp3"  # 실제 인코딩 방식으로 교체
sample_rate = "22050"  # 실제 샘플 레이트로 교체 -> 24000도 되는지 확인 
api_url = "https://d6a17d4a-2439-40f4-9fcf-5522422b4793.api.kr-central-1.kakaoi.io/ai/text-to-speech/de1e8abcbd644c11a6b5f424a0e11ccf"  # 실제 API 주소로 교체

# 헤더 설정
headers = {
    "x-api-key": api_key,
    "Content-Type": "application/xml",
    "X-TTS-Engine": engine,
    "X-TTS-Encoding": encoding,
    "X-TTS-Samplerate": sample_rate
}

# text = '카카오엔터프라이즈가 만든 제너럴 티티에스 에이피아이는 사용자가 입력한 텍스트를 처리하여 음성으로 변환합니다.'
# text =  "챠프포프킨과 치스챠코프는 라흐마니노프의 피아노 콘체르토의 선율이 흐르는 영화 파워트웨이트를 보면서 켄터키 후라이드 치킨, 포테이토 칩, 파파야 등을 포식하였다."
text=  "프로소디를 조절하면, 음성의 스타일을  변화시킬 수 있어요. "

total = 0
total_length = 0
for name in name_list:  
    # 데이터 설정
    data = f'<speak><voice name="{name}">{text}</voice></speak>'.encode('utf-8')  # UTF-8로 인코딩
    
    # 합성 시작 시간 기록
    start_time = time.time()

    # 요청 보내기
    fol = './output/test_4_ori_' + engine
    response = requests.post(api_url, headers=headers, data=data)
    filename = os.path.join(fol, name)
    os.makedirs(fol, exist_ok=True)

    inference_time = time.time() - start_time
    # 응답 확인
    if response.status_code == 200:
        # 응답 내용을 파일에 쓰기
        with open(filename+'.mp3', 'wb') as file:
            file.write(response.content)
        print("파일이 성공적으로 저장되었습니다.")
    else:
        print(f"요청에 실패했습니다. 상태 코드: {response.status_code}")
    
    # MP3 파일 로드 및 WAV 변환
    audio = AudioSegment.from_mp3(filename + '.mp3')
    wav_file = filename + '.wav'
    audio.export(wav_file, format='wav')

    # WAV 파일 길이 계산
    wav_data, samplerate = sf.read(wav_file)
    audio_length_seconds = len(wav_data) / samplerate

    total = total + inference_time
    total_length = total_length + audio_length_seconds
    # 실시간 처리율(RTF) 계산
        
rtf = total / total_length 
print(rtf)

# 0.02