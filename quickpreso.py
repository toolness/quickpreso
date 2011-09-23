import os
import wave
import subprocess
import json

ROOT = os.path.abspath(os.path.dirname(__file__))
path = lambda *x: os.path.join(ROOT, *x)

def say(words, filename, voice='Alex'):
    null = open('/dev/null', 'w')
    finalwav = path('final.wav')
    out = wave.open(finalwav, 'w')
    nchannels = 1
    sampwidth = 2
    framerate = 22050
    comptype = 'NONE'
    compname = 'not compressed'
    out.setparams((nchannels, sampwidth, framerate, 0, comptype, compname))
    durations = []
    tmpwave = path('tmp.wave')
    tmpwav = path('tmp.wav')
    for word in words:
        if isinstance(word, basestring):
            subprocess.check_call(['say', '-v', voice, '-o', tmpwave, word])
            subprocess.check_call(['ffmpeg', '-y', '-i', tmpwave, tmpwav],
                                  stdout=null, stderr=subprocess.STDOUT)
            inp = wave.open(tmpwav, 'r')
            durations.append(float(inp.getnframes()) / framerate)
            out.writeframes(inp.readframes(inp.getnframes()))
            inp.close()
            for tmpfilename in [tmpwave, tmpwav]:
                os.unlink(tmpfilename)
        elif isinstance(word, (int, float)):
            out.writeframes('\0' * (sampwidth * int(word * framerate)))
            durations.append(float(word))
        else:
            raise ValueError('unexpected: %s' % word)
    out.close()
    subprocess.check_call(['ffmpeg', '-y', '-i', finalwav,
                           '-acodec', 'libvorbis', '-aq', '1', filename],
                          stdout=null, stderr=subprocess.STDOUT)
    os.unlink(finalwav)
    null.close()
    return durations

def main():
    print "generating script.ogg and script.json from script.html."
    script = open(path('static-files', 'script.html'), 'r')
    speak = []
    for line in script:
        line = line.strip()
        if line and not line.startswith('<'):
            speak.append(line)
            speak.append(0.5)
    durations = say(speak, path('static-files', 'script.ogg'))
    json.dump(durations, open(path('static-files', 'script.json'), 'w'))
    print "done."
    
if __name__ == '__main__':
    main()
