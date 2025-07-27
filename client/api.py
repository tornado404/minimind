import sys
sys.path.append("third_party/Matcha-TTS")
import io
import time

import uvicorn
from fastapi import FastAPI, Response
from cosyvoice.cli.cosyvoice import CosyVoice
from cosyvoice.utils.file_utils import load_wav
import torchaudio
# third_party/Matcha-TTS
# cosyvoice = CosyVoice('pretrained_models/CosyVoice-300M-SFT')
cosyvoice = CosyVoice('pretrained_models/CosyVoice-300M')
# sft usage
# print(cosyvoice.list_avaliable_spks())
app = FastAPI()

@app.get("/api/voice/tts")
async def tts(query: str):
    start = time.process_time()
    output = cosyvoice.inference_sft(query, '中文女')
    output_list = list(output)
    end = time.process_time()
    print(f"Infer time: {end-start:.1f}s")
    buffer = io.BytesIO()
    # torchaudio.save(buffer, output['tts_speech'], 22050, format="wav")
    torchaudio.save(buffer, output_list[0]['tts_speech'], 22050, format="wav")
    buffer.seek(0)
    return Response(content=buffer.read(-1), media_type="audio/wav")

if __name__ == '__main__':
    uvicorn.run(app,
                host=None,
                port=8001,
                log_level="debug")