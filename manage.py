"""
    usage: go.py <command>
    
    commands:
    
      runserver       - run web server on 127.0.0.1 port %(port)s
      build           - build all content
"""

from wsgiref.simple_server import make_server
from wsgiref.util import FileWrapper
import os
import sys
import mimetypes
import wave
import subprocess
import hashlib
import json

ROOT = os.path.abspath(os.path.dirname(__file__))
path = lambda *x: os.path.join(ROOT, *x)

port = 8020
htmlpath = path('static-files', 'script.html')
oggpath = path('static-files', 'script.ogg')
jsonpath = path('static-files', 'script.json')

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

def build():
    print "generating script.ogg and script.json from script.html."
    script = open(htmlpath, 'r')
    
    speak = []
    for line in script:
        line = line.strip()
        if line and not line.startswith('<'):
            speak.append(line)
            speak.append(0.5)
    speakhash = hashlib.sha1(json.dumps(speak)).hexdigest()
    if os.path.exists(jsonpath) and os.path.exists(oggpath):
        oldmetadata = json.load(open(jsonpath, 'r'))
        if oldmetadata['speakhash'] == speakhash:
            print "done (no changes needed)."
            return
    metadata = dict(speakhash=speakhash, durations=say(speak, oggpath))
    json.dump(metadata, open(jsonpath, 'w'))
    print "done."

def make_app():
    def app(environ, start_response):
        origpath = environ['PATH_INFO']

        if origpath.endswith('/'):
            origpath = '%sindex.html' % origpath
        fileparts = origpath[1:].split('/')
        fullpath = path('static-files', *fileparts)
        fullpath = os.path.normpath(fullpath)
        (mimetype, encoding) = mimetypes.guess_type(fullpath)
        if fullpath in [jsonpath, oggpath]:
            build()
        if (fullpath.startswith(ROOT) and
            not '.git' in fullpath and
            os.path.isfile(fullpath) and
            mimetype):
            filesize = os.stat(fullpath).st_size
            start_response('200 OK', [('Content-Type', mimetype),
                                      ('Content-Length', str(filesize)),
                                      ('Accept-Ranges', 'bytes')])
            return FileWrapper(open(fullpath, 'rb'))

        start_response('404 Not Found', [('Content-Type', 'text/plain')])
        return ['Not Found: ', origpath]

    return app

def serve(ip=''):
    ipstr = ip
    if not ipstr:
        ipstr = 'all IP interfaces'
    server = make_server(ip, port, make_app())
    print "serving on %s port %d" % (ipstr, port)
    server.serve_forever()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print __doc__ % globals()
        sys.exit(1)

    cmd = sys.argv[1]
    
    if cmd == 'runserver':
        serve('127.0.0.1')
    elif cmd == 'build':
        build()
    else:
        print "unknown command: %s" % cmd
        sys.exit(1)
