"""
Get n rows of random mysql data given the following structure

[
    {
    "name": "employees",
    "columns": [
            {'name': "employee_no", 'type': "CHAR", 'width': 4},
            {'name': "empoyee_name", 'type': "VARCHAR", 'width': 40},
        ]
    },

    {
    "name": "departments",
    "columns": [
            {'name': "dept_no", 'type': "CHAR", 'width': 4},
            {'name': "dept_name", 'type': "VARCHAR", 'width': 40},
        ]
    },
]

Return insert statements in correct SQL syntax:

INSERT INTO employees
(
employee_no, employee_name
)
VALUES
(
0002, "sdfjkewr ldfj"
);

"""


FILEPATH = '/tmp/statements.sql'


data_type_map = {

    "INT": {
        "return": '1',
        # "options": [
        #     ("M", 4),
        #     ("NOT NULL", False),
        #     ("AUTO_INCREMENT", False),
        # ]
    },

    "TINYINT": {
        "return": '0',
    },

    "DATETIME": {
        "return": '"2013-05-29 16:02:33"',
    },

    "LONGTEXT": {
        "return": '"longtext"',
    },

    "CHAR": {
        "return": '"char"',
    },

    "VARCHAR": {
        "return": '"varchar"',
    },
}


def generate_rows(table_list):
    statements = []
    for table in table_list:
        generate_rows(table)

    #     name = table['name']
    #     columns = []
    #     values = []

    #     for column in table['columns']:
    #         columns.append(column['name'])
    #         random_data = get_random_data(column['type'])
    #         values.append(random_data)

    #     statements.append(insert_statement(name, columns, values))

    # return write_statements_to_file(statements)


def generate_rows(table):
    statements = []
    for table in table_list:
        name = table['name']
        columns = []
        values = []

        for column in table['columns']:
            columns.append(column['name'])
            random_data = get_random_data(column['type'])
            values.append(random_data)

        statements.append(insert_statement(name, columns, values))

    return write_statements_to_file(statements)


def get_random_data(data_type):
    return data_type_map[data_type]['return']


def insert_statement(table_name, column_names, column_values):
    return 'INSERT INTO %s (%s) VALUES (%s);' % (table_name,
                                                 ', '.join(column_names),
                                                 ', '.join(column_values)
                                                 )


def write_statements_to_file(statements):
    with open(FILEPATH, 'w') as f:
        for statement in statements:
            f.write(statement + "\n\n")
    print statements


test_data = [
    {
        "name": "employees",
        "columns": [
            {'name': "employee_no", 'type': "CHAR", 'width': 4},
            {'name': "empoyee_name", 'type': "VARCHAR", 'width': 40},
        ]
    },
    {
        "name": "departments",
        "columns": [
            {'name': "dept_no", 'type': "CHAR", 'width': 4},
            {'name': "dept_name", 'type': "VARCHAR", 'width': 40},
        ]
    },
    {
        "name": "status",
        "columns": [
            {'name': "current", 'type': "TINYINT", 'width': 4},
            {'name': "start_date", 'type': "DATETIME", 'width': 40},
        ]
    },
]
