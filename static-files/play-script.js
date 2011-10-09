$(window).ready(function() {
  var scriptLoaded = jQuery.Deferred();
  var metadataLoaded = jQuery.getJSON("script.json");
  $("#script").load("script.html", function() { scriptLoaded.resolve(); });
  $("#subtitle-toggle").click(function() {
    $("#subtitle").fadeToggle();
    if ($(this).text() == "Show subtitles")
      $(this).text("Hide subtitles")
    else
      $(this).text("Show subtitles")
  });
  jQuery.when(metadataLoaded, scriptLoaded).done(function(metadata) {
    var i = 0;
    var currTime = 0;
    var currVisual = null;
    var pop = Popcorn("#voiceover");
    var durations = metadata[0].durations;
    $("#script").contents().each(function() {
      if (this.nodeType == this.TEXT_NODE) {
        var subtitle = jQuery.trim(this.nodeValue);
        var speakingTime = durations[i];
        var pauseTime = durations[i+1];
        if (currVisual) {
          currVisual.end = currTime + speakingTime + pauseTime;
          pop.footnote(currVisual);
          currVisual = null;
        }
        pop.footnote({
          start: currTime,
          end: currTime + speakingTime,
          text: subtitle,
          target: 'subtitle'
        });
        currTime += speakingTime + pauseTime;
        i += 2;
      } else if (this.nodeType == this.ELEMENT_NODE) {
        currVisual = {
          text: $("<div></div>").append(this).html(),
          start: currTime,
          target: 'visual'
        };
      }
    });
    $("#throbber").hide();
    $("#content").show();
  });
});
