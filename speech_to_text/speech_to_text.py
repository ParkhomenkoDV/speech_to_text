import json
from queue import Queue

import vosk
import sounddevice as sd


class STT:
    """Speech to text"""

    __slots__ = ('model', 'texts')

    def __init__(self, path: str) -> None:
        self.model = vosk.Model(path)
        self.texts = Queue()

    def __callback(self, data, frames, time, status) -> None:
        if status: print((data, frames, time, status))
        self.texts.put(bytes(data))

    def listen(self, callback,
               samplerate: int, device: int, blocksize: int = 8_000, dtype: str = 'int16', channels: int = 1):
        with sd.RawInputStream(samplerate=samplerate,
                               device=device,
                               blocksize=blocksize,
                               dtype=dtype,
                               channels=channels,
                               callback=self.__callback):
            rec = vosk.KaldiRecognizer(self.model, samplerate)
            while True:
                data = self.texts.get()
                if rec.AcceptWaveform(data):  # flag end of sentence
                    text = json.loads(rec.Result())["text"]
                    callback(text)
                '''
                else:
                    print(rec.PartialResult())
                    '''


if __name__ == '__main__':
    path = "models/RUSSIAN_small"
    stt = STT(path)


    def callback(text: str):
        print(text)


    samplerate = 16_000
    device = 1
    stt.listen(callback, samplerate=samplerate, device=device)
