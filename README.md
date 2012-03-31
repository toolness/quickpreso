Quickpreso is an attempt to make prototyping presentations be more like prototyping HTML pages.

Whether this is a good idea remains to be seen.

## Requirements ##

To generate presentations, you need:

* OS X 10.6 or higher
* [ffmpeg][]

The generated presentations use [Popcorn.js][] for syncing audio to video content. Currently, the audio is only produced in Ogg Vorbis format, so only Firefox and Chrome can be used to view presentations.

  [ffmpeg]: http://ffmpeg.org/
  [Popcorn.js]: http://popcornjs.org/

## Quick Start ##

1. Run `python manage.py runserver`.

2. Edit [script.html][] to your liking. Each plain-text line is text to be narrated, while all HTML elements are slides that the narration voices over. **Warning**: The algorithm for parsing this file is currently very simple and fragile; every slide must begin with a `<`, and each slide and narration must be self-contained on a single line.

3. Open/reload http://127.0.0.1:8020 in Firefox or Chrome.

4. Repeat steps 2-3 as necessary until you're happy with your presentation. When you're finished, just upload everything in the `static-files` directory to a web server.

  [script.html]: https://github.com/toolness/quickpreso/blob/master/static-files/script.html
  [index.html]: https://github.com/toolness/quickpreso/blob/master/static-files/index.html
