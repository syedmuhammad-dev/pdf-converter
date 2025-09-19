import os
from datetime import datetime, timedelta

# Allowed file extensions
ALLOWED_EXTENSIONS = {
    'document': ['pdf', 'docx', 'doc', 'odt', 'txt'],
    'image': ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp']
}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in \
           [ext for exts in ALLOWED_EXTENSIONS.values() for ext in exts]

def get_file_category(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    for category, extensions in ALLOWED_EXTENSIONS.items():
        if ext in extensions:
            return category
    return None

def clean_temp_files(directory, max_age_minutes=10):
    now = datetime.now()
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if os.path.isfile(file_path):
            file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if now - file_time > timedelta(minutes=max_age_minutes):
                os.remove(file_path)