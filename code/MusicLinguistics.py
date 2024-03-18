import whisper
import json
from langdetect import detect
import fasttext
import torch
import config as c

class Music_Linguistics():
    def __init__(self, transcribe_model = 'tiny', detect_model = 2) -> None:
        """
        Detects language of provided wav file (check documentation of whisper for mp3 files) by transcribing the file into text, then use langdetect/fasttext (defaulted to fasttext) to detect language.

        Base Accuracy: ~90% (13 / 133 Tracks incorrectly classified across English, Japanese, Chinese, French, German)

        Note:
        Unable to decipher simplified and traditional chinese due to inscription limitations, but is possible to retrieve these languages as output using fasttext and langdetect.

        Required packages:
            torch (for detecting available cuda drivers) [Current version 2.2.1+cu121]
            langdetect
            fasttext (see documentation for installation in windows) [cmake works]
            whisper
        """
        print(f"[Whisper] loading {transcribe_model}")
        if torch.cuda.is_available():
            print('Cuda driver detected, using pytorch cuda')
            self.model = whisper.load_model(transcribe_model, device = 'cuda')
        else:
            self.model = whisper.load_model(transcribe_model)
        print(f"[Whisper] {transcribe_model} loaded for audio transcription")

        #define mapping files
        map1_path = c.ROOT_ASSET_PATH + c.LANGUAGE_CODE_MAP1
        map2_path = c.ROOT_ASSET_PATH + c.LANGUAGE_CODE_MAP2

        if detect_model == 1:
            map_path = map1_path # langdetect map
        else:
            map_path = map2_path # fasttext map (default)

        with open(map_path, 'r', encoding='utf-8') as file:
            self.lang_map = json.load(file)
        pass

    def transcribe(self, path):
        print(f"[Whisper] Beginning transcription")
        self.path = path
        data = self.model.transcribe(path)
        self.text = data['text']
        print(f"[Whisper] Complete transcription")
        return
    
    def detect_langdetect(self,path):
        lan_code = detect(self.text[:20]) # more than 50 characters will cause the library to think chinese is korean
        self.lan = self.lang_map.get(lan_code)

        print(f"Language detected: {self.lan}")
        return self.lan

    def detect_fasttext(self, rerun = False):
        # 128 mb model not available for selection
        model = fasttext.load_model(c.ROOT_ASSET_PATH + c.FASTTEXT_MODEL)
        lan, _ = model.predict(self.text)
        lan_code = lan[0][-2:]
        self.lan = self.lang_map.get(lan_code)

        if not rerun and not self.lan:
            data = self.model.transcribe(self.path)
            lan, _ = model.predict(data['text'])
            #TODO redundant code, check what the output is after run
            lan_code = lan[0][-2:]  
            self.lan = self.lang_map.get(lan_code)
        
        print(f"Language detected: {self.lan}")
        return self.lan


"""
Sample usages:

text = '最強悍的第三者永遠都不是別人而是命運於是沒有失望藏眼裡到心災往事不會說黃彙跟他為難我們兩人'
text2 = "If you're visiting this page, you're likely here because you're searching for a random sentence. Sometimes a random word just isn't enough, and that is where the random"

model = whisper.load_model('tiny')
print("model loaded")
PATH = 'C:\\Users\\vocals.wav'
obj = Music_Linguistics()
obj.transcribe(PATH)
print(lan['text'])


lan_c = detect("我")
print(lan_c)
with open(map_path, 'r', encoding='utf-8') as file:
    lang_map = json.load(file)

lan = lang_map.get(lan_c)
print(lan)

PATH = "C:\\Users\\vocals.wav"
obj = Music_Linguistics()
obj.transcribe(PATH)
obj.detect_fasttext()
print(obj.text)
"""