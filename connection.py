import csv
import util
import database_common
from psycopg2 import sql

SQL_IDENTIFIER = sql.Identifier
SQL_LITERAL = sql.Literal


@database_common.connection_handler
def read_all(cursor, table_name, order_by):
    order_by = sql_from_dictionary_with_operator(order_by, ' ', ', ')
    cursor.execute(sql.SQL("""
                                SELECT * FROM {table_name}
                                ORDER BY {order_by}
                            """).format(table_name=sql.Identifier(table_name),
                                        order_by=order_by)
                   )
    return cursor.fetchall()


@database_common.connection_handler
def read_first_n(cursor, table_name, order_by, n):
    order_by = sql_from_dictionary_with_operator(order_by, ' ', ', ')
    cursor.execute(sql.SQL("""
                                SELECT * FROM {table_name}
                                ORDER BY {order_by}
                                LIMIT {n}
                            """).format(table_name=sql.Identifier(table_name),
                                        order_by=order_by,
                                        n=sql.Literal(n))
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
def find_all_by_header(cursor, table_name, order_by, header, value):
    order_by = sql_from_dictionary_with_operator(order_by, ' ', ', ')
    cursor.execute(sql.SQL("""
                                SELECT * FROM {table_name}
                                WHERE {header} = {value}
                                ORDER BY {order_by}
                            """).format(table_name=sql.Identifier(table_name),
                                        order_by=order_by,
                                        header=sql.Identifier(header),
                                        value=sql.Literal(value))
                   )
    return cursor.fetchall()


@database_common.connection_handler
def find_all_by_header_multiple(cursor, table_name, order_by, header, values):
    if values:
        order_by = sql_from_dictionary_with_operator(order_by, ' ', ', ')
        cursor.execute(sql.SQL("""
                                    SELECT * FROM {table_name}
                                    WHERE {header} IN ({values})
                                    ORDER BY {order_by}
                                """).format(table_name=sql.Identifier(table_name),
                                            order_by=order_by,
                                            header=sql.Identifier(header),
                                            values=sql_from_list(values, type=SQL_LITERAL))
                       )
        return cursor.fetchall()
    else:
        return []


@database_common.connection_handler
def save_record_into_table(cursor, table_name, record):
    print("NEW RECORD:", record)
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
    print(new_record)
    criteria = sql.SQL("=").join([sql.Identifier(record_id_header), sql.Literal(record_id)])
    print(sql_from_dictionary(new_record))
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
    print(criteria)
    cursor.execute(sql.SQL("""
                            DELETE FROM {table_name}
                            WHERE {criteria}
                            """).format(table_name=sql.Identifier(table_name),
                                        criteria=criteria)
                   )



def save_file(file_, file_directory, file_name, acceptable_types):
    if util.get_file_extension(file_) not in acceptable_types:
        raise TypeError("Not acceptable file type. Acceptable types are:", ", ".join(acceptable_types))
    file_.save(file_directory + file_name)


def sql_from_dictionary(dictionary, join_pairs="=", join_items=", "):
    sql_output = []
    for key, value in dictionary.items():
        sql_output.append(sql.SQL(join_pairs).join([sql.Identifier(key), sql.Literal(value)]))
    return sql.SQL(join_items).join(sql_output)


def sql_from_dictionary_with_operator(dictionary, join_pairs="=", join_items=", "):
    sql_output = []
    for key, value in dictionary.items():
        sql_output.append(sql.SQL(join_pairs).join([sql.Identifier(key), sql.SQL(value)]))
    return sql.SQL(join_items).join(sql_output)


def sql_from_list_and_single(list, single, join_pairs="=", join_items=", "):
    sql_output = []
    for element in list:
        sql_output.append(sql.SQL(join_pairs).join([sql.Identifier(element), sql.Literal(single)]))
    return sql.SQL(join_items).join(sql_output)


def sql_from_single_and_list(single, list, join_pairs="=", join_items=", "):
    sql_output = []
    for element in list:
        sql_output.append(sql.SQL(join_pairs).join([sql.Identifier(single), sql.Literal(element)]))
    return sql.SQL(join_items).join(sql_output)


def sql_from_list(list, join_by=', ', type=SQL_IDENTIFIER):
    sql_output = []
    for element in list:
        sql_output.append(type(element))
    return sql.SQL(join_by).join(sql_output)


@database_common.connection_handler
def find_records_with_columns_like(cursor, table_name, columns, string, columns_to_return=('*')):
    criteria = sql_from_list_and_single(columns, '%' + string + '%', ' LIKE ', ' OR ')
    columns_to_return = sql_from_list(columns_to_return)
    cursor.execute(sql.SQL("""
                            SELECT {columns_to_return} FROM {table_name}
                            WHERE {criteria}
                            """).format(table_name=sql.Identifier(table_name),
                                        criteria=criteria,
                                        columns_to_return=columns_to_return)
                   )
    return cursor.fetchall()
