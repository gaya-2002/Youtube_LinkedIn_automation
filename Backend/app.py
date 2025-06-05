from flask import Flask, request, jsonify
from flask_cors import CORS 
from src.main import youtubeautomationFlow
from src.state.memory import SharedState

app = Flask(__name__)
CORS(app)

state = SharedState()
main_class = youtubeautomationFlow()

@app.route('/process', methods=['POST'])
def process():
    data = request.json
    youtube_url = data.get('youtubeURL')

    try:
        inputs = {'url':youtube_url}
        main_class.generate_blog(inputs)

        with open(state.get('edited_post_output'), 'r', encoding = 'utf-8') as file:
            result = file.read()
        
        return jsonify({'result':result})
    except Exception as e:
        return jsonify({'error',str((e))}), 500

@app.route('/regenerate', methods=['POST'])
def regenerate():
    try:
        data = request.json
        prompt = data.get('prompt', 'Improve and brief the blog')  # fallback prompt

        print(f"Regenerating with prompt: {prompt}")
        
        main_class.regenerate_content({'prompt': prompt})

        with open(state.get('rewritten_post'), 'r', encoding='utf-8') as file:
            result = file.read()
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save', methods=['POST'])
def save_blog():
    data = request.get_json()
    unique_id = data.get('id')
    youtube_url = data.get('url')
    chat_history = data.get('chatMessages')

    print("Chat history data:", data)

    required_keys = ['id','url','chatMessages']
    for key in required_keys:
        if key not in data:
            return jsonify({'error': 'Missing fields'}), 400

    return jsonify({'message': 'Saved', 'id': unique_id})

    
if __name__ == '__main__':
    app.run(port=5000, debug=True)