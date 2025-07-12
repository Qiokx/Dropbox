import os
from datetime import datetime

BASE_DIR = "/sdcard/Share"

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
