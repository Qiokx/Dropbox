from flask import request, send_from_directory, jsonify, render_template, redirect, url_for
import os
from .utils import list_files, format_file_size
from werkzeug.utils import secure_filename

def register_routes(app):

    # صفحه اصلی: نمایش محتوای دایرکتوری اصلی
    @app.route('/')
    def index():
        from .utils import get_base_dir, list_files, format_file_size
        files = list_files("")
        current_path = ""
        parent_path = ""
        return render_template("browse.html", files=files, current_path=current_path, parent_path=parent_path, format_file_size=format_file_size)

    @app.route('/browse/', defaults={'subpath': ''})
    @app.route('/browse/<path:subpath>')
    def browse(subpath):
        from .utils import get_base_dir
        files = list_files(subpath, get_base_dir())
        current_path = subpath
        parent_path = os.path.dirname(subpath) if subpath else ''
        return render_template(
            'browse.html',
            files=files,
            current_path=current_path,
            parent_path=parent_path,
            format_file_size=format_file_size
        )

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
            from .utils import get_base_dir
            old_path = os.path.join(get_base_dir(), data['oldPath'])
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
            from .utils import get_base_dir
            file_path = os.path.join(get_base_dir(), data['path'])
            if os.path.isfile(file_path):
                os.remove(file_path)
            elif os.path.isdir(file_path):
                os.rmdir(file_path)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)})

    @app.route('/files/<path:filepath>')
    def get_file(filepath):
        from .utils import get_base_dir
        dirpath = os.path.join(get_base_dir(), os.path.dirname(filepath))
        filename = os.path.basename(filepath)
        return send_from_directory(directory=dirpath, path=filename)
