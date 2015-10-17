from sqlparse import parse
from sqlparse import sql
from sqlparse import tokens


def generate_data(text):
    statements = parse(text)
    for create_table_stmnt in get_create_table_statements(statements):
        table_name = create_table_stmnt.get_name()
        columns = get_columns(create_table_stmnt)
        print table_name
        for column in columns:
            print '\t', column


def get_columns(create_table_stmnt):
    has_foreign_key = False
    columns = []
    for column in _get_columns(create_table_stmnt):
        columns.append(column)
    return columns


def _get_columns(create_table_stmnt):
    for tok1 in create_table_stmnt.tokens:
        if isinstance(tok1, sql.Function):
            for tok2 in tok1.tokens:
                if isinstance(tok2, sql.Parenthesis):
                    for tok3 in tok2.tokens:
                        if isinstance(tok3, sql.Identifier):
                            yield tok3
                        elif isinstance(tok3, sql.IdentifierList):
                            for tok4 in tok3.tokens:
                                if isinstance(tok4, sql.Identifier):
                                    yield tok4


def get_create_table_statements(statements):
    for stmnt in statements:
        if str(stmnt).strip().startswith('CREATE TABLE'):
            yield stmnt


def is_foreign_key_info(token):
    return token.value == 'FOREIGN'


if __name__ == '__main__':
    import sys
    [path] = sys.argv[1:]
    with open(path) as fp:
        generate_data(fp.read())
