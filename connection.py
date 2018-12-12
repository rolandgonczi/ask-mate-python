import csv
import util
import database_common
from psycopg2 import sql


@database_common.connection_handler
def read_all(cursor, table_name):
    cursor.execute(sql.SQL("""
                                SELECT * FROM {table_name}
                            """).format(table_name=sql.Identifier(table_name))
                   )
    return cursor.fetchall()


@database_common.connection_handler
def find_first_by_header(cursor, table_name, header, value):
    cursor.execute(sql.SQL("""
                                SELECT * FROM {table_name}
                                WHERE {header} = {value}
                            """).format(table_name=sql.Identifier(table_name),
                                        header=sql.Identifier(header),
                                        value=sql.Literal(value))
                   )
    return cursor.fetchone()


@database_common.connection_handler
def find_all_by_header(cursor, table_name, header, value):
    cursor.execute(sql.SQL("""
                                SELECT * FROM {table_name}
                                WHERE {header} = {value}
                            """).format(table_name=sql.Identifier(table_name),
                                        header=sql.Identifier(header),
                                        value=sql.Literal(value))
                   )
    return cursor.fetchall()


@database_common.connection_handler
def save_record_into_table(cursor, table_name, record):
    keys = []
    values = []
    for key, value in record.items():
        keys.append(sql.Identifier(key))
        values.append(sql.Literal(value))
    cursor.execute(sql.SQL("""
                                INSERT INTO {table_name} ({keys})
                                VALUES ({values})
                            """).format(table_name=sql.Identifier(table_name),
                                        keys=sql.SQL(", ").join(keys),
                                        values=sql.SQL(", ").join(values))
                   )


@database_common.connection_handler
def update_record_in_database(cursor, table_name, new_record, record_id, record_id_header):
    criteria = sql.SQL("=").join([sql.Identifier(record_id_header), sql.Literal(record_id)])
    cursor.execute(sql.SQL("""
                            UPDATE {table_name}
                            SET {new_record}
                            WHERE {criteria}
                            """).format(
                                        table_name=sql.Identifier(table_name),
                                        new_record=sql_from_dictionary(new_record),
                                        criteria=criteria
    ))


@database_common.connection_handler
def delete_record_from_database(cursor, table_name, record_id, record_id_header):
    criteria = sql.SQL("=").join([sql.Identifier(record_id_header), sql.Literal(record_id)])
    cursor.execute(sql.SQL("""
                            DELETE FROM {table_name}
                            WHERE {criteria}
                            """).format(table_name=sql.Identifier(table_name),
                                        criteria=criteria)
                   )


@database_common.connection_handler
def get_question_id_from_answer(cursor, table_name, header, value):
    cursor.execute(sql.SQL("""
                                SELECT question_id FROM {table_name}
                                WHERE {header} = {value}
                            """).format(table_name=sql.Identifier(table_name),
                                        header=sql.Identifier(header),
                                        value=sql.Literal(value))
                   )
    return cursor.fetchone()


@database_common.connection_handler
def get_answer_ids_from_question(cursor, table_name, header, value):
    cursor.execute(sql.SQL("""
                                SELECT answer_id FROM {table_name}
                                WHERE {header} = {value}
                            """).format(table_name=sql.Identifier(table_name),
                                        header=sql.Identifier(header),
                                        value=sql.Literal(value))
                   )
    return cursor.fetchall()


def save_file(file_, file_directory, file_name, acceptable_types):
    if util.get_file_extension(file_) not in acceptable_types:
        raise TypeError("Not acceptable file type. Acceptable types are:", ", ".join(acceptable_types))
    file_.save(file_directory + file_name)


def sql_from_dictionary(dictionary, join_pairs="=", join_items=", "):
    sql_output = []
    for key, value in dictionary.items():
        sql_output.append(sql.SQL(join_pairs).join([sql.Identifier(key), sql.Literal(value)]))
    return sql.SQL(join_items).join(sql_output)
