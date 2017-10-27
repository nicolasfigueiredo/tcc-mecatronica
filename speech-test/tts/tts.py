from gtts import gTTS
import vlc
import time

while True:
	text = input('Digite o que vc quer que a moça da Google fale: ')

	tts = gTTS(text=text, lang='pt')

	tts.save("hello.mp3")
	p = vlc.MediaPlayer("hello.mp3")
	p.play()

	time.sleep(0.2)
	while p.is_playing() == 1:
		pass
# f = TemporaryFile()
# tts.write_to_fp(f)
# # <Do something with f>
# f.close()