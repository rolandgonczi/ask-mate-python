import os
import connection
import util
import sys
import time

QUESTIONS_FILE_PATH = os.getenv('QUESTIONS_FILE_PATH') if 'QUESTIONS_FILE_PATH' in os.environ else 'sample_data/question.csv'
ANSWERS_FILE_PATH = os.getenv('ANSWERS_FILE_PATH') if 'ANSWERS_FILE_PATH' in os.environ else 'sample_data/answer.csv'
QUESTIONS_HEADER = ["id", "submission_time", "view_number", "vote_number", "title", "message", "image"]
ANSWERS_HEADER = ["id", "submission_time", "vote_number", "question_id", "message", "image"]
QUESTIONS_HEADER_NICE = {'id': "ID", "submission_time": "Submission time",
                         'view_number': "View number", 'vote_number': "Vote number",
                         'title': "Title", 'message': "Message", 'image': "Image"}
ANSWERS_HEADER_NICE = ["ID", "Submission time", "Vote number", "Question ID", "Message", "Image"]
IMAGE_DIRECTORY = sys.path[0] + "/images/"
IMAGE_DIRECTORY_RELATIVE = "images/"


def get_all_questions():
    return connection.read_all(QUESTIONS_FILE_PATH)


def get_all_answers():
    return connection.read_all(ANSWERS_FILE_PATH)


def get_specific_question(id_):
    return connection.find_first_by_header(QUESTIONS_FILE_PATH, "id", id_)


def get_specific_answer(id_):
    return connection.find_first_by_header(ANSWERS_FILE_PATH, ANSWERS_HEADER[0], id_)


def get_all_answers_by_question_id(question_id):
    return connection.find_all_by_header(ANSWERS_FILE_PATH, "question_id", question_id)


def calculate_new_id(data):
    list_of_data = data
    new_id_number = 0
    for keys in list_of_data:
        if int(keys["id"]) > new_id_number:
            new_id_number = int(keys["id"])
        new_id_number += 1
    return new_id_number


def save_new_question(question):
    connection.save_record_into_file(QUESTIONS_FILE_PATH, question, QUESTIONS_HEADER)


def save_new_answer(answer):
    connection.save_record_into_file(ANSWERS_FILE_PATH, answer, ANSWERS_HEADER)


def change_vote_number_for_question(question_id, amount):
    question = get_specific_question(question_id)
    question['vote_number'] = str(int(question['vote_number']) + amount)
    connection.update_record_in_file(QUESTIONS_FILE_PATH, QUESTIONS_HEADER, question, question_id, 'id')


def change_vote_number_for_answer(answer_id, amount):
    answer = get_specific_answer(answer_id)
    answer['vote_number'] = str(int(answer['vote_number']) + amount)
    connection.update_record_in_file(ANSWERS_FILE_PATH, ANSWERS_HEADER, answer, answer_id, 'id')


def delete_question(id_):
    questions = connection.read_all(QUESTIONS_FILE_PATH)
    answers = connection.read_all(ANSWERS_FILE_PATH)
    for answer in get_all_answers_by_question_id(id_):
        delete_image_file(answer["image"])
        answers.remove(answer)
    question = get_specific_question(id_)
    delete_image_file(question["image"])
    questions.remove(question)
    connection.re_write_file(QUESTIONS_FILE_PATH, questions, QUESTIONS_HEADER)
    connection.re_write_file(ANSWERS_FILE_PATH, answers, ANSWERS_HEADER)


def get_question_for_answer_from_id(answer_id):
    answer = get_specific_answer(answer_id)
    return get_specific_question(answer['question_id'])


def update_question(question):
    connection.update_record_in_file(QUESTIONS_FILE_PATH, QUESTIONS_HEADER, question, question["id"], "id")


def delete_answer(answer_id):
    answers = get_all_answers()
    answers.remove(get_specific_answer(answer_id))
    connection.re_write_file(ANSWERS_FILE_PATH, answers, ANSWERS_HEADER)


def sort_data_by_header(data, header, reverse):
    result = sorted(data, key=lambda x: int(x[header]) if x[header].isdigit() else x[header], reverse=reverse)
    return result


def save_question_image(file_, question_id):
    file_name = "question_" + question_id + "." + util.get_file_extension(file_)
    connection.save_file(file_, IMAGE_DIRECTORY, file_name, ("png", "jpg", "jpeg", "gif"))


def save_answer_image(file_, answer_id):
    file_name = "answer_" + answer_id + "." + util.get_file_extension(file_)
    connection.save_file(file_, IMAGE_DIRECTORY, file_name, ("png", "jpg", "jpeg", "gif"))


def generate_question_image_file_name(file_, question_id, absolute=True):
    image_directory = IMAGE_DIRECTORY if absolute else IMAGE_DIRECTORY_RELATIVE
    return image_directory + "question_" + question_id + "." + util.get_file_extension(file_)


def generate_answer_image_file_name(file_, answer_id, absolute=True):
    image_directory = IMAGE_DIRECTORY if absolute else IMAGE_DIRECTORY_RELATIVE
    return image_directory + "answer_" + answer_id + "." + util.get_file_extension(file_)


def delete_image_file(image_path):
    os.remove(sys.path[0] + "/" + image_path)


def convert_time_in_data_to_human_readable(data, format_="%Y.%m.%d %H:%M:%S"):
    if type(data) in (set, tuple, list):
        for record in data:
            record["submission_time"] = time.strftime(format_, time.localtime(int(record["submission_time"])))
    else:
        data["submission_time"] = time.strftime(format_, time.localtime(int(data["submission_time"])))
