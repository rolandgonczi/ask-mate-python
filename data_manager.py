import os
import connection
import util
import sys
import time
from datetime import datetime

QUESTION_TABLE_NAME = "question"
ANSWER_TABLE_NAME = "answer"
COMMENTS_TABLE_NAME = "comment"
TAG_TABLE_NAME = "tag"
USER_TABLE_NAME = "users"
QUESTION_TAG_CONNECTION_TABLE = "question_tag"
USER_QUESTION_VOTE_TABLE_NAME = "user_question_vote"
USER_ANSWER_VOTE_TABLE_NAME = "user_answer_vote"
QUESTIONS_HEADER = ["id", "submission_time", "view_number", "vote_number", "title", "message", "image"]
ANSWERS_HEADER = ["id", "submission_time", "vote_number", "question_id", "message", "image"]
COMMENTS_HEADER = ["id", "question_id", "answer_id", "message", "submission_time", "edited_count"]
QUESTIONS_HEADER_NICE = {'id': "ID", "submission_time": "Submission time",
                         'view_number': "View number", 'vote_number': "Vote number",
                         'title': "Title", 'message': "Message", 'image': "Image"}
ANSWERS_HEADER_NICE = ["ID", "Submission time", "Vote number", "Question ID", "Message", "Image"]
IMAGE_DIRECTORY = sys.path[0] + "/images/"
IMAGE_DIRECTORY_RELATIVE = "images/"
ORDER_BY_DEFAULT = {"submission_time": "DESC"}


def get_all_questions():
    return connection.read_all(QUESTION_TABLE_NAME, ORDER_BY_DEFAULT)


def get_first_n_questions(n):
    return connection.read_first_n(QUESTION_TABLE_NAME, ORDER_BY_DEFAULT, n)


def get_all_answers():
    return connection.read_all(ANSWER_TABLE_NAME, ORDER_BY_DEFAULT)


def get_specific_question(question_id, with_username=False):
    question = connection.find_first_by_header(QUESTION_TABLE_NAME, "id", question_id)
    if with_username:
        question["username"] = get_username_by_user_id(question["user_id"])
    return question


def get_specific_answer(answer_id, with_username=False):
    answer = connection.find_first_by_header(ANSWER_TABLE_NAME, "id", answer_id)
    if with_username:
        answer["username"] = get_username_by_user_id(answer["user_id"])
    return answer


def get_specific_comment(comment_id, with_username=False):
    comment = connection.find_first_by_header(COMMENTS_TABLE_NAME, "id", comment_id)
    if with_username:
        comment["username"] = get_username_by_user_id(comment["user_id"])
    return comment


def get_all_answers_by_question_id(question_id):
    return connection.find_all_by_header(ANSWER_TABLE_NAME, ORDER_BY_DEFAULT, "question_id", question_id)


def get_comments_by_question_id(question_id):
    return connection.find_all_by_header(COMMENTS_TABLE_NAME, ORDER_BY_DEFAULT, "question_id", question_id)


def get_comments_by_answer_id(answer_id):
    return connection.find_all_by_header(COMMENTS_TABLE_NAME, ORDER_BY_DEFAULT, "answer_id", answer_id)


def get_question_id_by_answer_id(answer_id):
    return connection.get_column_with_key(ANSWER_TABLE_NAME, ('question_id',), 'id', answer_id)['question_id']


def save_new_question(question):
    connection.save_record_into_table(QUESTION_TABLE_NAME, question)


def save_new_comment(comment):
    connection.save_record_into_table(COMMENTS_TABLE_NAME, comment)


def save_new_answer(answer):
    connection.save_record_into_table(ANSWER_TABLE_NAME, answer)


def change_vote_number_for_question(question_id, amount):
    question = get_specific_question(question_id)
    question['vote_number'] = str(int(question['vote_number']) + amount)
    connection.update_record_in_database(QUESTION_TABLE_NAME, question, question_id, 'id')


