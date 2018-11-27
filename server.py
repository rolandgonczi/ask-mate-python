from flask import Flask, render_template, request, redirect, url_for
import data_manager
import time

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


@app.route('/question/<question_id>')
def show_question(question_id):
    question = data_manager.get_specific_question(question_id)
    answers = data_manager.get_all_answers_by_question_id(question_id)
    return render_template("question.html", question=question, answers=answers)


@app.route('/add-question/', methods=["GET", "POST"])
def ask_question():
    if request.method == "GET":
        return render_template("ask.html")
    if request.method == "POST":
        question = {}
        for key in request.form:
            if key in data_manager.QUESTIONS_HEADER:
                question[key] = request.form[key]
        question["submission_time"] = int(time.time())
        question["view_number"] = 0
        question["vote_number"] = 0
        question["id"] = data_manager.calculate_new_id(data_manager.get_all_questions())
        data_manager.save_new_question(question)
        return redirect('/')


@app.route('/question/<question_id>/new-answer')
def new_answer():
    return none


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
