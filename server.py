from flask import Flask, render_template, request, redirect, url_for
import data_manager

app = Flask(__name__)


@app.route('/')
def index():
    return redirect(url_for("list_messages"))


@app.route('/list/')
def list_messages():
    questions = data_manager.get_all_questions()
    return render_template("list.html", questions=questions,
                           headers=data_manager.QUESTIONS_HEADER,
                           nice_headers=data_manager.QUESTIONS_HEADER_NICE)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
