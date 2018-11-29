import csv
import util


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


def update_record_in_file(file_path, headers, new_record, record_id, record_id_header):
    file_contents = read_all(file_path)
    with open(file_path, "w") as f:
        csv_writer = csv.DictWriter(f, headers)
        csv_writer.writeheader()
        for record in file_contents:
            if record[record_id_header] == record_id:
                csv_writer.writerow(new_record)
            else:
                csv_writer.writerow(record)


def re_write_file(file_path, data, headers):
    with open(file_path, "w") as f:
        csv_writer = csv.DictWriter(f, headers)
        csv_writer.writeheader()
        csv_writer.writerows(data)


def save_file(file_, file_directory, file_name, acceptable_types):
    if util.get_file_extension(file_) not in acceptable_types:
        raise TypeError("Not acceptable file type. Acceptable types are:", ", ".join(acceptable_types))
    file_.save(file_directory + file_name)
