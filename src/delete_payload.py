import os

def handle_delete_payload(data, payload_dir, allowed_extensions):
    payload = data.get("payload")
    if not payload:
        return {'error': 'filename parameter is required'}, 400

    if '..' in payload:
        return {'error': 'Invalid filename'}, 400

    file_extension = payload.rsplit('.', 1)[-1].lower() if '.' in payload else ''
    if file_extension not in allowed_extensions:
        return {'error': f'File type {file_extension} not allowed'}, 400

    safe_payload_dir = os.path.abspath(payload_dir)
    full_path = os.path.abspath(os.path.join(payload_dir, payload))

    if not full_path.startswith(safe_payload_dir):
         return {'error': 'Invalid filepath'}, 400

    filepath = full_path

    if os.path.exists(filepath) and os.path.isfile(filepath):
        try:
            os.remove(filepath)
            
            directory = os.path.dirname(filepath)
            while directory.startswith(safe_payload_dir) and directory != safe_payload_dir:
                if not os.listdir(directory):
                    os.rmdir(directory)
                    directory = os.path.dirname(directory)
                else:
                    break

            return {
                'success': True,
                'message': f'File {payload} deleted successfully',
                'filename': payload
            }, 200
        except Exception as e:
            return {'error': str(e), 'message': 'Failed to delete file'}, 500
    else:
        return {
            'error': 'File not found',
            'filename': payload
        }, 404
