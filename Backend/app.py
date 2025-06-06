from flask import Flask, request, jsonify
from flask_cors import CORS 
from src.main import youtubeautomationFlow
from src.state.memory import SharedState
from pathlib import Path
import json

import shutil
import os

app = Flask(__name__)
CORS(app)

#global variables
state = SharedState()
main_class=None
id=None

def clear_folder(folder_path):
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)  # Remove file or link
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)  # Remove folder
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')

def set_folders(chat_id):
    state.set(chat_id,"main_path",str(Path(__file__).parent/"src"/"main.py"))
    state.set(chat_id,"downloaded_audio_path",str(Path(__file__).parent / "src"/"state"))


@app.route('/process', methods=['POST'])
def process():

    #data getting from json
    data = request.json
    youtube_url = data.get('youtubeURL')
    global id
    id = data.get('id')

    #other necessary functions
    state.set_chat_id(id)
    set_folders(id)
    clear_folder(state.get(id,"downloaded_audio_path"))

    try:
        global main_class
        main_class = youtubeautomationFlow(id)
        inputs = {'url':youtube_url}
        main_class.generate_blog(inputs)

        with open(state.get('edited_post_output'), 'r', encoding = 'utf-8') as file:
            title=file.line()
            result = file.read()
        
        state.set(id,"title",title)

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

        with open(state.get(id,'rewritten_post'), 'r', encoding='utf-8') as file:
            result = file.read()
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save', methods=['POST'])
def save_blog():
    data = request.get_json()
    unique_id = data.get('id')
    chat_history = data.get('chatMessages')

    print("Chat history data:", data)

    required_keys = ['id','url','chatMessages']
    for key in required_keys:
        if key not in data:
            return jsonify({'error': 'Missing fields'}), 400
        
    state.set(state.get(unique_id),"Chat_history",str(Path(state.get['Blog_output']).parent)+r'/chat_history.json')
    with open(state.get(unique_id,"Chat_history"),'w') as f:
        json.dump(chat_history, f, indent=4)

    return jsonify({'message': 'Saved', 'id': unique_id})

@app.route('/retrive_history',methods=['GET'])
def retrieve_history():
    data=request.json
    chat_id=data['id']
    file_path=state.get(chat_id,'Chat_history')

    with open(file_path, "r") as json_file:
        content = json.load(json_file)
    
    return jsonify({'chat':content})



@app.route('/refresh',methods=["GET"])
def refresh():
    chat_ids=list(state.get_keys())
    urls=[x.get("youtube_url") for x in state]
    titles=[x.get("title") for x in state]

    return jsonify({"chat_ids":chat_ids,"urls":urls,"titles":titles})
    
if __name__ == '__main__':
    app.run(port=5000, debug=True)