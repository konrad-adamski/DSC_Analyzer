jsonMeasurement.y = jsonMeasurement.y.map(yWert => (yWert+1) * 100000);
getRowTable(jsonPeak, "area_green");

for (let i = 1; i <= peakCount; i++) {
    let slider_start = document.getElementById("slider_start_" + i);
    let slider_end = document.getElementById("slider_end_" + i);

    let input_start = document.getElementById("slider_start_" + i + "_text");
    let input_end = document.getElementById("slider_end_" + i + "_text");

    slider_start.value = jsonPeak[i]["Start_Temperature"];
    input_start.value = jsonPeak[i]["Start_Temperature"];

    slider_end.value = jsonPeak[i]["End_Temperature"];
    input_end.value = jsonPeak[i]["End_Temperature"];
}

// Erstellen des Bokeh-Plots
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


// Erstellen der Datenquelle
var source = new Bokeh.ColumnDataSource({
    data: {
        x: json_get_x(jsonPeak),
        y: get_y(json_get_x(jsonPeak), jsonMeasurement)
    }
});

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
    var point1 = plot.circle({field: "x"}, {field: "y"}, {source: source1, size: 10, color: ["#0B610B", "#31B404"]});
    plot.line({field: "x"}, {field: "y"}, {source: source1, line_width:2, line_color:"#088A08"});
}

if (source2.data["x"].length > 0) {
    var point2 = plot.circle({field: "x"}, {field: "y"}, {source: source2, size: 10, color: ["#8A2908", "#DF7401"]});
    plot.line({field: "x"}, {field: "y"}, {source: source2, line_width:2, line_color:"#B45F04"});
}
if (source3.data["x"].length > 0) {
    plot.circle({field: "x"}, {field: "y"}, {source: source3, size: 10, color: ["#151515", "#6E6E6E"]});
    plot.line({field: "x"}, {field: "y"}, {source: source3, line_width:2, line_color:"#424242"});
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

// Table Functions -------------
function getRowTable(rowData, areaClass) {
        const tableBody = document.querySelector("#peakTable tbody");
        // Tabelle leeren
        //tableBody.innerHTML = '';

        for (const key in rowData) {
            if (rowData.hasOwnProperty(key)) {
                const row = document.createElement("tr");
                row.innerHTML = `<td>${key}</td>
                                 <td>${rowData[key]["Peak_Temperature"]}</td>
                                 <td class="${areaClass}">${rowData[key]["Area"]}</td>`;
                tableBody.appendChild(row);
            }
        }
        // MDL-Komponenten neu initialisieren
        componentHandler.upgradeElements(tableBody);
    }


function updateTableClass(newClass) {
    const tableBody = document.querySelector("#peakTable tbody");
    // Durch alle Zeilen der Tabelle iterieren
    const rows = tableBody.querySelectorAll("tr");
    rows.forEach((row) => {
        // Das letzte td-Element in jeder Zeile auswählen
        const lastTd = row.lastElementChild;
        // Alte Klassen entfernen, die auf "area_" beginnen (optional)
        Array.from(lastTd.classList).forEach((cls) => {
            if (cls.startsWith("area_")) {
                lastTd.classList.remove(cls);
            }
        });
        // Neue Klasse hinzufügen
        lastTd.classList.add(newClass);
    });
}

function tableDeletePeaks() {
    const rows = document.querySelectorAll('#peakTable tbody tr');
    const selectedKeys = [];

    // Schlüssel der ausgewählten Zeilen sammeln
    rows.forEach((row) => {
        if (row.classList.contains('is-selected')) {
            const key = row.cells[1].textContent;  // Zweite Spalte für Schlüssel
            selectedKeys.push(key);
        }
    });

    // Entfernen der ausgewählten Peaks aus jsonPeak
    selectedKeys.forEach(key => {
        delete jsonPeak[key];
    });

    // Setzen des aktualisierten JSON-Strings in das versteckte Eingabefeld
    document.getElementById('jsonPeak_table').value = JSON.stringify(jsonPeak);

    // Absenden des Formulars
    document.getElementById('tableDeleteForm').submit();
}

function tableAddPeak() {
    // Setzen des JSON-Strings in das versteckte Eingabefeld
    document.getElementById('jsonPeak_table_add').value = JSON.stringify(jsonPeak);

    // Absenden des Formulars
    document.getElementById('tableAddForm').submit();

}

// JSON Functions ---------

 // Definition einer Funktion zur Extraktion von abwechselnden Werten aus JSON-Objekten
 function json_get_x(data) {
     let result = [];
     for (let key in data) {
         result.push(data[key]["Start_Temperature"]);
         result.push(data[key]["End_Temperature"]);
     }
     return result;
 }

 function json_get_x_by(key, data) {
     key = String(key)
     if (key in data) { // Überprüfen, ob der Schlüssel im JSON-Objekt vorhanden ist
         let result = [];
         result.push(data[key]["Start_Temperature"]);
         result.push(data[key]["End_Temperature"]);
         return result;
     } else {
         return []; // Leere Liste zurückgeben, wenn der Schlüssel nicht vorhanden ist
     }
 }

 function get_y(inputValues, lineData) {
     if (inputValues.length > 0) {
         return inputValues.map(inputValue => getNearestY(inputValue, lineData));
     } else {
         return []
     }
 }

 function getNearestY(xValue, lineData) {

     // Finde den nächsten x-Wert
     const nearestX = getNearestX(xValue, lineData['x']);

     // Finde den Index des nächsten x-Werts in der x-Liste
     let nearestIndex = lineData['x'].findIndex(x => x === nearestX);

     return parseInt(lineData['y'][nearestIndex]);
 }

 function getNearestX(inputValue, xList) {
     return xList.reduce((nearestX, currentX) =>
         Math.abs(currentX - inputValue) < Math.abs(nearestX - inputValue) ? currentX : nearestX
     );
 }

// Plot functions --------------------
function custom_y_formatter(y_value) {
    return y_value // Teilt den y-Wert durch 100000
}


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


// Funktion zum Überprüfen, ob der Teilstring "S3" in einem Parameter der URL enthalten ist
function hasS3Parameter() {
    let urlParams = new URLSearchParams(window.location.search);
    for (let [key, value] of urlParams.entries()) {
        if (value.includes('S3')) {
            return true;
        }
    }
    return false;
}
