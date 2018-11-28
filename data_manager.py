import os
import connection

QUESTIONS_FILE_PATH = os.getenv('QUESTIONS_FILE_PATH') if 'QUESTIONS_FILE_PATH' in os.environ else 'sample_data/question.csv'
ANSWERS_FILE_PATH = os.getenv('ANSWERS_FILE_PATH') if 'ANSWERS_FILE_PATH' in os.environ else 'sample_data/answer.csv'
QUESTIONS_HEADER = ["id", "submission_time", "view_number", "vote_number", "title", "message", "image"]
ANSWERS_HEADER = ["id", "submission_time", "vote_number", "question_id", "message", "image"]
QUESTIONS_HEADER_NICE = ["ID", "Submission time", "View number", "Vote number", "Title", "Message", "Image"]
ANSWERS_HEADER_NICE = ["ID", "Submission time", "Vote number", "Question ID", "Message", "Image"]


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


def delete_question(id_):
    questions = connection.read_all(QUESTIONS_FILE_PATH)
    answers = connection.read_all(ANSWERS_FILE_PATH)
    for answer in get_all_answers_by_question_id(id_):
        answers.remove(answer)
    questions.remove(get_specific_question(id_))
    connection.re_write_file(QUESTIONS_FILE_PATH, questions, QUESTIONS_HEADER)
    connection.re_write_file(ANSWERS_FILE_PATH, answers, ANSWERS_HEADER)


