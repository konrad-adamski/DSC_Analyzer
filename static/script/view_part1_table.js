// init
getRowTable(jsonPeak, "area_green");


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

function openModal() {
    document.getElementById('myModal').style.display = 'block';
}

function closeModal() {
    document.getElementById('myModal').style.display = 'none';
}


function tableAddPeak() {
    closeModal();
    // Setzen des JSON-Strings in das versteckte Eingabefeld
    document.getElementById('jsonPeak_table_add').value = JSON.stringify(jsonPeak);

    // Absenden des Formulars
    document.getElementById('tableAddForm').submit();

}


