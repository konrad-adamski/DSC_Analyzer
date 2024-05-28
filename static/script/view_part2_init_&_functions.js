var start_colors = ["#151515", "#0B610B", "#8A2908"]
var end_colors = ["#6E6E6E", "#31B404", "#DF7401"]
var line_colors = ["#424242", "#088A08", "#B45F04"]

for (let i = 1; i <= peakCount; i++) {
    let slider_start = document.getElementById("slider_start_" + i);
    let slider_end = document.getElementById("slider_end_" + i);

    let input_start = document.getElementById("slider_start_" + i + "_text");
    let input_end = document.getElementById("slider_end_" + i + "_text");

    slider_start.value = jsonPeak[i]["T1 (Onset) [°C]"];
    input_start.value = jsonPeak[i]["T1 (Onset) [°C]"];

    slider_end.value = jsonPeak[i]["T2 (Offset) [°C]"];
    input_end.value = jsonPeak[i]["T2 (Offset) [°C]"];

    // Farben
    let modulo = i % 3;
    let startColor = start_colors[modulo];
    let endColor = end_colors[modulo];
    // Fügen Sie CSS-Regeln dynamisch hinzu
    addSliderThumbStyle(i, startColor, endColor);

    // Fügen Sie die dynamisch generierten Klassen hinzu
    slider_start.classList.add(`slider-start${i}`);
    slider_end.classList.add(`slider-end${i}`);

}


function addSliderThumbStyle(index, startColor, endColor) {
    const styleId = 'dynamic-slider-styles';
    let styleElement = document.getElementById(styleId);

    if (!styleElement) {
        styleElement = document.createElement('style');
        styleElement.id = styleId;
        document.head.appendChild(styleElement);
    }

    // Füge neue Regeln dem bestehenden Style-Element hinzu
    styleElement.textContent += `
        .slider-start${index}::-webkit-slider-thumb {
            background: ${startColor};
        }
        .slider-start${index}::-moz-range-thumb {
            background: ${startColor};
        }
        .slider-end${index}::-webkit-slider-thumb {
            background: ${endColor};
        }
        .slider-end${index}::-moz-range-thumb {
            background: ${endColor};
        }`;
}



// JSON Functions ------------------------------------------------------------------------------------------------------

 // Definition einer Funktion zur Extraktion von abwechselnden Werten aus JSON-Objekten
 function json_get_x(data) {
     let result = [];
     for (let key in data) {
         result.push(data[key]["T1 (Onset) [°C]"]);
         result.push(data[key]["T2 (Offset) [°C]"]);
     }
     return result;
 }

 function json_get_x_by(key, data) {
     key = String(key)
     if (key in data) { // Überprüfen, ob der Schlüssel im JSON-Objekt vorhanden ist
         let result = [];
         result.push(data[key]["T1 (Onset) [°C]"]);
         result.push(data[key]["T2 (Offset) [°C]"]);
         return result;
     } else {
         return []; // Leere Liste zurückgeben, wenn der Schlüssel nicht vorhanden ist
     }
 }


// Value Mapping Functions ------------------------------------
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