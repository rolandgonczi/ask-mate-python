from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, session
import data_manager
import sys
import security

app = Flask(__name__)
UI_FILE_PATH = sys.path[0] + "/ui"

app.secret_key = b'r[_Drea+%!"edCElf>>,'


def need_login(post_type=None):
    def decorator(server_function):
        @wraps(server_function)
        def wrapper(*args, **kwargs):
            if session.get('user_id'):
                if (post_type == "question" and \
                        session['user_id'] == data_manager.get_user_id_for_question(kwargs["question_id"]))\
                        or (post_type == "answer" and\
                        session['user_id'] == data_manager.get_user_id_for_answer(kwargs["answer_id"]))\
                        or (post_type == "comment" and \
                        session['user_id'] == data_manager.get_user_id_for_comment(kwargs["comment_id"]))\
                        or post_type == "any":
                    valid = True
                else:
                    return render_template('invalid_user.html')
                if valid:
                    return server_function(*args, **kwargs)
            else:
                return redirect(url_for('login', next=request.url))
        return wrapper
    return decorator


@app.route('/')
def index():
    questions = data_manager.get_first_n_questions(5)
    return render_template("list.html", questions=questions,
                           headers=data_manager.QUESTIONS_HEADER,
                           nice_headers=data_manager.QUESTIONS_HEADER_NICE,
                           index_page=True,
                           page_title=" | Home Page",
                           current_user=data_manager.get_user_by_user_id(session.get('user_id')))


@app.route('/list/')
def list_messages():
    questions = data_manager.get_all_questions()
    header = request.args.get('header')
    reverse = request.args.get('reverse')
    if header is not None and reverse is not None:
        questions = data_manager.sort_data_by_header(questions, header, int(reverse))
    return render_template("list.html", questions=questions,
                           headers=data_manager.QUESTIONS_HEADER,
                           nice_headers=data_manager.QUESTIONS_HEADER_NICE,
                           page_title=" | Browse questions",
                           current_user=data_manager.get_user_by_user_id(session.get('user_id')))


@app.route('/question/<question_id>')
def show_question(question_id):
    question = data_manager.get_specific_question(question_id)
    answers = data_manager.get_all_answers_by_question_id(question_id)
    question_tags = data_manager.get_tags_for_question(question_id)
    question_comments = data_manager.get_comments_by_question_id(question_id)
    answer_comments = data_manager.get_answer_comments_for_answers(answers)
    usernames = data_manager.get_all_usernames_for_dictionaries(answers, question_comments, answer_comments, [question])
    current_user_id = session.get('user_id', None)
    return render_template("question.html",
                           question=question, answers=answers,
                           question_comments=question_comments,
                           answer_comments=answer_comments,
                           question_tags=question_tags,
                           user_id=current_user_id,
                           usernames=usernames,
                           page_title=" | Question | {}".format(question['title']),
                           current_user=data_manager.get_user_by_user_id(session.get('user_id')))


@app.route('/add-question/', methods=["GET", "POST"])
@need_login(post_type="any")
def ask_question():
    if request.method == "GET":
        return render_template("ask.html", page_title=" | Ask new question",
                               current_user=data_manager.get_user_by_user_id(session.get('user_id')))
    if request.method == "POST":
        data_manager.add_new_question(request.form, request.files, user_id=session['user_id'])
        return redirect(url_for('index'))


@app.route('/question/<question_id>/edit', methods=["GET", "POST"])
@need_login(post_type="question")
def edit_question(question_id):
    if request.method == "GET":
        question = data_manager.get_specific_question(question_id)
        return render_template("update_question.html", question=question,
                               page_title=" | Edit question: {}".format(question['title']),
                               current_user=data_manager.get_user_by_user_id(session.get('user_id')))
    if request.method == "POST":
        data_manager.update_question(request.form, question_id)
        return redirect(url_for('show_question', question_id=question_id))


@app.route('/answer/<answer_id>/edit', methods=["GET", "POST"])
@need_login(post_type="answer")
def edit_answer(answer_id):
    answer = data_manager.get_specific_answer(answer_id)
    if request.method == "GET":
        question_message = data_manager.get_question_for_answer_from_id(answer_id)["message"]
        return render_template("update_answer.html",
                               answer=answer,
                               question_message=question_message,
                               page_title=" | Edit answer",
                               current_user=data_manager.get_user_by_user_id(session.get('user_id')))
    if request.method == "POST":
        data_manager.update_answer(request.form, answer_id)
        return redirect(url_for('show_question', question_id=answer["question_id"]))