def change_vote_number_for_answer(answer_id, amount):
    answer = get_specific_answer(answer_id)
    answer['vote_number'] = str(int(answer['vote_number']) + amount)
    connection.update_record_in_database(ANSWER_TABLE_NAME, answer, answer_id, 'id')


def delete_question(question_id):
    delete_tags_for_question(question_id)
    answers = get_all_answers_by_question_id(question_id)
    for answer in answers:
        delete_image_file(answer["image"])
        connection.delete_record_from_database(COMMENTS_TABLE_NAME, answer['id'], "answer_id")
    question = get_specific_question(question_id)
    connection.delete_record_from_database(COMMENTS_TABLE_NAME, question_id, "question_id")
    connection.delete_record_from_database(ANSWER_TABLE_NAME, question_id, "question_id")
    delete_image_file(question["image"])
    connection.delete_record_from_database(COMMENTS_TABLE_NAME, question_id, "question_id")
    connection.delete_record_from_database(QUESTION_TABLE_NAME, question_id, "id")


def get_question_for_answer_from_id(answer_id):
    answer = get_specific_answer(answer_id)
    return get_specific_question(answer['question_id'])


def update_question(new_question, question_id):
    connection.update_record_in_database(QUESTION_TABLE_NAME, new_question, question_id, "id")


def update_answer(new_answer, answer_id):
    connection.update_record_in_database(ANSWER_TABLE_NAME, new_answer, answer_id, "id")


def update_comment(comment):
    connection.update_record_in_database(COMMENTS_TABLE_NAME, comment, comment["id"], "id")


def delete_answer(answer_id):
    answer = get_specific_answer(answer_id)
    delete_image_file(answer["image"])
    connection.delete_record_from_database(COMMENTS_TABLE_NAME, answer_id, "answer_id")
    connection.delete_record_from_database(ANSWER_TABLE_NAME, answer_id, "id")
    return answer["question_id"]


def delete_comment(comment_id):
    connection.delete_record_from_database(COMMENTS_TABLE_NAME, comment_id, "id")


def sort_data_by_header(data, header, reverse):
    result = sorted(data, key=lambda x: x[header], reverse=reverse)
    return result


def save_question_image(file_, file_name):
    connection.save_file(file_, IMAGE_DIRECTORY, file_name, ("png", "jpg", "jpeg", "gif"))


def save_answer_image(file_, file_name):
    connection.save_file(file_, IMAGE_DIRECTORY, file_name, ("png", "jpg", "jpeg", "gif"))


def generate_question_image_file_name(file_):
    return "question_" + str(time.time()) + "." + util.get_file_extension(file_)


def generate_answer_image_file_name(file_):
    return "answer_" + str(time.time()) + "." + util.get_file_extension(file_)


def delete_image_file(image_path):
    if image_path:
        os.remove(sys.path[0] + "/images/" + image_path)


def get_question_ids_with_content_from_questions(content):
    look_in = ("title", "message")
    return_columns = ('id',)
    questions = connection.find_records_with_columns_like(QUESTION_TABLE_NAME, look_in, content, return_columns)
    return set(question['id'] for question in questions)


def get_question_ids_with_content_from_answers(content):
    look_in = ("message",)
    return_columns = ('question_id',)
    answers = connection.find_records_with_columns_like(ANSWER_TABLE_NAME, look_in, content, return_columns)
    return set(answer['question_id'] for answer in answers)


def get_question_ids_with_content(content):
    from_answers = get_question_ids_with_content_from_answers(content)
    from_questions = get_question_ids_with_content_from_questions(content)
    return from_answers | from_questions


def get_all_questions_with_ids(question_ids):
    return connection.find_all_by_header_multiple_values(QUESTION_TABLE_NAME, ORDER_BY_DEFAULT, 'id', question_ids)


def get_search_results(content):
    question_ids = get_question_ids_with_content(content)
    return get_all_questions_with_ids(question_ids)


