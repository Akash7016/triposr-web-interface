from flask import Flask, render_template_string, request, jsonify, send_from_directory
import os
import threading
import subprocess
import uuid
import requests
from urllib.parse import urlparse
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

task_status = {}
task_outputs = {}

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Upload Photos</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
    <style>
        body {
            margin: 0;
            font-family: 'Inter', Arial, sans-serif;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            position: relative;
        }
        body::before {
            content: '';
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: 
                radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 255, 255, 0.15) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(120, 119, 198, 0.15) 0%, transparent 50%);
            pointer-events: none;
            z-index: 0;
        }
        .card {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            max-width: 480px;
            box-shadow: 
                0 8px 32px rgba(0, 0, 0, 0.1),
                0 2px 16px rgba(0, 0, 0, 0.08);
            padding: 0 0 24px 0;
            position: relative;
            z-index: 1;
        }
        .card-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 24px 32px;
            font-size: 1.3rem;
            font-weight: 600;
            border-radius: 20px 20px 0 0;
            margin: 0;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        .upload-area {
            margin: 32px 32px 0 32px;
            border: 2px dashed rgba(102, 126, 234, 0.3);
            border-radius: 16px;
            background: linear-gradient(145deg, rgba(245, 248, 255, 0.8), rgba(239, 246, 255, 0.6));
            padding: 40px 20px 32px 20px;
            text-align: center;
            transition: all 0.3s ease;
            position: relative;
        }
        .upload-area:hover {
            border-color: rgba(102, 126, 234, 0.6);
            background: linear-gradient(145deg, rgba(239, 246, 255, 0.9), rgba(219, 234, 254, 0.7));
            transform: translateY(-2px);
        }
        .upload-icon {
            width: 64px;
            margin-bottom: 12px;
            opacity: 0.8;
        }
        .upload-area-text {
            color: #64748b;
            font-size: 1rem;
        }
        .browse-link {
            color: #667eea;
            text-decoration: none;
            cursor: pointer;
            font-weight: 600;
            transition: color 0.2s ease;
        }
        .browse-link:hover {
            color: #764ba2;
        }
        .file-types {
            font-size: 0.95rem;
            color: #94a3b8;
            margin-top: 6px;
        }
        .divider {
            margin: 24px 0 16px 0;
            border: none;
            border-top: 1px solid #e5e7eb;
        }
        .import-url {
            display: flex;
            gap: 12px;
            margin: 24px 32px 16px 32px;
            align-items: center;
        }
        .import-url input {
            flex: 1;
            padding: 12px 16px;
            border-radius: 12px;
            border: 2px solid rgba(102, 126, 234, 0.2);
            font-size: 1rem;
            background: rgba(255, 255, 255, 0.8);
            transition: all 0.2s ease;
        }
        .import-url input:focus {
            outline: none;
            border-color: #667eea;
            background: rgba(255, 255, 255, 0.95);
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }
        .import-url button {
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 12px 24px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
        }
        .import-url button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(16, 185, 129, 0.4);
        }
        .card-footer {
            display: flex;
            justify-content: flex-end;
            gap: 12px;
            margin: 32px 32px 0 32px;
        }
        .footer-btn {
            background: rgba(243, 244, 246, 0.8);
            color: #374151;
            border: none;
            border-radius: 12px;
            padding: 12px 32px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            backdrop-filter: blur(10px);
        }
        .footer-btn.primary {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }
        .footer-btn.primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 25px rgba(102, 126, 234, 0.5);
        }
        .progress-bar {
            width: 90%;
            background: #f3f4f6;
            border-radius: 8px;
            margin: 18px auto 0 auto;
            height: 8px;
            position: relative;
        }
        .progress {
            background: #2563eb;
            height: 8px;
            border-radius: 8px;
            transition: width 0.3s;
        }
        .preview-img {
            margin: 18px auto 0 auto;
            max-width: 90%;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.08);
            display: block;
        }
        .filename-row {
            display: flex;
            align-items: center;
            gap: 12px;
            margin: 18px 0 0 32px;
        }
        .filename-img {
            width: 32px;
            height: 32px;
            object-fit: cover;
            border-radius: 6px;
            border: 1px solid #e5e7eb;
        }
        .filename-text {
            font-size: 1rem;
            color: #222;
            font-weight: 500;
        }
    </style>
