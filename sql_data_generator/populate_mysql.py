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
import sys

VISITING = 'VISITING'
FILEPATH = '/tmp/statements.sql'


data_type_map = {

    "bigint": {
        "return": '1',
    },
    "char": {
        "return": '"char"',
    },
    "CHARACTER": {
        "return": '"char"',
    },
    "date": {
        "return": '"2013-05-29 16:02:33"',
    },
    "datetime": {
        "return": '"2013-05-29 16:02:33"',
    },
    "decimal": {
        "return": '0.21345',
    },
    "double": {
        "return": '0.21345',
    },
    "int": {
        "return": '1',
    },
    "longtext": {
        "return": '"longtext"',
    },
    "smallint": {
        "return": '1',
    },
    "tinyint": {
        "return": '1',
    },
    "varchar": {
        "return": '"varchar"',
    },
}


class Tables(object):

    def __init__(self, table_list):
        self.table_dict = self.get_table_dict(table_list)

    def get_table_dict(self, table_list):
        table_dict = {}

        for table in table_list:
            name = table['name']
            table_dict[name] = table
            table['visited'] = False

        return table_dict

    def generate_rows_all_tables(self):
        tables = self.table_dict
        self.statements = []

        for table_name in tables:
            self.generate_rows(table_name)

        return self.write_statements_to_file(self.statements)

    def get_foreign_key_table_names(self, columns):
        foreign_key_tables = []
        for column in columns:
            if 'foreign_key_table' in column:
                foreign_key_tables.append(column['foreign_key_table'])
        return foreign_key_tables

    def generate_rows(self, table_name):
        table = self.table_dict[table_name]

        if table['visited'] is True:
            return []
        elif table['visited'] == VISITING:
            print >>sys.stderr, "Cycle detected involving table %s" % table_name
            return []
        else:
            table['visited'] = VISITING

        for foreign_key_table_name in self.get_foreign_key_table_names(table['columns']):
            self.generate_rows(foreign_key_table_name)

        columns = []
        values = []
        for column in table['columns']:
            columns.append(column['name'])
            random_data = self.get_random_data(column['type'])
            values.append(random_data)

        rows = [self.insert_statement(table_name, columns, values)]

        self.statements.extend(rows)

        table['visited'] = True


    def get_random_data(self, data_type):
        return data_type_map[data_type]['return']

    def insert_statement(self, table_name, column_names, column_values):
        return 'INSERT INTO %s (%s) VALUES (%s);' % (table_name,
                                                     ', '.join(column_names),
                                                     ', '.join(column_values)
                                                     )

    def write_statements_to_file(self, statements):
        with open(FILEPATH, 'w') as f:
            for statement in statements:
                f.write(statement + "\n\n")
                print statement


test_data = [
    {
        "name": "status",
        "columns": [
            {'name': "current", 'type': "TINYINT", 'type_arguments': 4},
            {'name': "start_date", 'type': "DATETIME", 'type_arguments': 40},
            {'name': "employee_id", 'type': "INT", 'type_arguments': 4,
             "foreign_key_table": "employees"},
        ]
    },
    {
        "name": "employees",
        "columns": [
            {'name': "id", 'type': "INT", 'type_arguments': 4},
            {'name': "empoyee_name", 'type': "VARCHAR", 'type_arguments': 40},
        ]
    },
    {
        "name": "schedule",
        "columns": [
            {'name': "dept_no", 'type': "CHAR", 'type_arguments': 4},
            {'name': "dept_name", 'type': "VARCHAR", 'type_arguments': 40},
            {'name': "employee_id", 'type': "INT", 'type_arguments': 4,
             "foreign_key_table": "employees"},
            {'name': "department_id", 'type': "INT", 'type_arguments': 4,
             "foreign_key_table": "departments"},
        ]
    },
    {
        "name": "departments",
        "columns": [
            {'name': "id", 'type': "CHAR", 'type_arguments': 4},
            {'name': "dept_name", 'type': "VARCHAR", 'type_arguments': 40},
            {'name': "employee_id", 'type': "INT", 'type_arguments': 4,
             "foreign_key_table": "employees"},
        ]
    },
]


if __name__ == '__main__':
    tables = Tables(schema)
    tables.generate_rows_all_tables()
