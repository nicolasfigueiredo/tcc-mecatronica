from __future__ import division

import sys

from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
import pyaudio
from six.moves import queue

from watson_developer_cloud import TextToSpeechV1
from slot_filling.Constants import *

import vlc
import time
from gtts import gTTS

# Audio recording parameters
RATE = 16000
CHUNK = int(RATE / 10)  # 100ms

input_mode = ''

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True

    def __enter__(self):
        self._audio_interface = pyaudio.PyAudio()
        self._audio_stream = self._audio_interface.open(
            format=pyaudio.paInt16,
            # The API currently only supports 1-channel (mono) audio
            # https://goo.gl/z757pE
            channels=1, rate=self._rate,
            input=True, frames_per_buffer=self._chunk,
            # Run the audio stream asynchronously to fill the buffer object.
            # This is necessary so that the input device's buffer doesn't
            # overflow while the calling thread makes network requests, etc.
            stream_callback=self._fill_buffer,
        )

        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        while not self.closed:
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)
# [END audio_stream]

def listen_print_loop(responses):
    """Iterates through server responses and prints them.
    The responses passed is a generator that will block until a response
    is provided by the server.
    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.
    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """
    num_chars_printed = 0
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        if not result.is_final:
            pass
            # sys.stdout.write(transcript + overwrite_chars + '\r')
            # sys.stdout.flush()

            # num_chars_printed = len(transcript)

        else:
            return(transcript + overwrite_chars)
            # Exit recognition if any of the transcribed phrases could be
            # one of our keywords.
            # if re.search(r'\b(exit|quit)\b', transcript, re.I):
            #     print('Exiting..')
            #     break
            # num_chars_printed = 0


# See http://g.co/cloud/speech/docs/languages
# for a list of supported languages.
language_code = 'pt-BR'  # a BCP-47 language tag

client = speech.SpeechClient()
config = types.RecognitionConfig(
    encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
    sample_rate_hertz=RATE,
    language_code=language_code)
streaming_config = types.StreamingRecognitionConfig(
    config=config,
    single_utterance=True,
    interim_results=False)

text_to_speech = TextToSpeechV1(
    username=WATSON_USERNAME,
    password=WATSON_PWORD,
    x_watson_learning_opt_out=True)  # Optional flag


def setup(mode):
    global input_mode
    input_mode = mode 

def get_input(prompt):
    global input_mode

    if input_mode == 't':
        return(input(prompt))
    else:
        if prompt:
            output(prompt)
        with MicrophoneStream(RATE, CHUNK) as stream:
            audio_generator = stream.generator()
            requests = (types.StreamingRecognizeRequest(audio_content=content)
                for content in audio_generator)
            responses = client.streaming_recognize(streaming_config, requests)
            utterance = listen_print_loop(responses)
            print(utterance)
            return(utterance)
      
def output(msg):
    global input_mode

    if input_mode == 'v':
        # tts = gTTS(text=msg, lang='pt')
        # tts.save("tts_out.mp3")

        with open('output.wav', 'wb') as audio_file:
            audio_file.write(
                text_to_speech.synthesize(msg, accept='audio/wav',
                                      voice="pt-BR_IsabelaVoice"))


        p = vlc.MediaPlayer("output.wav")
        p.play()

        print(msg)
        
        time.sleep(0.2)
        while p.is_playing() == 1:
            pass

    else:
        print(msg)