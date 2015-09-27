

currentId = 0;

function getData(id) {
  if (id == 0) {
    return;
  }
  weapon = $('input[name=optionsWeapons]:checked', '#fencerform').val();
  $(".loading-image").show();
  $.getJSON("get?id="+id+"&weapon="+weapon,
      function(result) {
        $.getJSON("translate?id="+id , function (res) {
          name = res["name"]
          currentId = id;
          drawBasic(result, name);
          $(".loading-image").hide();
        });
      }
  );
}

function queryEvents(q) {
  $.getJSON("event?q="+q,
      function(result) {
          displayEvents(result);
          $(".loading-image").hide();
      }
  );
}

function rateEvent(tournament_id, event_id) {
  $.getJSON("rate_event?tournament_id="+tournament_id+"&event_id="+event_id,
      function(ratings) {
        for (i = 0 ; i < ratings.length; i++) {
            $("#title_box").append('<h3>' + ratings[i]["name"] + ' - ' + ratings[i]["birthyear"] + ' - ' + ratings[i]["rating"] + "</h3>");
        }
        $(".loading-image").hide();
      }
  );
}

function drawBasic(fencer, fullname) {
      // 116580
      dateseen = {}
      rows = [];
      fencer_name = fullname;
      console.log(fencer_name);
      if (fencer != 0) {
        for (i = 0; i < fencer['ratings'].length; i++) {
          if (fencer['ratings'][i]['date'] in dateseen)
            continue;
          dateseen[fencer['ratings'][i]['date']] = 1;
          rows.push([Date.parse(fencer['ratings'][i]['date']), fencer['ratings'][i]['rating']]);
        }
      }
      latest_rank = 0;
      if (rows.length != 0) {
        latest_rank = rows[rows.length - 1][1] 
      }
    $('#container').highcharts({

        credits: {
             enabled: false
        },
        chart: {
            type: 'line'
        },
        title: {
            text: ''
        },
        subtitle: {
            text: fencer_name + ' - ' + latest_rank.toFixed(2) + ' - ' + fencer["weapon"],
            style: {
                fontSize: '32px'
            }
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: { // don't display the dummy year
            },
            title: {
                text: 'Date'
            }
        },
        yAxis: {
            title: {
                text: 'Rating'
            },
        },
        tooltip: {
            headerFormat: '<b>{series.name}</b><br>',
            pointFormat: '{point.x:%e. %b}: {point.y:.2f}'
        },

        plotOptions: {
            series: {
                cursor:'pointer',
                marker: {
                    enabled: true
                },
                point: {
                    events: {
                        click: function (e) {
                          console.log(this);
                        }
                    }
                }
            }
        },

        series: [{
            name: fencer_name,
            // Define the data points. All series have a dummy year
            // of 1970/71 in order to be compared on the same x axis. Note
            // that in JavaScript, months start at 0 for January, 1 for February etc.
            data: rows
        }]
    });
} 
function drawFrame() {
    rows = []
    $('#container').highcharts({

        credits: {
             enabled: false
        },
        chart: {
            type: 'line'
        },
        title: {
            text: ''
        },
        subtitle: {
            text: "Example - 0.00"
        },
        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: { // don't display the dummy year
            },
            title: {
                text: 'Date'
            }
        },
        yAxis: {
            title: {
                text: 'Rating'
            },
        },
        tooltip: {
            headerFormat: '<b>{series.name}</b><br>',
            pointFormat: '{point.x:%e. %b}: {point.y:.2f}'
        },

        plotOptions: {
            series: {
                cursor:'pointer',
                marker: {
                    enabled: true
                },
            }
        },

        series: [{
            name: "Example",
            // Define the data points. All series have a dummy year
            // of 1970/71 in order to be compared on the same x axis. Note
            // that in JavaScript, months start at 0 for January, 1 for February etc.
            data: rows
        }]

    });
}

function displayEvents(events) {
  $("#title_thing").text("Click on the correct event...");
  $("#subtitle_thing").text("Tournament - Event - Start Date");
  $( "h3" ).empty();
  for (i = 0 ; i < events.length; i++) {
    $("#title_box").append('<h3 tournament_id="'+events[i]["tournament_id"]+'" event_id="' +events[i]["event_id"]+ '" tename="' + events[i]["tname"] + ' ' + events[i]["ename"]  + '">' + events[i]["tname"] + ' - ' + events[i]["ename"] + ' - ' + events[i]["start_date"] + "</h3>");
  }
  $("h3").click(function() {
      $(".loading-image").show();
      $("#title_thing").text($(this).attr('tename'));
      $("#subtitle_thing").text("Name - Birthyear - Latest Rating");
      $("h3").empty()
      ratings = rateEvent($(this).attr('tournament_id'), $(this).attr('event_id'));
  });
}

function displayNames(names) {
  $("#title_thing").text("Click on the correct fencer...");
  $("#subtitle_thing").text("Full Name - Birth Year - Last Tournament");
  $( "h3" ).empty();
  for (i = 0 ; i < names.length; i++) {
    $("#title_box").append('<h3 id="'+names[i]["id"]+'">' + names[i]["fullname"] + ' - ' + names[i]["birthyear"] + ' - ' + names[i]["t_date"]+ "</h3>");
  }
  $("h3").click(function() {
    getData($(this).attr('id'));
  });
}

function displayMore(names) {
}


$( document ).ready(function() {
    drawFrame();
  $(".pure-radio").click(function() {
    getData(currentId);
  });
});
$( "#fencerform" ).submit(function( event ) {
  value_string = $('#fenceridinput').val();
  if (!isNaN(value_string)) {
    getData(parseInt(value_string));
  } else {
    value_name = $.trim(value_string);
  $(".loading-image").show();
    $.getJSON("name?q="+value_name,
        function(result) {
          console.log(result);
          displayNames(result);
          $(".loading-image").hide();
        }
    );
  } 
  event.preventDefault();
});

$( "#eventform" ).submit(function( event ) {
  value_string = $('#eventquery').val();
  if (!isNaN(value_string)) {
    //console.log("hi")
    //queryEvents(value_string);
  } else {
    $(".loading-image").show();
    queryEvents(value_string);
  } 
  event.preventDefault();
});
