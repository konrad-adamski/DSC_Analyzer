 function excelDownload(projectId, attribute) {
    let attr_type = attribute.split("_")[0]
    let filename = prompt("Bitte geben Sie den Namen für die Excel-Datei ein:", `project${projectId}_${attr_type}_download`);
    if (filename) {
        filename += ".xlsx";  // Stelle sicher, dass die Dateiendung angehängt wird
        window.location.href = `/download_excel/${projectId}/${attribute}/${encodeURIComponent(filename)}`;
    }
}



function excelDownload_for_series(projectId, attribute, sample, segment) {
    let attr_type = attribute.split("_")[0];
    let filename = prompt("Bitte geben Sie den Namen für die Excel-Datei ein:", `project${projectId}_${attr_type}_${sample}_download`);
    if (filename) {
        filename += ".xlsx";  // Stelle sicher, dass die Dateiendung angehängt wird
        let encodedFilename = encodeURIComponent(filename);
        let encodedSample = encodeURIComponent(sample);
        let encodedSegment = encodeURIComponent(segment);
        window.location.href = `/download_excel/${projectId}/${attribute}/${encodedFilename}/?sample=${encodedSample}&segment=${encodedSegment}`;
    }
}