def get_tags_for_question(question_id):
    question_tag = connection.find_all_by_header('question_tag', None, 'question_id', question_id)
    tag_ids = tuple(tag['tag_id'] for tag in question_tag)
    return connection.find_all_by_header_multiple_values(TAG_TABLE_NAME, None, 'id', tag_ids)


def get_all_tags():
    return connection.read_all(TAG_TABLE_NAME, None)


def save_new_tag(tag_name):
    if not tag_exists(tag_name):
        connection.save_record_into_table(TAG_TABLE_NAME, {'name': tag_name})


def get_tag_id_by_name(tag_name):
    return connection.find_first_by_header(TAG_TABLE_NAME, 'name', tag_name)["id"]


def tag_exists(tag_name):
    return bool(connection.find_first_by_header(TAG_TABLE_NAME, 'name', tag_name))


def question_has_tag(question_id, tag_id):
    criteria = {'question_id': question_id, 'tag_id': tag_id}
    return bool(connection.find_first_by_multiple_headers(QUESTION_TAG_CONNECTION_TABLE, criteria))


def save_new_tag_for_question(question_id, tag_id):
    if not question_has_tag(question_id, tag_id):
        question_tag = {'question_id': question_id, 'tag_id': tag_id}
        connection.save_record_into_table(QUESTION_TAG_CONNECTION_TABLE, question_tag)


def delete_tags_for_question(question_id):
    connection.delete_record_from_database(QUESTION_TAG_CONNECTION_TABLE, question_id, 'question_id')


def delete_specific_tag_from_question(question_id, tag_id):
    criteria = {'question_id': question_id, 'tag_id': tag_id}
    connection.delete_record_by_multiple_headers(QUESTION_TAG_CONNECTION_TABLE, criteria)
    if not any_question_has_tag_by_id(tag_id):
        print("should delete")
        connection.delete_record_from_database(TAG_TABLE_NAME, tag_id, 'id')


def any_question_has_tag_by_id(tag_id):
    print("checks if exists")
    print(bool(connection.find_first_by_header(QUESTION_TAG_CONNECTION_TABLE, 'tag_id', tag_id)))
    return bool(connection.find_first_by_header(QUESTION_TAG_CONNECTION_TABLE, 'tag_id', tag_id))


def get_answer_comments_for_answers(answers):
    comments = []
    for answer in answers:
        comments.extend(get_comments_by_answer_id(answer["id"]))
    return comments


def get_question_id_for_comment(comment):
    if comment["question_id"] is not None:
        question_id = comment["question_id"]
    else:
        answer_id = comment["answer_id"]
        answer = get_specific_answer(answer_id)
        question_id = answer["question_id"]
    return question_id



