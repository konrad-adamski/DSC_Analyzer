jsonMeasurement.y = jsonMeasurement.y.map(yWert => (yWert+1) * 100000);

// Erstellung des Bokeh-Plots ------------------------------------------------------------------------------------------
var plot = Bokeh.Plotting.figure({
    width: 700,
    height: 420,
    x_axis_label: "Temperatur in °C",
    y_axis_label: "DSC in mW",
    x_range: [-50, 300]
});

plot.xaxis.ticker = new Bokeh.SingleIntervalTicker({ interval: 50 }); // 50 als Intervall festlegen
// Ändern der y-Achsenticks
plot.yaxis.ticker = new Bokeh.SingleIntervalTicker({ interval: 50000 }); // 10,000 als Intervall festlegen
plot.yaxis.formatter =new Bokeh.CustomJSTickFormatter({
    args: {},
    code: `
        return ((tick / 100000)-1).toFixed(1);
    `
});


 // Erstellen der Datenquelle für die Linie
var lineSource = new Bokeh.ColumnDataSource({
    data: jsonMeasurement
});

// Hinzufügen der Linie zum Plot
plot.line({field: "x"}, {field: "y"}, {source: lineSource, line_width: 2, line_color: "blue"});


// Erstellen der Datenquellen
var sources = {};

Object.keys(jsonPeak).forEach(key => {
    sources[key] = new Bokeh.ColumnDataSource({
        data: {
            x: json_get_x_by(key, jsonPeak),
            y: get_y(json_get_x_by(key, jsonPeak), jsonMeasurement)
        }
    });
    console.log("Datenquelle erstellt für Key:", key, "mit Daten:", sources[key].data);
});

Object.keys(sources).forEach(key => {
    let modulo = key % 3;
    console.log("Modulo:", modulo);
    let source = sources[key];
    plot.line({field: "x"}, {field: "y"}, {source: source, line_width: 2, line_color: line_colors[modulo]});
    plot.circle({field: "x"}, {field: "y"}, {source: source, size: 10,
        color: [start_colors[modulo], end_colors[modulo]]});


    console.log("Grafik hinzugefügt für Key:", key);
});

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

    // Aktualisieren des Plots
    let source = sources[index];
    source.data.x = json_get_x_by(index, jsonPeak);
    source.data.y = get_y(json_get_x_by(index, jsonPeak), jsonMeasurement);
    source.change.emit();


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
