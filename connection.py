import csv


def read_all(file_path):
    all_data = []
    with open(file_path) as data_base:
        csv_reader = csv.DictReader(data_base)
        for record in csv_reader:
            all_data.append(record)
    return all_data


def find_first_by_header(file_path, header, value):
    with open(file_path) as data_base:
        csv_reader = csv.DictReader(data_base)
        for record in csv_reader:
            if record[header] == value:
                return record
