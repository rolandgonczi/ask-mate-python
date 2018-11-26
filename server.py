from flask import Flask, render_template, request, redirect, url_for
import data_manager

app = Flask(__name__)


@app.route('/')
def index():
    return redirect(url_for("list_messages"))


@app.route('/list/')
def list_messages():
    return "list_messages_here"

if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
