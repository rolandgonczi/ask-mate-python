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
    return connection.find_first_by_header(QUESTIONS_FILE_PATH, QUESTIONS_HEADER[0], id_)

def get_specific_answer(id_):
    return connection.find_first_by_header(ANSWERS_FILE_PATH, ANSWERS_HEADER[0], id_)