def add_new_question(form, files, user_id):
    question = {}
    for key in form:
        if key in QUESTIONS_HEADER:
            question[key] = form[key]
    question["submission_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    question["view_number"] = 0
    question["vote_number"] = 0
    question["user_id"] = user_id
    if files.get('image'):
        question["image"] = generate_question_image_file_name(files['image'])
        save_question_image(files['image'], question["image"])
    save_new_question(question)


def add_new_answer(form, files, question_id, user_id):
    answer = {}
    for key in form:
        if key in ANSWERS_HEADER:
            answer[key] = form[key]
    answer["question_id"] = question_id
    answer["submission_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    answer["vote_number"] = 0
    answer["user_id"] = user_id
    if files.get('image'):
        answer["image"] = generate_answer_image_file_name(files['image'])
        save_answer_image(files['image'], answer["image"])
    save_new_answer(answer)

def add_new_comment(form, user_id, question_id=None, answer_id=None):
    comment = {}
    for key in form:
        if key in COMMENTS_HEADER:
            comment[key] = form[key]
    comment["question_id"] = question_id
    comment["answer_id"] = answer_id
    comment["submission_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    comment["edited_count"] = 0
    comment["user_id"] = user_id
    save_new_comment(comment)


def add_tag_to_question(form, question_id):
    if form['new_tag']:
        save_new_tag(form['new_tag'])
        tag_id = get_tag_id_by_name(form['new_tag'])
    else:
        tag_id = form['existing_tag']
    save_new_tag_for_question(question_id, tag_id)


def get_password_for_username(username):
    user = get_user_by_username(username)
    if user:
        return user.get("password", False)
    else:
        return None


def save_new_user(username, password):
    connection.save_record_into_table(USER_TABLE_NAME, {"username": username, "password": password})


def get_user_by_username(username):
    return connection.find_first_by_header(USER_TABLE_NAME, "username", username)


def get_username_by_user_id(user_id):
    return connection.find_first_by_header(USER_TABLE_NAME, "id", user_id)["username"]


def get_user_id_for_question(question_id):
    return connection.find_first_by_header(QUESTION_TABLE_NAME, "id", question_id)['user_id']


def get_user_id_for_answer(answer_id):
    return connection.find_first_by_header(ANSWER_TABLE_NAME, "id", answer_id)['user_id']


def get_user_id_for_comment(comment_id):
    return connection.find_first_by_header(COMMENTS_TABLE_NAME, "id", comment_id)['user_id']

def all_user_data():
    user_data = connection.list_all_user_data()
    return user_data


def get_user_by_user_id(user_id):
    return connection.find_first_by_header(USER_TABLE_NAME, "id", user_id)


def get_all_question_by_user_id(user_id):
    return connection.find_all_by_header(QUESTION_TABLE_NAME, ORDER_BY_DEFAULT, "user_id", user_id)


def get_all_answer_by_user_id(user_id):
    return connection.find_all_by_header(ANSWER_TABLE_NAME, ORDER_BY_DEFAULT, "user_id", user_id)


def get_all_comment_by_user_id(user_id):
    return connection.find_all_by_header(COMMENTS_TABLE_NAME, ORDER_BY_DEFAULT, "user_id", user_id)


def set_answer_as_accepted(answer_id):
    connection.update_record_in_database(ANSWER_TABLE_NAME, {"accepted": True}, answer_id, "id")


def add_vote_to_question_from_user(question_id, user_id, vote=True):
    connection.save_record_into_table(USER_QUESTION_VOTE_TABLE_NAME, {"user_id": user_id, "question_id": question_id, "vote": vote})


def add_vote_to_answer_from_user(answer_id, user_id, vote=True):
    connection.save_record_into_table(USER_ANSWER_VOTE_TABLE_NAME, {"user_id": user_id, "answer_id": answer_id, "vote": vote})


def vote_exists_for_question(question_id, user_id):
    return connection.find_first_by_multiple_headers(USER_QUESTION_VOTE_TABLE_NAME, {'question_id': question_id, "user_id": user_id})


def vote_exists_for_answer(answer_id, user_id):
    return connection.find_first_by_multiple_headers(USER_ANSWER_VOTE_TABLE_NAME, {'answer_id': answer_id, "user_id": user_id})


def modify_reputation_for_user(user_id, value):
    reputation = connection.find_first_by_header(USER_TABLE_NAME, 'id', user_id)['reputation']
    connection.update_record_in_database(USER_TABLE_NAME, {'reputation': reputation + value}, user_id, 'id')


def answer_accepted(answer_id):
    return connection.find_first_by_header(ANSWER_TABLE_NAME, 'id', answer_id)['accepted']


def get_all_usernames_for_dictionaries(*args):
    user_ids = set()
    for _list in args:
        for dictionary in _list:
            user_ids.add(dictionary.get('user_id'))
    users = connection.find_all_by_header_multiple_values(USER_TABLE_NAME, {'id': 'ASC'}, 'id', user_ids)
    usernames = {}
    for user in users:
        usernames[user['id']] = user['username']
    return usernames


def count_all_tags_in_questions():
    return connection.count_header_from_joined_tables('tag', 'question_tag', 'id', 'tag_id', 'name')