@app.route('/comment/<comment_id>/edit', methods=["GET", "POST"])
@need_login(post_type="comment")
def edit_comment(comment_id):
    comment = data_manager.get_specific_comment(comment_id)
    if request.method == "GET":
        return render_template("update_comment.html", comment=comment, page_title=" | Edit comment",
                               current_user=data_manager.get_user_by_user_id(session.get('user_id')))
    if request.method == "POST":
        for key in request.form:
            comment[key] = request.form[key]
        if comment["edited_count"] is None:
            comment["edited_count"] = 1
        else:
            comment["edited_count"] += 1
        data_manager.update_comment(comment)
        question_id = data_manager.get_question_id_for_comment(comment)
        return redirect(url_for('show_question', question_id=question_id))


@app.route('/question/<question_id>/new-answer/', methods=["GET", "POST"])
@need_login(post_type="any")
def new_answer(question_id):
    question = data_manager.get_specific_question(question_id)
    if session["user_id"] != question["user_id"]:
        if request.method == "GET":
            return render_template("new_answer.html", question=question,
                                   page_title=" | Add new answer to {}".format(question['title']),
                                   current_user=data_manager.get_user_by_user_id(session.get('user_id')))
        if request.method == "POST":
            data_manager.add_new_answer(request.form, request.files, question_id, session["user_id"])
            return redirect(url_for('show_question', question_id=question_id))
    else:
        return render_template('invalid_user.html')


@app.route('/question/<question_id>/new-comment/', methods=["GET", "POST"])
@need_login(post_type="any")
def new_comment_for_question(question_id):
    if request.method == "GET":
        question = data_manager.get_specific_question(question_id)
        return render_template("new_comment.html", question=question,
                               page_title=" | Add new comment to question {}".format(question['title']),
                               current_user=data_manager.get_user_by_user_id(session.get('user_id')))
    if request.method == "POST":
        data_manager.add_new_comment(request.form, session["user_id"], question_id=question_id)
        return redirect('/question/{}'.format(question_id))


@app.route('/answer/<int:answer_id>/new_comment/', methods=["GET", "POST"])
@need_login(post_type="any")
def new_comment_to_specific_answer(answer_id):
    question_id = data_manager.get_question_id_by_answer_id(answer_id)
    if request.method == "GET":
        answer = data_manager.get_specific_answer(answer_id)
        return render_template("new_comment_to_answer.html", answer=answer, page_title=' | Add new comment to answer',
                               current_user=data_manager.get_user_by_user_id(session.get('user_id')))
    if request.method == "POST":
        data_manager.add_new_comment(request.form, session["user_id"], answer_id=answer_id)
        return redirect(url_for('show_question', question_id=question_id))


@app.route("/comment/<int:comment_id>/delete", methods= ["GET", "POST"])
@need_login(post_type="comment")
def delete_comment(comment_id):
    comment = data_manager.get_specific_comment(comment_id)
    question_id = data_manager.get_question_id_for_comment(comment)
    if request.method == "GET":
        return render_template("confirm_delete.html", comment=comment, question_id=question_id,
                               page_title=' | Confirm comment deletion',
                               current_user=data_manager.get_user_by_user_id(session.get('user_id')))
    elif request.method == "POST":
        data_manager.delete_comment(comment_id)
        return redirect('/question/{}'.format(question_id))


@app.route("/question/<int:question_id>/delete")
@need_login(post_type="question")
def delete_question(question_id):
    data_manager.delete_question(question_id)
    return redirect("/list/")


@app.route("/answer/<int:answer_id>/delete")
@need_login(post_type="answer")
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
@need_login(post_type="any")
def question_vote_up(question_id):
    if not data_manager.vote_exists_for_question(question_id, session['user_id'])\
            and data_manager.get_user_id_for_question(question_id) != session['user_id']:
        data_manager.change_vote_number_for_question(question_id, 1)
        data_manager.add_vote_to_question_from_user(question_id, session['user_id'], True)
        data_manager.modify_reputation_for_user(session['user_id'], 5)
    return redirect(url_for('show_question', question_id=question_id))


@app.route('/question/<int:question_id>/vote-down/')
@need_login(post_type="any")
def question_vote_down(question_id):
    if not data_manager.vote_exists_for_question(question_id, session['user_id'])\
            and data_manager.get_user_id_for_question(question_id) != session['user_id']:
        data_manager.change_vote_number_for_question(question_id, -1)
        data_manager.add_vote_to_question_from_user(question_id, session['user_id'], False)
        data_manager.modify_reputation_for_user(session['user_id'], -2)
    return redirect(url_for('show_question', question_id=question_id))


@app.route('/answer/<int:answer_id>/vote-up/')
@need_login(post_type="any")
def answer_vote_up(answer_id):
    if not data_manager.vote_exists_for_answer(answer_id, session['user_id'])\
            and data_manager.get_user_id_for_answer(answer_id) != session['user_id']:
        data_manager.change_vote_number_for_answer(answer_id, 1)
        data_manager.add_vote_to_answer_from_user(answer_id, session['user_id'], True)
        data_manager.modify_reputation_for_user(session['user_id'], 10)
    question_id = data_manager.get_question_for_answer_from_id((answer_id))['id']
    return redirect(url_for('show_question', question_id=question_id))


