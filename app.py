from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, emit
import re
import uuid
import urllib.request
import json
import socket as sock

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lanparty2024'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

queue = []
current_index = -1  # -1 = semmi sem megy

VIDEO_ID_PATTERNS = [
    r'(?:youtube\.com/watch\?.*?v=)([a-zA-Z0-9_-]{11})',
    r'(?:youtu\.be/)([a-zA-Z0-9_-]{11})',
    r'(?:youtube\.com/embed/)([a-zA-Z0-9_-]{11})',
    r'(?:youtube\.com/shorts/)([a-zA-Z0-9_-]{11})',
    r'(?:youtube\.com/v/)([a-zA-Z0-9_-]{11})',
]

def extract_video_id(url):
    url = url.strip()
    for pattern in VIDEO_ID_PATTERNS:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url
    return None

def get_video_title(video_id):
    try:
        oembed = f'https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json'
        req = urllib.request.Request(oembed, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            return data.get('title', 'Ismeretlen videó')
    except Exception:
        return 'Ismeretlen videó'

def queue_state():
    return {'queue': queue, 'current_index': current_index}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/player')
def player():
    return render_template('player.html')

@app.route('/api/queue')
def get_queue():
    return jsonify(queue_state())

@app.route('/api/add', methods=['POST'])
def add_video():
    global queue, current_index
    data = request.get_json() or {}
    url = (data.get('url') or '').strip()
    submitter = (data.get('submitter') or 'Névtelen').strip()[:50] or 'Névtelen'

    video_id = extract_video_id(url)
    if not video_id:
        return jsonify({'error': 'Érvénytelen YouTube URL'}), 400

    title = get_video_title(video_id)
    item = {
        'id': str(uuid.uuid4()),
        'video_id': video_id,
        'title': title,
        'submitter': submitter,
    }

    was_empty = len(queue) == 0
    queue.append(item)
    if was_empty:
        current_index = 0

    socketio.emit('queue_updated', queue_state())
    if was_empty:
        socketio.emit('play_video', {'video_id': video_id, 'index': 0, 'item': item})

    return jsonify({'success': True, 'item': item})

@app.route('/api/next', methods=['POST'])
def next_video():
    global current_index
    current_index += 1
    if current_index < len(queue):
        video = queue[current_index]
        socketio.emit('queue_updated', queue_state())
        socketio.emit('play_video', {
            'video_id': video['video_id'],
            'index': current_index,
            'item': video,
        })
        return jsonify({'success': True, 'video': video})
    else:
        socketio.emit('queue_updated', queue_state())
        socketio.emit('queue_ended', {})
        return jsonify({'success': True, 'done': True})

@app.route('/api/skip', methods=['POST'])
def skip_video():
    return next_video()

@app.route('/api/remove', methods=['POST'])
def remove_video():
    global queue, current_index
    data = request.get_json() or {}
    item_id = data.get('id')

    idx = next((i for i, v in enumerate(queue) if v['id'] == item_id), None)
    if idx is None:
        return jsonify({'error': 'Nem található'}), 404

    playing_this = idx == current_index

    queue.pop(idx)

    if not queue:
        current_index = -1
        socketio.emit('queue_updated', queue_state())
        socketio.emit('queue_ended', {})
        return jsonify({'success': True})

    if idx < current_index:
        current_index -= 1
    elif playing_this:
        # current_index stays, now points to the next video (or past end)
        if current_index >= len(queue):
            socketio.emit('queue_updated', queue_state())
            socketio.emit('queue_ended', {})
            return jsonify({'success': True})
        video = queue[current_index]
        socketio.emit('queue_updated', queue_state())
        socketio.emit('play_video', {
            'video_id': video['video_id'],
            'index': current_index,
            'item': video,
        })
        return jsonify({'success': True})

    socketio.emit('queue_updated', queue_state())
    return jsonify({'success': True})

@app.route('/api/clear', methods=['POST'])
def clear_queue():
    global queue, current_index
    queue = []
    current_index = -1
    socketio.emit('queue_updated', queue_state())
    socketio.emit('queue_ended', {})
    return jsonify({'success': True})

@socketio.on('connect')
def handle_connect():
    emit('queue_updated', queue_state())

if __name__ == '__main__':
    hostname = sock.gethostname()
    try:
        local_ip = sock.gethostbyname(hostname)
    except Exception:
        local_ip = '???.???.???.???'

    print()
    print('  LAN Party Lejatszo')
    print('  ================================')
    print(f'  Lokalis:  http://localhost')
    print(f'  LAN:      http://{local_ip}')
    print(f'  Player:   http://localhost/player')
    print('  ================================')
    print('  Ctrl+C a leallitashoz')
    print()

    socketio.run(app, host='0.0.0.0', port=80, debug=False)
