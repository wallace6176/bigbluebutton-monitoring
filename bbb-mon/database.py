import json
import os
import sys
import psycopg2

from psycopg2._json import Json


def save_meetings(response):
    json_data = json.dumps(response)
    # json_data = json.dumps(views.get_meetings())
    meeting_record = json.loads(json_data)

    # create a nested list of the records' values
    values = [list(x.values()) for x in meeting_record]
    # value string for the SQL string
    values_str = ""

    # enumerate over the records' values
    for i, record in enumerate(values):

        # declare empty list for values
        val_list = []

        # append each value to a new list of values
        for v, val in enumerate(record):
            if type(val) == str:
                val = str(Json(val)).replace('"', '')
            elif type(val) == list:
                val = str(Json(val)).replace('[]', '')
            elif type(val) == dict:
                val = str(Json(val)).replace('{}', '')
            val_list += [str(val)]

        # put parenthesis around each record string
        values_str += "(" + ', '.join(val_list) + "),\n"

    # remove the last comma and end SQL with a semicolon
    values_str = values_str[:-2] + ";"

    table_name = "meetings"
    # sql_string = 'INSERT INTO {} '.format(table_name)
    sql_string = "INSERT INTO %s (name, id, creation, nousers, moderators, viewers, metadata) \nVALUES %s" % (
        table_name,
        values_str
    )

    try:
        # declare a new PostgreSQL connection object
        conn = psycopg2.connect(
            dbname=os.environ['dbname'],
            user=os.environ['dbuser'],
            host=os.environ['dbhost'],
            port=os.environ['port'],
            password=os.environ['dbpassword'],

            # attempt to connect for 10 seconds then raise exception
            connect_timeout=10
        )

        cur = conn.cursor()
        print("\ncreated cursor object:", cur)

    except (Exception, psycopg2.Error) as err:
        print("\npsycopg2 connect error:", err)
        conn = None
        cur = None

    # only attempt to execute SQL if cursor is valid
    if cur is not None:

        try:
            cur.execute(sql_string)
            conn.commit()

            print('\n***** INSERT complete *****')

        except (Exception, psycopg2.Error) as error:
            print("\nexecute_sql() error:", error)
            conn.rollback()

        # close the cursor and connection
        cur.close()
        conn.close()

    return ""