@app.route('/answer/<int:answer_id>/vote-down/')
@need_login(post_type="any")
def answer_vote_down(answer_id):
    if not data_manager.vote_exists_for_answer(answer_id, session['user_id'])\
            and data_manager.get_user_id_for_answer(answer_id) != session['user_id']:
        data_manager.change_vote_number_for_answer(answer_id, -1)
        data_manager.add_vote_to_answer_from_user(answer_id, session['user_id'], False)
        data_manager.modify_reputation_for_user(session['user_id'], -2)
    question_id = data_manager.get_question_for_answer_from_id((answer_id))['id']
    return redirect(url_for('show_question', question_id=question_id))


@app.route('/search')
def search():
    search = request.args.get('search')
    search_results = data_manager.get_search_results(search)
    return render_template("search.html", questions=search_results,
                           headers=data_manager.QUESTIONS_HEADER,
                           nice_headers=data_manager.QUESTIONS_HEADER_NICE,
                           page_title=" | Search for: {}".format(search),
                           current_user=data_manager.get_user_by_user_id(session.get('user_id')))


@app.route('/question/<int:question_id>/new-tag', methods=['POST', 'GET'])
@need_login(post_type="question")
def new_tag_for_question(question_id):
    if request.method == 'GET':
        all_tags = data_manager.get_all_tags()
        tags_for_question = data_manager.get_tags_for_question(question_id)
        return render_template('new_tag.html',
                               all_tags=all_tags,
                               tags_for_question=tags_for_question,
                               question_id=question_id,
                               page_title=' | Add new tag',
                               current_user=data_manager.get_user_by_user_id(session.get('user_id')))
    elif request.method == 'POST':
        data_manager.add_tag_to_question(request.form, question_id)
        return redirect(url_for('show_question', question_id=question_id))


@app.route('/question/<int:question_id>/tag/<int:tag_id>/delete')
@need_login(post_type="question")
def delete_tag_from_question(question_id, tag_id):
    data_manager.delete_specific_tag_from_question(question_id, tag_id)
    return redirect(url_for('show_question', question_id=question_id))


@app.route('/answer/<int:question_id>/<int:answer_id>/accept')
@need_login(post_type="question")
def accept_answer(question_id, answer_id):
    if not data_manager.answer_accepted(answer_id):
        data_manager.set_answer_as_accepted(answer_id)
        data_manager.modify_reputation_for_user(session['user_id'], 15)
    return redirect(url_for('show_question', question_id=question_id))


@app.route('/login', methods= ['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', page_title=" | Login")
    if request.method == 'POST':
        if request.form['form'] == 'login':
            if security.verify_password(
                    request.form['password'],
                    data_manager.get_password_for_username(request.form['username'])):
                session["user_id"] = data_manager.get_user_by_username(request.form['username'])['id']
                return redirect(request.form.get('next'))
            else:
                return render_template('login.html', invalid=True, page_title=" | Login",
                                       current_user=data_manager.get_user_by_user_id(session.get('user_id')))
        if request.form['form'] == 'register':
            data_manager.save_new_user(request.form['username'], security.hash_password(request.form['password']))
            session["user_id"] = data_manager.get_user_by_username(request.form['username'])['id']

            return redirect(request.form.get('next'))


@app.route('/logout')
def logout():
    session.pop('user_id')
    return redirect(request.referrer)


@app.route('/list_users', methods= ['GET'])
def all_user_data():
    return render_template("list_users.html", users=data_manager.all_user_data(), page_title=" | Users",
                           current_user=data_manager.get_user_by_user_id(session.get('user_id')))


@app.route('/user/<int:user_id>')
def show_user(user_id):
    user = data_manager.get_user_by_user_id(user_id)
    user.pop("password")
    question = data_manager.get_all_question_by_user_id(user_id)
    answers = data_manager.get_all_answer_by_user_id(user_id)
    comments = data_manager.get_all_comment_by_user_id(user_id)
    return render_template("user_page.html",
                           questions=question,
                           answers=answers,
                           comments=comments,
                           user=user,
                           page_title=" | User Page | {}".format(user['username']),
                           current_user=data_manager.get_user_by_user_id(session.get('user_id'))
                           )


@app.route('/tags')
def tags():
    tags = data_manager.count_all_tags_in_questions()
    return render_template("tags.html", tags=tags, page_title=" | Tags",
                           current_user=data_manager.get_user_by_user_id(session.get('user_id')))


@app.route('/answer/<int:answer_id>')
def answer(answer_id):
    return redirect(url_for('show_question', question_id=data_manager.get_question_id_by_answer_id(answer_id)))


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=8000,
        debug=True,
    )
