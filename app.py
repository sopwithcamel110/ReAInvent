from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=['POST', 'GET'])
def index(chatbox = ""):
    if request.method == 'POST':
        url = request.form['linkInput']
        chatbox = url
    return render_template('index.html', chatbox=chatbox)