</head>
<body>
    <div class="card">
        <div class="card-header">Upload Photos</div>
        <form id="upload-form" enctype="multipart/form-data" onsubmit="return false;">
            <div class="upload-area">
                <img src="https://img.icons8.com/ios/100/image--v2.png" class="upload-icon" alt="Upload Icon" />
                <div class="upload-area-text">Drop your image here, or <span class="browse-link" onclick="document.getElementById('file-input').click();">browse</span></div>
                <div class="file-types">Supported: PNG, JPG, JPEG, WEBP</div>
                <input type="file" id="file-input" name="file" accept="image/*" style="display:none;" onchange="previewFile(event)">
                <div style="position:relative; display:inline-block;">
                    <img id="preview" class="preview-img" style="display:none;" />
                    <button id="remove-preview" type="button" style="display:none; position:absolute; top:8px; right:8px; background:#fff; border:none; border-radius:50%; width:32px; height:32px; box-shadow:0 2px 8px rgba(0,0,0,0.12); cursor:pointer; font-size:1.2rem; color:#2563eb;">&#10006;</button>
                </div>
            </div>
            <div class="import-url">
                <input type="url" id="url-input" placeholder="Paste image URL here..." />
                <button type="button" onclick="importFromURL()">Import</button>
            </div>
            <div class="card-footer">
                <button type="button" class="footer-btn primary" onclick="startUpload()">Upload</button>
            </div>
        </form>
        <div style="margin:16px 32px;">
            <div id="progress-bar-container" style="width:100%;height:8px;background:#f3f4f6;border-radius:8px;margin:0 0 8px 0;display:none;">
                <div id="progress-bar" style="height:8px;width:0%;background:#2563eb;border-radius:8px;transition:width 0.3s;"></div>
            </div>
            <div id="progress-status" style="font-weight:600;color:#2563eb;margin-bottom:8px;"></div>
            <pre id="progress-log" style="background:#f5f8ff;border:1px solid #e0e7ff;border-radius:8px;padding:12px;max-height:200px;overflow-y:auto;font-size:0.85rem;color:#222;white-space:pre-wrap;display:none;"></pre>
        </div>
        <div id="output-list" style="margin:16px 32px;"></div>
    </div>
    <script>
    let taskId = null;
    function startUpload() {
        const preview = document.getElementById('preview');
        const fileInput = document.getElementById('file-input');
        
        // Check if we have an imported URL image
        if (preview.dataset.importUrl && preview.style.display === 'block') {
            // Process imported URL image
            const imageUrl = preview.dataset.importUrl;
            
            document.getElementById('progress-status').innerText = 'Importing and processing image...';
            document.getElementById('progress-bar-container').style.display = 'block';
            document.getElementById('progress-log').style.display = 'block';
            
            fetch('/import_url', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({url: imageUrl})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    taskId = data.task_id;
                    pollProgress();
                } else {
                    document.getElementById('progress-status').innerText = 'Import failed: ' + (data.error || 'Unknown error');
                }
            })
            .catch(err => {
                document.getElementById('progress-status').innerText = 'Import failed: Network error';
                console.error('Import failed:', err);
            });
        } else if (fileInput.files && fileInput.files[0]) {
            // Process uploaded file
            const formData = new FormData(document.getElementById('upload-form'));
            document.getElementById('progress-status').innerText = 'Uploading...';
            document.getElementById('progress-bar-container').style.display = 'block';
            document.getElementById('progress-log').style.display = 'block';
            
            fetch('/ajax_upload', {
                method: 'POST',
                body: formData
            }).then(response => response.json())
            .then(data => {
                if (data.success) {
                    taskId = data.task_id;
                    pollProgress();
                } else {
                    document.getElementById('progress-status').innerText = 'Upload failed.';
                }
            });
        } else {
            alert('Please select a file or import an image from URL first.');
        }
    }

    function pollProgress() {
        if (!taskId) return;
        fetch(`/ajax_progress?task_id=${taskId}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('progress-status').innerText = data.status;
                document.getElementById('progress-log').innerText = data.log;
                
                // Progress bar logic: estimate based on log content and status
                let percent = 0;
                if (data.status === 'Processing...') {
                    // Estimate progress based on log length (crude but works)
                    percent = Math.min(85, Math.floor(data.log.length / 100));
                } else if (data.status === 'Completed') {
                    percent = 100;
                } else if (data.status === 'Failed' || data.status.startsWith('Error')) {
                    percent = 100;
                }
                document.getElementById('progress-bar').style.width = percent + '%';
                
                // Continue polling if still processing
                if (data.status === 'Processing...' || data.status === 'Starting...') {
                    setTimeout(pollProgress, 1000);
                } else {
                    // Task completed, get outputs
                    fetch(`/ajax_outputs?task_id=${taskId}`)
                        .then(response => response.json())
                        .then(data => {
                            if (data.files.length > 0) {
                                let outHtml = '<h3 style="margin-bottom:8px;">Download Results:</h3>';
                                data.files.forEach(f => {
                                    outHtml += `<div style="margin:4px 0;"><a href="/download_output/${taskId}/${f}" download style="color:#2563eb;text-decoration:none;font-weight:500;">${f}</a></div>`;
                                });
                                document.getElementById('output-list').innerHTML = outHtml;
                            }
                        });
                }
            })
            .catch(err => {
                document.getElementById('progress-status').innerText = 'Error checking progress';
                console.error('Progress check failed:', err);
            });
    }

    function importFromURL() {
        const urlInput = document.getElementById('url-input');
        const imageUrl = urlInput.value.trim();
        
        if (!imageUrl) {
            alert('Please enter an image URL');
            return;
        }
        
        // Validate URL format
        try {
            new URL(imageUrl);
        } catch {
            alert('Please enter a valid URL');
            return;
        }
        
        // Show the image as preview directly from the URL
        const preview = document.getElementById('preview');
        
        // Set up event handlers for this specific import
        preview.onload = function() {
            // Image loaded successfully, show preview
            preview.style.display = 'block';
            document.getElementById('remove-preview').style.display = 'block';
            urlInput.value = ''; // Clear the input
            
            // Clear the event handlers to prevent issues later
            preview.onload = null;
            preview.onerror = null;
        };
        
        preview.onerror = function() {
            // Only show error if this was a genuine load failure during import
            if (preview.src === imageUrl) {
                alert('Failed to load image from URL. Please check the URL and try again.');
            }
            // Clear the event handlers
            preview.onload = null;
            preview.onerror = null;
        };
        
        // Set the image source to the URL for preview
        preview.src = imageUrl;
        
        // Store the URL for later processing
        preview.dataset.importUrl = imageUrl;
    }

    function previewFile(event) {
        const input = event.target;
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const preview = document.getElementById('preview');
                preview.src = e.target.result;
                preview.style.display = 'block';
                preview.dataset.importUrl = ''; // Clear import URL data
                document.getElementById('remove-preview').style.display = 'block';
            }
            reader.readAsDataURL(input.files[0]);
        }
    }
    
    function clearPreview() {
        const preview = document.getElementById('preview');
        
        // Clear the error and load event handlers to prevent unwanted alerts
        preview.onerror = null;
        preview.onload = null;
        
        // Clear the preview
        preview.src = '';
        preview.style.display = 'none';
        preview.dataset.importUrl = ''; // Clear import URL data
        document.getElementById('remove-preview').style.display = 'none';
        document.getElementById('file-input').value = '';
        document.getElementById('url-input').value = '';
    }
    
    document.getElementById('remove-preview').onclick = clearPreview;
    </script>
</body>
</html>
'''

def run_batch(image_path, task_id):
    task_status[task_id] = {'status': 'Processing...', 'log': 'Starting TripoSR processing...\n'}
    try:
        # Convert to absolute path
        abs_image_path = os.path.abspath(image_path)
        
        # Create output directory for this task
        output_dir = os.path.join('C:\\ai3d\\TripoSR', 'output', task_id)
        os.makedirs(output_dir, exist_ok=True)
        
        # Call run_fast.ps1 directly with the uploaded image
        cmd = [
            'powershell.exe', 
            '-NoLogo', '-NoProfile', '-ExecutionPolicy', 'Bypass',
            '-File', r'C:\ai3d\TripoSR\run_fast.ps1',
            '-img', abs_image_path,
            '-out', output_dir
        ]
        
        # Stream output in real-time
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                                 text=True, universal_newlines=True, bufsize=1)
        
        log_lines = [f'Starting TripoSR processing...\nImage: {abs_image_path}\nOutput: {output_dir}\n']
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                line = line.rstrip() + '\n'
                log_lines.append(line)
                task_status[task_id] = {'status': 'Processing...', 'log': ''.join(log_lines)}
        
        retcode = process.poll()
        final_status = 'Completed' if retcode == 0 else 'Failed'
        task_status[task_id] = {'status': final_status, 'log': ''.join(log_lines)}
        
        # List output files
        if os.path.exists(output_dir):
            task_outputs[task_id] = [f for f in os.listdir(output_dir) if f.endswith(('.obj', '.png', '.jpg', '.mtl'))]
        else:
            task_outputs[task_id] = []
            
    except Exception as e:
        error_msg = f'Error occurred: {str(e)}\n'
        task_status[task_id] = {'status': f'Error: {str(e)}', 'log': error_msg}
        task_outputs[task_id] = []

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/ajax_upload', methods=['POST'])
def ajax_upload():
    file = request.files.get('file')
    if not file:
        return jsonify({'success': False})
    filename = secure_filename(file.filename)
    save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(save_path)
    task_id = str(uuid.uuid4())
    task_status[task_id] = {'status': 'Starting...', 'log': ''}
    thread = threading.Thread(target=run_batch, args=(save_path, task_id))
    thread.start()
    return jsonify({'success': True, 'task_id': task_id})

@app.route('/import_url', methods=['POST'])
def import_url():
    import requests
    from urllib.parse import urlparse
    
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'success': False, 'error': 'No URL provided'})
    
    image_url = data['url']
    
    try:
        # Download image from URL
        response = requests.get(image_url, stream=True, timeout=30)
        response.raise_for_status()
        
        # Check if it's an image
        content_type = response.headers.get('content-type', '')
        if not content_type.startswith('image/'):
            return jsonify({'success': False, 'error': 'URL does not point to an image'})
        
        # Generate filename from URL
        parsed_url = urlparse(image_url)
        filename = os.path.basename(parsed_url.path)
        if not filename or '.' not in filename:
            # Generate filename based on content type
            ext = content_type.split('/')[-1]
            if ext in ['jpeg', 'jpg', 'png', 'webp']:
                filename = f'imported_image_{uuid.uuid4().hex[:8]}.{ext}'
            else:
                filename = f'imported_image_{uuid.uuid4().hex[:8]}.jpg'
        
        filename = secure_filename(filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        
        # Save the image
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        # Start processing
        task_id = str(uuid.uuid4())
        task_status[task_id] = {'status': 'Starting...', 'log': ''}
        thread = threading.Thread(target=run_batch, args=(save_path, task_id))
        thread.start()
        
        # Return preview URL for the imported image
        preview_url = f'/static/uploads/{filename}'
        return jsonify({'success': True, 'task_id': task_id, 'preview_url': preview_url})
        
    except requests.exceptions.RequestException as e:
        return jsonify({'success': False, 'error': f'Failed to download image: {str(e)}'})
    except Exception as e:
        return jsonify({'success': False, 'error': f'Error processing URL: {str(e)}'})

@app.route('/ajax_progress')
def ajax_progress():
    task_id = request.args.get('task_id')
    info = task_status.get(task_id)
    if info is None:
        return jsonify({'status': 'Unknown', 'log': ''})
    return jsonify({'status': info['status'], 'log': info['log']})

@app.route('/ajax_outputs')
def ajax_outputs():
    task_id = request.args.get('task_id')
    files = task_outputs.get(task_id, [])
    return jsonify({'files': files})

@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/download_output/<task_id>/<filename>')
def download_output(task_id, filename):
    output_dir = os.path.join('C:\\ai3d\\TripoSR', 'output', task_id)
    return send_from_directory(output_dir, filename, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)