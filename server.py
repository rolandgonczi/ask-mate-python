from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import data_manager
import time
import sys
from datetime import datetime

app = Flask(__name__)
UI_FILE_PATH = sys.path[0] + "/ui"


@app.route('/')
def index():
    questions = data_manager.get_first_n_questions(5)
    return render_template("list.html", questions=questions,
                           headers=data_manager.QUESTIONS_HEADER,
                           nice_headers=data_manager.QUESTIONS_HEADER_NICE,
                           index_page=True)


@app.route('/list/')
def list_messages():
    questions = data_manager.get_all_questions()
    header = request.args.get('header')
    reverse = request.args.get('reverse')
    if header is not None and reverse is not None:
        questions = data_manager.sort_data_by_header(questions, header, int(reverse))
    return render_template("list.html", questions=questions,
                           headers=data_manager.QUESTIONS_HEADER,
                           nice_headers=data_manager.QUESTIONS_HEADER_NICE)


@app.route('/question/<question_id>')
def show_question(question_id):
    question = data_manager.get_specific_question(question_id)
    answers = data_manager.get_all_answers_by_question_id(question_id)
    question_tags = data_manager.get_tags_for_question(question_id)
    question_comments = data_manager.get_comments_by_question_id(question_id)
    answer_comments = data_manager.get_answer_comments_for_answers(answers)
    return render_template("question.html",
                           question=question, answers=answers,
                           question_comments=question_comments,
                           answer_comments=answer_comments,
                           question_tags=question_tags)


@app.route('/add-question/', methods=["GET", "POST"])
def ask_question():
    if request.method == "GET":
        return render_template("ask.html")
    if request.method == "POST":
        data_manager.add_new_question(request.form, request.files)
        return redirect(url_for('index'))


@app.route('/question/<question_id>/edit', methods=["GET", "POST"])
def edit_question(question_id):
    question = data_manager.get_specific_question(question_id)
    if request.method == "GET":
        return render_template("update_question.html", question=question)
    if request.method == "POST":
        new_question = request.form
        for key in new_question:
            question[key] = new_question[key]
        data_manager.update_question(question)
        return redirect(url_for('show_question', question_id=question_id))


@app.route('/answer/<answer_id>/edit', methods=["GET", "POST"])
def edit_answer(answer_id):
    answer = data_manager.get_specific_answer(answer_id)
    if request.method == "GET":
        return render_template("update_answer.html", answer=answer)
    if request.method == "POST":
        new_answer = request.form
        for key in new_answer:
            answer[key] = new_answer[key]
        data_manager.update_answer(answer)
        return redirect(url_for('show_question', question_id=answer["question_id"]))


@app.route('/comment/<comment_id>/edit', methods=["GET", "POST"])
def edit_comment(comment_id):
    comment = data_manager.get_specific_comment(comment_id)
    if request.method == "GET":
        return render_template("update_comment.html", comment=comment)
    if request.method == "POST":
        new_comment = request.form
        for key in new_comment:
            comment[key] = new_comment[key]
        if comment["edited_count"] == None:
            comment["edited_count"] = 1
        else:
            comment["edited_count"] += 1
        print(comment["edited_count"])
        data_manager.update_comment(comment)
        question_id = data_manager.get_question_id_for_comment(comment)
        return redirect(url_for('show_question', question_id=question_id))


@app.route('/question/<question_id>/new-answer/', methods=["GET", "POST"])
def new_answer(question_id):
    if request.method == "GET":
        question = data_manager.get_specific_question(question_id)
        return render_template("new_answer.html", question=question)
    if request.method == "POST":
        data_manager.add_new_answer(request.form, request.files, question_id)
        return redirect(url_for('show_question', question_id=question_id))


