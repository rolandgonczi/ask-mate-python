import csv

def read_all(file_path, header_list):
    all_data = []
    with open(file_path) as data_base:
        csv_reader = csv.reader(data_base)
        for record in csv_reader:
            if len(record) > len(header_list):
                raise IndexError("Header length and record lengths do not match.")
            record_as_dictionary = {}
            for index, item in enumerate(record):
                try:
                    item = int(item)
                except ValueError:
                    try:
                        item = float(item)
                    except ValueError:
                        pass
                record_as_dictionary[header_list[index]] = item
            all_data.append(record_as_dictionary)
    return all_data