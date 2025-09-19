document.addEventListener('DOMContentLoaded', function() {
    const dropArea = document.getElementById('dropArea');
    const fileInput = document.getElementById('fileInput');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const fileType = document.getElementById('fileType');
    const conversionOptions = document.getElementById('conversionOptions');
    const targetFormat = document.getElementById('targetFormat');
    const convertBtn = document.getElementById('convertBtn');
    const progressSection = document.getElementById('progressSection');
    const progressBar = document.querySelector('.progress');
    const progressText = document.getElementById('progressText');
    const downloadSection = document.getElementById('downloadSection');
    const downloadLink = document.getElementById('downloadLink');
    
    let currentFile = null;
    let fileCategory = null;

    // Drag and drop functionality
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight() {
        dropArea.classList.add('dragover');
    }
    
    function unhighlight() {
        dropArea.classList.remove('dragover');
    }
    
    dropArea.addEventListener('drop', handleDrop, false);
    fileInput.addEventListener('change', handleFileSelect, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }
    
    function handleFileSelect(e) {
        const files = e.target.files;
        handleFiles(files);
    }
    
    function handleFiles(files) {
        if (files.length > 0) {
            const file = files[0];
            uploadFile(file);
        }
    }
    
    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert('Error: ' + data.error);
                return;
            }
            
            currentFile = data.filename;
            fileCategory = data.file_category;
            
            // Show file info
            fileName.textContent = data.filename;
            fileType.textContent = fileCategory;
            fileInfo.classList.remove('hidden');
            
            // Populate conversion options
            populateFormatOptions(fileCategory);
            
            // Show conversion options
            conversionOptions.classList.remove('hidden');
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Upload failed. Please try again.');
        });
    }
    
    function populateFormatOptions(category) {
        // Clear existing options
        targetFormat.innerHTML = '<option value="">Select target format</option>';
        
        let formats = [];
        if (category === 'document') {
            formats = [
                {value: 'pdf', text: 'PDF'},
                {value: 'docx', text: 'DOCX (Word)'},
                {value: 'odt', text: 'ODT (OpenDocument)'},
                {value: 'txt', text: 'TXT (Plain Text)'}
            ];
        } else if (category === 'image') {
            formats = [
                {value: 'png', text: 'PNG'},
                {value: 'jpg', text: 'JPG'},
                {value: 'webp', text: 'WEBP'},
                {value: 'bmp', text: 'BMP'},
                {value: 'tiff', text: 'TIFF'}
            ];
        }
        
        formats.forEach(format => {
            const option = document.createElement('option');
            option.value = format.value;
            option.textContent = format.text;
            targetFormat.appendChild(option);
        });
    }
    
    convertBtn.addEventListener('click', startConversion);
    
    function startConversion() {
        const format = targetFormat.value;
        const compress = document.getElementById('compressOption').checked;
        
        if (!format) {
            alert('Please select a target format');
            return;
        }
        
        // Show progress section
        conversionOptions.classList.add('hidden');
        progressSection.classList.remove('hidden');
        
        // Simulate progress
        let progress = 0;
        const interval = setInterval(() => {
            progress += 5;
            progressBar.style.width = `${progress}%`;
            
            if (progress >= 90) {
                clearInterval(interval);
            }
        }, 200);
        
        // Send conversion request
        fetch('/convert', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: currentFile,
                target_format: format,
                compress: compress
            })
        })
        .then(response => response.json())
        .then(data => {
            clearInterval(interval);
            progressBar.style.width = '100%';
            
            if (data.error) {
                progressText.textContent = 'Error: ' + data.error;
                setTimeout(() => {
                    progressSection.classList.add('hidden');
                    conversionOptions.classList.remove('hidden');
                }, 2000);
                return;
            }
            
            progressText.textContent = 'Conversion complete!';
            
            // Show download section
            setTimeout(() => {
                progressSection.classList.add('hidden');
                downloadLink.href = data.download_url;
                downloadLink.textContent = `Download ${data.filename}`;
                downloadSection.classList.remove('hidden');
            }, 1000);
        })
        .catch(error => {
            clearInterval(interval);
            console.error('Error:', error);
            progressText.textContent = 'Conversion failed. Please try again.';
            setTimeout(() => {
                progressSection.classList.add('hidden');
                conversionOptions.classList.remove('hidden');
            }, 2000);
        });
    }
});