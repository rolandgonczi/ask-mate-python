import os
import connection
import util
import sys
import time

QUESTION_TABLE_NAME = "question"
ANSWER_TABLE_NAME = "answer"
QUESTIONS_HEADER = ["id", "submission_time", "view_number", "vote_number", "title", "message", "image"]
ANSWERS_HEADER = ["id", "submission_time", "vote_number", "question_id", "message", "image"]
QUESTIONS_HEADER_NICE = {'id': "ID", "submission_time": "Submission time",
                         'view_number': "View number", 'vote_number': "Vote number",
                         'title': "Title", 'message': "Message", 'image': "Image"}
ANSWERS_HEADER_NICE = ["ID", "Submission time", "Vote number", "Question ID", "Message", "Image"]
IMAGE_DIRECTORY = sys.path[0] + "/images/"
IMAGE_DIRECTORY_RELATIVE = "images/"


def get_all_questions():
    return connection.read_all(QUESTION_TABLE_NAME)


def get_all_answers():
    return connection.read_all(ANSWER_TABLE_NAME)


def get_specific_question(id_):
    return connection.find_first_by_header(QUESTION_TABLE_NAME, "id", id_)


def get_specific_answer(id_):
    return connection.find_first_by_header(ANSWER_TABLE_NAME, "id", id_)


def get_all_answers_by_question_id(question_id):
    return connection.find_all_by_header(ANSWER_TABLE_NAME, "question_id", question_id)


def save_new_question(question):
    connection.save_record_into_table(QUESTION_TABLE_NAME, question)


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
    answers = get_all_answers_by_question_id(question_id)
    for answer in answers:
        delete_image_file(answer["image"])
    question = get_specific_question(question_id)
    connection.delete_record_from_database(ANSWER_TABLE_NAME, question_id, "question_id")
    delete_image_file(question["image"])
    connection.delete_record_from_database(QUESTION_TABLE_NAME, question_id, "id")


def get_question_for_answer_from_id(answer_id):
    answer = get_specific_answer(answer_id)
    return get_specific_question(answer['question_id'])


def update_question(question):
    connection.update_record_in_database(QUESTION_TABLE_NAME, question, question["id"], "id")


def delete_answer(answer_id):
    connection.delete_record_from_database(ANSWER_TABLE_NAME, answer_id, "id")


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
    questions = connection.find_records_with_columns_like('question', look_in, content, return_columns)
    return set(question['id'] for question in questions)


def get_question_ids_with_content_from_answers(content):
    look_in = ("message",)
    return_columns = ('question_id',)
    answers = connection.find_records_with_columns_like('answer', look_in, content, return_columns)
    return set(answer['question_id'] for answer in answers)


def get_question_ids_with_content(content):
    from_answers = get_question_ids_with_content_from_answers(content)
    from_questions = get_question_ids_with_content_from_questions(content)
    return from_answers | from_questions


def get_all_questions_with_ids(question_ids):
    return connection.find_all_by_header_multiple('question', 'id', question_ids)


def get_search_results(content):
    question_ids = get_question_ids_with_content(content)
    return get_all_questions_with_ids(question_ids)