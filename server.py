from flask import Flask, request, send_from_directory, jsonify, render_template_string, redirect, url_for
import os
import json
from shutil import copyfile
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
BASE_DIR = "/sdcard/Share"  # مسیر پوشه اصلی فایل‌ها
UPLOAD_FOLDER = BASE_DIR
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from core.app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
def list_files(subpath=""):
    full_path = os.path.join(BASE_DIR, subpath)
    items = []
    for fname in os.listdir(full_path):
        fpath = os.path.join(full_path, fname)
        rel_path = os.path.join(subpath, fname)
        ext = fname.lower().rsplit('.', 1)[-1] if '.' in fname else ''
        is_file = os.path.isfile(fpath)
        is_dir = os.path.isdir(fpath)
        is_image = ext in ['png', 'jpg', 'jpeg', 'gif', 'bmp', 'webp', 'svg']
        is_video = ext in ['mp4', 'webm', 'mkv', 'avi', 'mov', '3gp']
        is_audio = ext in ['mp3', 'wav', 'ogg', 'm4a', 'flac', 'aac']
        is_document = ext in ['pdf', 'doc', 'docx', 'txt', 'rtf']
        is_archive = ext in ['zip', 'rar', '7z', 'tar', 'gz']
        
        # اطلاعات فایل
        size = os.path.getsize(fpath) if is_file else 0
        modified = datetime.fromtimestamp(os.path.getmtime(fpath)).strftime('%Y-%m-%d %H:%M')
        
        items.append({
            'name': fname,
            'path': rel_path.replace('\\', '/'),
            'is_dir': is_dir,
            'is_file': is_file,
            'is_image': is_image,
            'is_video': is_video,
            'is_audio': is_audio,
            'is_document': is_document,
            'is_archive': is_archive,
            'ext': ext,
            'size': size,
            'modified': modified
        })
    return items

def format_file_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024.0:
            return f"{size:.2f} {unit}"
        size /= 1024.0
    return f"{size:.2f} TB"

@app.route('/')
def index():
    return redirect(url_for('browse', subpath=''))

