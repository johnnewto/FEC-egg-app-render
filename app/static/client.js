var el = x => document.getElementById(x);
var test_file_loaded = false;

function showPicker(inputId) { el('file-input').click(); }

function showPicked(input) {
    el('upload-label').innerHTML = input.files[0].name;
    var reader = new FileReader();
    reader.onload = function (e) {
        el('image-picked').src = e.target.result;
        el('image-picked').className = '';
        test_file_loaded = false;
    }
    reader.readAsDataURL(input.files[0]);
}

function analyze() {
    var uploadFiles = el('file-input').files;
    if (!test_file_loaded && uploadFiles.length != 1) alert('Please select 1 file to analyze!');

    el('analyze-button').innerHTML = 'Analyzing...';
    var xhr = new XMLHttpRequest();
    var loc = window.location
    xhr.responseType = 'blob';
    if (test_file_loaded )
        xhr.open('POST', `${loc.protocol}//${loc.hostname}:${loc.port}/analyzeTest`, true);
    else
        xhr.open('POST', `${loc.protocol}//${loc.hostname}:${loc.port}/analyze`, true);

    xhr.onerror = function() {alert (xhr.responseText);}
    xhr.onload = function(e) {
        if (this.readyState === 4) {
            // var response = JSON.parse(e.target.responseText);
            // el('result-label').innerHTML = `Result = ${response['result']}`;
            var blob = this.response;
            el('image-picked').src = window.URL.createObjectURL(blob);
            el('image-picked').className = '';
        }
        el('analyze-button').innerHTML = 'Analyze';
    }
    xhr.onloadend = function (e) {
        console.log("end")
    }
    if (test_file_loaded )
        xhr.send(null);
    else {
        var fileData = new FormData();
        fileData.append('file', uploadFiles[0]);
        xhr.send(fileData);
    }
}


function test() {
    var xhr = new XMLHttpRequest();
    var loc = window.location
    xhr.responseType = 'blob';

    xhr.open('GET', `${loc.protocol}//${loc.hostname}:${loc.port}/test`, true);
    xhr.onerror = function() {alert (xhr.responseText);}
    xhr.onload = function(e) {
        if (this.readyState === 4) {
            // var response = JSON.parse(e.target.responseText);
            // el('result-label').innerHTML = `Result = ${response['result']}`;
            var blob = this.response;
            el('image-picked').src = window.URL.createObjectURL(blob);
            el('image-picked').className = '';
        }
    }
    xhr.onloadend = function (e) {
        console.log("end")
        test_file_loaded = true;
        el('upload-label').innerHTML =  'Test File'
    }

    xhr.send(null);
}