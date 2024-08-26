import os
from flask import Flask, send_from_directory, make_response, request, jsonify
from flask_socketio import SocketIO


app = Flask(__name__, static_folder='static', static_url_path='/')

socketio = SocketIO(app)

effects = [
    'fade', 'scale',
    'slide', 'slide-up', 'slide-down', 'slide-left', 'slide-right',
    'expand', 'expand-up', 'expand-down', 'expand-left', 'expand-right'
]

def get_image_filenames():
    image_dir = "static/images"
    try:
        return [f for f in os.listdir(image_dir)
                if f != ".gitignore" and os.path.isfile(os.path.join(image_dir, f))]
    except FileNotFoundError:
        return []

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/images')
def list_images():
    images = [f'images/{file}' for file in get_image_filenames()]
    return jsonify(images)

@app.route('/images/<path:filename>')
def serve_image(filename):
    response = make_response(send_from_directory(os.path.join(app.static_folder, 'images'), filename))
    response.headers['Cache-Control'] = 'public, max-age=31536000'
    return response

@app.route('/api/transition', methods=['GET'])
def api_transition():
    name = request.args.get('name')
    effect = request.args.get('effect')
    duration = request.args.get('duration')

    if not name:
        return jsonify({"error": "No name provided"}), 400
    
    if not effect:
        return jsonify({"error": "No effect provided"}), 400

    if not duration:
        return jsonify({"error": "No duration provided"}), 400

    image_filenames = get_image_filenames()
    duration = float(duration)

    if name not in image_filenames:
        return jsonify({"error": f"Image not found, available images: {', '.join(image_filenames)}"}), 404
    
    if effect not in effects:
        return jsonify({"error": f"Effect not supported, available effects: {', '.join(effects)}"}), 400
    
    if duration <= 0:
        return jsonify({"error": "Duration must be positive"}), 400

    socketio.emit('api_transition', (name, effect, duration), namespace='/')
    return jsonify({"message": f"Image transition broadcasted"}), 200


if __name__ == '__main__':
    socketio.run(app, debug=True)