@app.route('/browse/', defaults={'subpath': ''})
@app.route('/browse/<path:subpath>')
def browse(subpath):
    files = list_files(subpath)
    current_path = subpath
    parent_path = os.path.dirname(subpath) if subpath else ''
    return render_template_string("""<!DOCTYPE html>
<html>
<head>
    <title>File Manager</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        :root {
            --primary-color: #007AFF;
            --secondary-color: #5856D6;
            --background-color: #000000;
            --surface-color: #1C1C1E;
            --surface-secondary: #2C2C2E;
            --text-primary: #FFFFFF;
            --text-secondary: #8E8E93;
            --border-color: #38383A;
            --success-color: #30D158;
            --danger-color: #FF453A;
            --warning-color: #FF9F0A;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: var(--background-color);
            color: var(--text-primary);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            overflow-x: hidden;
        }

        .header {
            background: var(--surface-color);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid var(--border-color);
            position: sticky;
            top: 0;
            z-index: 100;
            padding: 1rem 0;
        }

        .header-content {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 1rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 1rem;
        }

        .header-left {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .header-title {
            font-size: 1.2rem;
            font-weight: 600;
            color: var(--text-primary);
            margin: 0;
        }

        .breadcrumb {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 0.8rem;
            color: var(--text-secondary);
        }

        .breadcrumb a {
            color: var(--primary-color);
            text-decoration: none;
            transition: opacity 0.2s;
        }

        .breadcrumb a:hover {
            opacity: 0.7;
        }

        .add-btn {
            background: var(--primary-color);
            color: white;
            border: none;
            padding: 0.6rem 1rem;
            border-radius: 8px;
            cursor: pointer;
            font-size: 0.8rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 0.4rem;
            transition: all 0.2s;
        }

        .add-btn:hover {
            background: #0056CC;
            transform: translateY(-1px);
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 1rem;
        }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
            gap: 1rem;
            margin-top: 1rem;
        }

        .item {
            background: var(--surface-color);
            border-radius: 12px;
            padding: 1rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.2s;
            border: 1px solid transparent;
            position: relative;
            user-select: none;
        }

        .item:hover {
            background: var(--surface-secondary);
            border-color: var(--border-color);
            transform: translateY(-2px);
        }

        .item.selected {
            background: var(--primary-color);
            color: white;
        }

        .item-icon {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
            display: block;
        }

        .item-preview {
            width: 80px;
            height: 80px;
            margin: 0 auto 0.5rem;
            border-radius: 8px;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            background: var(--surface-secondary);
        }

        .item-preview img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .item-preview video {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .item-name {
            font-size: 0.8rem;
            word-break: break-word;
            line-height: 1.3;
            margin-bottom: 0.3rem;
        }

        .item-info {
            font-size: 0.7rem;
            color: var(--text-secondary);
        }

        .bottom-actions {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: var(--surface-color);
            border-top: 1px solid var(--border-color);
            padding: 1rem;
            display: none;
            backdrop-filter: blur(10px);
        }

        .bottom-actions.show {
            display: block;
        }

        .actions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(80px, 1fr));
            gap: 1rem;
            max-width: 400px;
            margin: 0 auto;
        }

        .action-btn {
            background: none;
            border: none;
            color: var(--text-primary);
            font-size: 0.7rem;
            cursor: pointer;
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.3rem;
            padding: 0.5rem;
            border-radius: 8px;
            transition: background 0.2s;
        }

        .action-btn:hover {
            background: var(--surface-secondary);
        }

        .action-btn.danger {
            color: var(--danger-color);
        }

        .action-icon {
            font-size: 1.2rem;
        }

        .drop-zone {
            border: 2px dashed var(--border-color);
            border-radius: 12px;
            padding: 2rem;
            text-align: center;
            margin: 1rem 0;
            transition: all 0.2s;
            color: var(--text-secondary);
        }

        .drop-zone.drag-over {
            border-color: var(--primary-color);
            background: rgba(0, 122, 255, 0.1);
            color: var(--primary-color);
        }

        .file-input {
            display: none;
        }

        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.8);
            backdrop-filter: blur(10px);
            z-index: 1000;
        }

        .modal.show {
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .modal-content {
            background: var(--surface-color);
            border-radius: 16px;
            padding: 2rem;
            max-width: 90vw;
            max-height: 90vh;
            overflow: auto;
        }

        .close-btn {
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: none;
            border: none;
            color: var(--text-primary);
            font-size: 1.5rem;
            cursor: pointer;
        }

        @media (max-width: 768px) {
            .grid {
                grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
                gap: 0.8rem;
            }
            
            .header-content {
                flex-wrap: wrap;
                gap: 0.5rem;
            }
            
            .header-left {
                flex-direction: column;
                align-items: flex-start;
                gap: 0.3rem;
            }
            
            .header-title {
                font-size: 1.1rem;
            }
            
            .actions-grid {
                grid-template-columns: repeat(5, 1fr);
            }
        }

        .progress-bar {
            width: 100%;
            height: 4px;
            background: var(--surface-secondary);
            border-radius: 2px;
            overflow: hidden;
            margin-top: 1rem;
            display: none;
        }

        .progress-fill {
            height: 100%;
            background: var(--primary-color);
            transition: width 0.3s ease;
        }

        .empty-state {
            text-align: center;
            padding: 4rem 2rem;
            color: var(--text-secondary);
        }

        .empty-state-icon {
            font-size: 4rem;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <div class="header">
        <div class="header-content">
            <div class="header-left">
                <h1 class="header-title">📁 Dropbox</h1>
                {% if current_path %}
                    <div class="breadcrumb">
                        <a href="{{ url_for('browse', subpath='') }}">Home</a>
                        <span>›</span>
                        <span>{{ current_path.split('/')[-1] if '/' in current_path else current_path }}</span>
                    </div>
                {% endif %}
            </div>
            <button class="add-btn" onclick="document.getElementById('fileInput').click()">
                <span>+</span>
                <span>Add Files</span>
            </button>
        </div>
    </div>

    <div class="container">
        <div class="drop-zone" id="dropZone">
            <div style="font-size: 2rem; margin-bottom: 1rem;">📁</div>
            <div>Drag and drop files here or click "Add Files" to upload</div>
        </div>

        <div class="progress-bar" id="progressBar">
            <div class="progress-fill" id="progressFill"></div>
        </div>

        {% if files %}
            <div class="grid" id="fileGrid">
                {% for f in files %}
                <div class="item" data-path="{{ f.path }}" data-name="{{ f.name }}" data-type="{{ 'folder' if f.is_dir else 'file' }}">
                    {% if f.is_dir %}
                        <div class="item-icon">📁</div>
                        <div class="item-name">{{ f.name }}</div>
                        <div class="item-info">Folder</div>
                    {% elif f.is_image %}
                        <div class="item-preview">
                            <img src="{{ url_for('get_file', filepath=f.path) }}" alt="{{ f.name }}">
                        </div>
                        <div class="item-name">{{ f.name }}</div>
                        <div class="item-info">{{ format_file_size(f.size) }}</div>
                    {% elif f.is_video %}
                        <div class="item-preview">
                            <video src="{{ url_for('get_file', filepath=f.path) }}" muted></video>
                        </div>
                        <div class="item-name">{{ f.name }}</div>
                        <div class="item-info">{{ format_file_size(f.size) }}</div>
                    {% elif f.is_audio %}
                        <div class="item-icon">🎵</div>
                        <div class="item-name">{{ f.name }}</div>
                        <div class="item-info">{{ format_file_size(f.size) }}</div>
                    {% elif f.is_document %}
                        <div class="item-icon">📄</div>
                        <div class="item-name">{{ f.name }}</div>
                        <div class="item-info">{{ format_file_size(f.size) }}</div>
                    {% elif f.is_archive %}
                        <div class="item-icon">📦</div>
                        <div class="item-name">{{ f.name }}</div>
                        <div class="item-info">{{ format_file_size(f.size) }}</div>
                    {% else %}
                        <div class="item-icon">📄</div>
                        <div class="item-name">{{ f.name }}</div>
                        <div class="item-info">{{ format_file_size(f.size) }}</div>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        {% else %}
            <div class="empty-state">
                <div class="empty-state-icon">📁</div>
                <h3>No files found</h3>
                <p>This folder is empty. Add some files to get started.</p>
            </div>
        {% endif %}
    </div>

    <div class="bottom-actions" id="bottomActions">
        <div class="actions-grid">
            <button class="action-btn" onclick="shareItem()">
                <div class="action-icon">📤</div>
                <div>Share</div>
            </button>
            <button class="action-btn" onclick="renameItem()">
                <div class="action-icon">✏️</div>
                <div>Rename</div>
            </button>
            <button class="action-btn" onclick="moveItem()">
                <div class="action-icon">📁</div>
                <div>Move</div>
            </button>
            <button class="action-btn" onclick="copyItem()">
                <div class="action-icon">📋</div>
                <div>Copy</div>
            </button>
            <button class="action-btn danger" onclick="deleteItem()">
                <div class="action-icon">🗑️</div>
                <div>Delete</div>
            </button>
        </div>
    </div>

    <div class="modal" id="modal">
        <div class="modal-content" id="modalContent">
            <button class="close-btn" onclick="closeModal()">×</button>
            <div id="modalBody"></div>
        </div>
    </div>

    <input type="file" id="fileInput" class="file-input" multiple onchange="handleFiles(this.files)">

    <script>
        let selectedItem = null;
        let longPressTimer = null;
        let touchStartTime = 0;

        // Initialize
        document.addEventListener('DOMContentLoaded', function() {
            setupEventListeners();
            setupDragAndDrop();
        });

        function setupEventListeners() {
            const items = document.querySelectorAll('.item');
            items.forEach(item => {
                // Click events
                item.addEventListener('click', function(e) {
                    if (selectedItem) {
                        clearSelection();
                        return;
                    }
                    
                    if (item.dataset.type === 'folder') {
                        window.location.href = '/browse/' + item.dataset.path;
                    } else {
                        openFile(item.dataset.path);
                    }
                });

                // Long press for mobile
                item.addEventListener('touchstart', function(e) {
                    touchStartTime = Date.now();
                    longPressTimer = setTimeout(() => {
                        selectItem(item);
                    }, 500);
                });

                item.addEventListener('touchend', function(e) {
                    clearTimeout(longPressTimer);
                    if (Date.now() - touchStartTime < 500) {
                        // Short tap
                        if (selectedItem) {
                            clearSelection();
                        }
                    }
                });

                // Context menu for desktop
                item.addEventListener('contextmenu', function(e) {
                    e.preventDefault();
                    selectItem(item);
                });
            });
        }

        function setupDragAndDrop() {
            const dropZone = document.getElementById('dropZone');
            
            ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, preventDefaults, false);
                document.body.addEventListener(eventName, preventDefaults, false);
            });

            ['dragenter', 'dragover'].forEach(eventName => {
                dropZone.addEventListener(eventName, highlight, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, unhighlight, false);
            });

            dropZone.addEventListener('drop', handleDrop, false);
        }

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        function highlight() {
            document.getElementById('dropZone').classList.add('drag-over');
        }

        function unhighlight() {
            document.getElementById('dropZone').classList.remove('drag-over');
        }

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            handleFiles(files);
        }

        function handleFiles(files) {
            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                formData.append('files', files[i]);
            }

            uploadFiles(formData);
        }

        function uploadFiles(formData) {
            const progressBar = document.getElementById('progressBar');
            const progressFill = document.getElementById('progressFill');
            
            progressBar.style.display = 'block';
            
            fetch('/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                progressBar.style.display = 'none';
                if (data.success) {
                    location.reload();
                } else {
                    alert('Upload failed: ' + data.message);
                }
            })
            .catch(error => {
                progressBar.style.display = 'none';
                alert('Upload failed: ' + error);
            });
        }

        function selectItem(item) {
            selectedItem = item;
            item.classList.add('selected');
            document.getElementById('bottomActions').classList.add('show');
        }

        function clearSelection() {
            if (selectedItem) {
                selectedItem.classList.remove('selected');
                selectedItem = null;
            }
            document.getElementById('bottomActions').classList.remove('show');
        }

        function openFile(path) {
            window.open('/files/' + path, '_blank');
        }

        function shareItem() {
            if (!selectedItem) return;
            
            const path = selectedItem.dataset.path;
            const url = window.location.origin + '/files/' + path;
            
            if (navigator.share) {
                navigator.share({
                    title: selectedItem.dataset.name,
                    url: url
                });
            } else {
                navigator.clipboard.writeText(url).then(() => {
                    alert('Link copied to clipboard');
                });
            }
            clearSelection();
        }

        function renameItem() {
            if (!selectedItem) return;
            
            const currentName = selectedItem.dataset.name;
            const newName = prompt('Enter new name:', currentName);
            
            if (newName && newName !== currentName) {
                // API call to rename
                fetch('/api/rename', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        oldPath: selectedItem.dataset.path,
                        newName: newName
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('Rename failed: ' + data.message);
                    }
                });
            }
            clearSelection();
        }

        function moveItem() {
            alert('Move functionality coming soon');
            clearSelection();
        }

        function copyItem() {
            alert('Copy functionality coming soon');
            clearSelection();
        }

        function deleteItem() {
            if (!selectedItem) return;
            
            if (confirm('Are you sure you want to delete this item?')) {
                fetch('/api/delete', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        path: selectedItem.dataset.path
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert('Delete failed: ' + data.message);
                    }
                });
            }
            clearSelection();
        }

        function closeModal() {
            document.getElementById('modal').classList.remove('show');
        }

        // Close bottom actions when clicking outside
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.item') && !e.target.closest('.bottom-actions')) {
                clearSelection();
            }
        });

        // Keyboard shortcuts
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape') {
                clearSelection();
                closeModal();
            }
        });
    </script>
</body>
</html>
""", files=files, current_path=current_path, parent_path=parent_path, format_file_size=format_file_size)

# API endpoints
@app.route('/upload', methods=['POST'])
def upload_files():
    try:
        files = request.files.getlist('files')
        uploaded_files = []
        
        for file in files:
            if file.filename != '':
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                uploaded_files.append(filename)
        
        return jsonify({'success': True, 'files': uploaded_files})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/rename', methods=['POST'])
def rename_file():
    try:
        data = request.json
        old_path = os.path.join(BASE_DIR, data['oldPath'])
        new_name = secure_filename(data['newName'])
        new_path = os.path.join(os.path.dirname(old_path), new_name)
        
        os.rename(old_path, new_path)
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/delete', methods=['POST'])
def delete_file():
    try:
        data = request.json
        file_path = os.path.join(BASE_DIR, data['path'])
        
        if os.path.isfile(file_path):
            os.remove(file_path)
        elif os.path.isdir(file_path):
            os.rmdir(file_path)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/files/<path:filepath>')
def get_file(filepath):
    dirpath = os.path.join(BASE_DIR, os.path.dirname(filepath))
    filename = os.path.basename(filepath)
    return send_from_directory(directory=dirpath, path=filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)