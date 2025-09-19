import os
from PIL import Image
import subprocess

def compress_file(input_path, output_dir):
    filename = os.path.basename(input_path)
    name, ext = os.path.splitext(filename)
    output_path = os.path.join(output_dir, f"{name}_compressed{ext}")
    
    file_ext = ext[1:].lower()
    
    if file_ext in ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff']:
        return compress_image(input_path, output_path)
    elif file_ext in ['pdf']:
        return compress_pdf(input_path, output_path)
    else:
        # For other file types, just copy the file
        with open(input_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                f_out.write(f_in.read())
        return output_path

def compress_image(input_path, output_path, quality=85):
    with Image.open(input_path) as img:
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
            # Always use .jpg for converted images
            output_path = os.path.splitext(output_path)[0] + '.jpg'
        img.save(output_path, optimize=True, quality=quality)
    return output_path

def compress_pdf(input_path, output_path):
    try:
        # Use Ghostscript for PDF compression
        subprocess.run([
            'gs', '-sDEVICE=pdfwrite', '-dCompatibilityLevel=1.4',
            '-dPDFSETTINGS=/ebook', '-dNOPAUSE', '-dQUIET', '-dBATCH',
            f'-sOutputFile={output_path}', input_path
        ], check=True)
        return output_path
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback: copy the file if compression fails
        with open(input_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                f_out.write(f_in.read())
        return output_path