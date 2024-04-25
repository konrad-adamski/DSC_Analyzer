jsonMeasurement.y = jsonMeasurement.y.map(yWert => (yWert+1) * 100000);


// Erstellung des Bokeh-Plots ------------------------------------------------------------------------------------------
var plot = Bokeh.Plotting.figure({
    width: 700,
    height: 420,
    x_axis_label: "Temperatur in °C",
    y_axis_label: "DSC in mW/mg",
    x_range: [-50, 300]
});

plot.xaxis.ticker = new Bokeh.SingleIntervalTicker({ interval: 50 }); // 50 als Intervall festlegen
// Ändern der y-Achsenticks
plot.yaxis.ticker = new Bokeh.SingleIntervalTicker({ interval: 2000 }); // 10,000 als Intervall festlegen
plot.yaxis.formatter =new Bokeh.CustomJSTickFormatter({
    args: {},
    code: `
        return ((tick / 100000)-1).toFixed(2);
    `
});


 // Erstellen der Datenquelle für die Linie
var lineSource = new Bokeh.ColumnDataSource({
    data: jsonMeasurement
});

// Hinzufügen der Linie zum Plot
plot.line({field: "x"}, {field: "y"}, {source: lineSource, line_width: 2, line_color: "blue"});


// Erstellen der Datenquellen
var source1 = new Bokeh.ColumnDataSource({
    data: {
        x: json_get_x_by(1, jsonPeak),
        y: get_y(json_get_x_by(1, jsonPeak), jsonMeasurement)
    }
});

var source2 = new Bokeh.ColumnDataSource({
    data: {
        x: json_get_x_by(2, jsonPeak),
        y: get_y(json_get_x_by(2, jsonPeak), jsonMeasurement)
    }
});

var source3 = new Bokeh.ColumnDataSource({
    data: {
        x: json_get_x_by(3, jsonPeak),
        y: get_y(json_get_x_by(3, jsonPeak), jsonMeasurement)
    }
});


if (source1.data["x"].length > 0) {
    plot.circle({field: "x"}, {field: "y"}, {source: source1, size: 10, color: ["#0B610B", "#31B404"]});
    plot.line({field: "x"}, {field: "y"}, {source: source1, line_width:2, line_color:"#088A08"});
}

if (source2.data["x"].length > 0) {
    plot.circle({field: "x"}, {field: "y"}, {source: source2, size: 10, color: ["#8A2908", "#DF7401"]});
    plot.line({field: "x"}, {field: "y"}, {source: source2, line_width:2, line_color:"#B45F04"});
}
if (source3.data["x"].length > 0) {
    plot.circle({field: "x"}, {field: "y"}, {source: source3, size: 10, color: ["#151515", "#6E6E6E"]});
    plot.line({field: "x"}, {field: "y"}, {source: source3, line_width:2, line_color:"#424242"});
}


// Durchlaufen des jsonPeak-Objekts
for (let key in jsonPeak) {
    let peakTemperature = jsonPeak[key]["Peak_Temperature"];
    let peak_y = getNearestY(peakTemperature, jsonMeasurement)
    plot.x([peakTemperature], [peak_y], { size: 10, color: '#3399ff', line_width: 2});
}


// Definieren der Tooltip-Nachrichts
var tooltip_x = [
    ("Temperatur"),
    ("@x°C")
];

// Hinzufügen des Hover-Tools zum Plot und Übergabe aller Glyphenobjekte
plot.add_tools(new Bokeh.HoverTool({
    tooltips: [tooltip_x]
}));

plot.toolbar.active_drag = null;

// Anzeigen des Bokeh-Plots
Bokeh.Plotting.show(plot, '#plot');


// Plot Functions ------------------------------------------------------------------------------------------------------

// Funktion zum Aktualisieren der Punkte
function updatePoint(send_boolean, sliderId) {
    updateTableClass("area_red");
    let slider = document.getElementById(sliderId); // Holen Sie sich den Schieberegler
    let input = document.getElementById(sliderId+"_text");

    let type = sliderId.split('_')[1];
    let index = sliderId.split('_')[2];

    if (type === "start"){
        jsonPeak[index]["Start_Temperature"] = slider.value
    } else {
        jsonPeak[index]["End_Temperature"] = slider.value
    }

    if (index === "1") {
        source1.data.x = json_get_x_by(1, jsonPeak);
        source1.data.y = get_y(json_get_x_by(1, jsonPeak), jsonMeasurement);
        source1.change.emit();
    } else if (index === "2") {
        source2.data.x = json_get_x_by(2, jsonPeak);
        source2.data.y = get_y(json_get_x_by(2, jsonPeak), jsonMeasurement);
        source2.change.emit();
    } else if (index === "3") {
        source3.data.x = json_get_x_by(3, jsonPeak);
        source3.data.y = get_y(json_get_x_by(3, jsonPeak), jsonMeasurement);
        source3.change.emit();
    }

    // Aktualisieren des Textfeldes
    input.value = slider.value

    // Send
    if (send_boolean) {
        document.getElementById("jsonPeak").value = JSON.stringify(jsonPeak);
        sendPointForm();
    }
}

// Funktion zum Aktualisieren des Schiebereglers basierend auf dem Textfeldwert
function updateSlider(sliderId) {
    let inputValue = parseFloat(document.getElementById(sliderId + "_text").value);
    let slider = document.getElementById(sliderId); // Holen Sie sich den Schieberegler

    // Überprüfen, ob der Input innerhalb des zulässigen Bereichs liegt
    if (inputValue >= -50 && inputValue <= 300) {
        slider.value = inputValue; // Aktualisieren des Schiebereglers
    } else if (inputValue < -50) {
        slider.value = -50;
    } else if (inputValue > 300) {
        slider.value = 300;
    }

    updatePoint(true, sliderId); // Aufrufen der updatePoint-Funktion mit der aktuellen Schieberegler-ID
}

function sendPointForm() {
    let form = document.getElementById('pointForm');
    form.submit();
}
