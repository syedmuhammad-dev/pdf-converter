from flask import Flask, render_template, request, send_file, jsonify
import os
from werkzeug.utils import secure_filename
from utils.converters import convert_document, convert_image
from utils.compressors import compress_file
from utils.file_handlers import allowed_file, get_file_category, clean_temp_files

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads/temp'
app.config['PROCESSED_FOLDER'] = 'uploads/processed'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        file_category = get_file_category(filename)
        return jsonify({
            'message': 'File uploaded successfully',
            'filename': filename,
            'file_category': file_category
        })
    
    return jsonify({'error': 'File type not allowed'}), 400

@app.route('/convert', methods=['POST'])
def convert_file():
    data = request.json
    filename = data.get('filename')
    target_format = data.get('target_format')
    compress = data.get('compress', False)
    
    if not filename or not target_format:
        return jsonify({'error': 'Missing parameters'}), 400
    
    input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(input_path):
        return jsonify({'error': 'File not found'}), 404
    
    file_category = get_file_category(filename)
    
    try:
        # Convert the file
        if file_category == 'document':
            output_path = convert_document(input_path, target_format, app.config['PROCESSED_FOLDER'])
        elif file_category == 'image':
            output_path = convert_image(input_path, target_format, app.config['PROCESSED_FOLDER'])
        else:
            return jsonify({'error': 'Unsupported file type for conversion'}), 400
        
        # Compress if requested
        if compress:
            output_path = compress_file(output_path, app.config['PROCESSED_FOLDER'])
        
        download_filename = os.path.basename(output_path)
        return jsonify({
            'message': 'Conversion successful',
            'download_url': f'/download/{download_filename}',
            'filename': download_filename
        })
    
    except Exception as e:
        return jsonify({'error': f'Conversion failed: {str(e)}'}), 500

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    if os.path.exists(file_path):
        return send_file(file_path, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

@app.after_request
def after_request(response):
    # Clean up temporary files after each request
    try:
        clean_temp_files(app.config['UPLOAD_FOLDER'])
        clean_temp_files(app.config['PROCESSED_FOLDER'], max_age_minutes=30)
    except:
        pass  # Don't fail the request if cleanup fails
    return response

if __name__ == '__main__':
    app.run(debug=True)