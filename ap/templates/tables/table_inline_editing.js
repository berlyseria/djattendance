// ajax call to database for inline editing
// updated gives the change, pk the object id, field the model field, url the model POST url
function editDB(updated, objPK, field, url) {
  var pass = false;

  $.ajax({
    async: false,
    type: "POST",
    url,
    data: {
      change: updated,
      pk: objPK,
      f: field
    },
    success(response) {
      pass = true;
      new Notification(Notification.SUCCESS, "Saved").show();
    },
    error(jqXHR, textStatus, errorThrown) {
      new Notification(Notification.ERROR, "Could not update").show();
    }
  });

  return pass;
}

// blur function - for clicking outside input when editing is finished
function blurFunction(textbox, orig, clicked, url) {
  var passed = false;
  if (textbox.value !== orig) {
    passed = editDB(textbox.value, clicked.parent().attr("id"), clicked.attr("class"), url);
  }

  if (passed) {
    clicked.text(textbox.value);
  } else {
    clicked.text(orig);
  }
}

// set event for inline editing when you double click remembrance text or reference.
// parameters: clicked is table field; POST url; textarea Boolean
function tableInlineEdit(clicked, url, textarea) {
  var orig = clicked.text(); // for comparison
  if (orig === "None") {
    orig = "";
  }

  var input;
  var cols = $("table thead tr th").eq($("td").index(clicked)%7).width()/9;
  if (textarea) {
    input = $("<textarea>", {
      rows: orig.length/cols, // estimate height of text to minimize table resizing
      cols,
      blur() {
        blurFunction(this, orig, clicked, url);
      },
      keyup(e) { // if pressing enter
        if (e.which === 13) { input.blur(); }
      }
    });

    input.val(orig);
  } else {
    input = $("<input>", {
      value: orig,
      type: "text",
      blur() {
        blurFunction(this, orig, clicked, url);
      },
      keyup(e) { // if pressing enter
        if (e.which === 13) { input.blur(); }
      }
    });
  }

  input.appendTo( clicked.empty() ).focus();
}