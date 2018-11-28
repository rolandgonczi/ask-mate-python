import csv


def read_all(file_path):
    all_data = []
    with open(file_path) as data_base:
        csv_reader = csv.DictReader(data_base)
        for record in csv_reader:
            print(record)
            all_data.append(record)
    return all_data


def find_first_by_header(file_path, header, value):
    with open(file_path) as data_base:
        csv_reader = csv.DictReader(data_base)
        for record in csv_reader:
            if record[header] == value:
                return record


def find_all_by_header(file_path, header, value):
    all_by_header = []
    with open(file_path) as data_base:
        csv_reader = csv.DictReader(data_base)
        for record in csv_reader:
            if record[header] == value:
                all_by_header.append(record)
    return all_by_header


def save_record_into_file(file_path, record, headers):
    with open(file_path, "a") as f:
        csv_writer = csv.DictWriter(f, headers)
        csv_writer.writerow(record)