@app.route('/question/<question_id>/new-comment/', methods=["GET", "POST"])
def new_comment_for_question(question_id):
    if request.method == "GET":
        question = data_manager.get_specific_question(question_id)
        answer = data_manager.get_specific_answer(answer_id)
        return render_template("new_comment.html", question=question, answer=answer)
    if request.method == "POST":
        data_manager.add_new_comment(request.form, question_id=question_id)
        return redirect('/question/{}'.format(question_id))


@app.route('/answer/<int:answer_id>/new_comment/', methods=["GET", "POST"])
def new_comment_to_specific_answer(answer_id):
    question_id = data_manager.get_question_id_by_answer_id(answer_id)
    if request.method == "GET":
        answer = data_manager.get_specific_answer(answer_id)
        return render_template("new_comment_to_answer.html", answer=answer)
    if request.method == "POST":
        data_manager.add_new_comment(request.form, answer_id=answer_id)
        return redirect(url_for('show_question', question_id=question_id))


@app.route("/comment/<int:comment_id>/delete")
def delete_comment(comment_id):
    comment = data_manager.get_specific_comment(comment_id)
    question_id = data_manager.get_question_id_for_comment(comment)
    data_manager.delete_comment(comment_id)
    return redirect('/question/{}'.format(question_id))


@app.route("/question/<int:question_id>/delete")
def delete_question(question_id):
    data_manager.delete_question(question_id)
    return redirect("/list/")


@app.route("/answer/<int:answer_id>/delete")
def delete_answer(answer_id):
    question_id = data_manager.delete_answer(answer_id)
    return redirect(url_for('show_question', question_id=question_id))


@app.route('/ui/<image_title>')
def ui_image(image_title):
    return send_from_directory(UI_FILE_PATH, image_title)


@app.route('/images/<image_title>')
def images(image_title):
    return send_from_directory(data_manager.IMAGE_DIRECTORY, image_title)


@app.route('/question/<int:question_id>/vote-up/')
def question_vote_up(question_id):
    data_manager.change_vote_number_for_question(question_id, 1)
    return redirect(url_for('show_question', question_id=question_id))


@app.route('/question/<int:question_id>/vote-down/')
def question_vote_down(question_id):
    data_manager.change_vote_number_for_question(question_id, -1)
    return redirect(url_for('show_question', question_id=question_id))


@app.route('/answer/<int:answer_id>/vote-up/')
def answer_vote_up(answer_id):
    data_manager.change_vote_number_for_answer(answer_id, 1)
    question_id = data_manager.get_question_for_answer_from_id((answer_id))['id']
    return redirect(url_for('show_question', question_id=question_id))


@app.route('/answer/<int:answer_id>/vote-down/')
def answer_vote_down(answer_id):
    data_manager.change_vote_number_for_answer(answer_id, -1)
    question_id = data_manager.get_question_for_answer_from_id((answer_id))['id']
    return redirect(url_for('show_question', question_id=question_id))


@app.route('/search')
def search():
    search = request.args.get('search')
    search_results = data_manager.get_search_results(search)
    return render_template("search.html", questions=search_results,
                           headers=data_manager.QUESTIONS_HEADER,
                           nice_headers=data_manager.QUESTIONS_HEADER_NICE)


@app.route('/question/<int:question_id>/new-tag', methods=['POST', 'GET'])
def new_tag_for_question(question_id):
    if request.method == 'GET':
        all_tags = data_manager.get_all_tags()
        tags_for_question = data_manager.get_tags_for_question(question_id)
        return render_template('new_tag.html',
                               all_tags=all_tags,
                               tags_for_question=tags_for_question,
                               question_id=question_id)
    elif request.method == 'POST':
        data_manager.add_tag_to_question(request.form, question_id)
        return redirect(url_for('show_question', question_id=question_id))


@app.route('/question/<int:question_id>/tag/<int:tag_id>/delete')
def delete_tag_from_question(question_id, tag_id):
    data_manager.delete_specific_tag_from_question(question_id, tag_id)
    return redirect(url_for('show_question', question_id=question_id))



if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
