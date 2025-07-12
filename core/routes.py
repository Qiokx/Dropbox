import os
from flask import request, send_from_directory, jsonify, render_template, redirect, url_for
from werkzeug.utils import secure_filename
from .utils import list_files, format_file_size, BASE_DIR

def register_routes(app):
    # Register static folder for CSS
    app.static_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), ''))
    @app.route('/')
    def index():
        return redirect(url_for('browse', subpath=''))

    @app.route('/browse/', defaults={'subpath': ''})
    @app.route('/browse/<path:subpath>')
    def browse(subpath):
        files = list_files(subpath)
        current_path = subpath
        parent_path = os.path.dirname(subpath) if subpath else ''
        return render_template('template.html', files=files, current_path=current_path, parent_path=parent_path, format_file_size=format_file_size)

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
