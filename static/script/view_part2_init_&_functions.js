for (let i = 1; i <= Math.min(peakCount, 3); i++) {
    let slider_start = document.getElementById("slider_start_" + i);
    let slider_end = document.getElementById("slider_end_" + i);

    let input_start = document.getElementById("slider_start_" + i + "_text");
    let input_end = document.getElementById("slider_end_" + i + "_text");

    slider_start.value = jsonPeak[i]["Start_Temperature"];
    input_start.value = jsonPeak[i]["Start_Temperature"];

    slider_end.value = jsonPeak[i]["End_Temperature"];
    input_end.value = jsonPeak[i]["End_Temperature"];
}



// JSON Functions ------------------------------------------------------------------------------------------------------

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