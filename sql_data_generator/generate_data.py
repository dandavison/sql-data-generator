from sqlparse import parse
from sqlparse import sql


def generate_data(text):
    statements = parse(text)
    for create_table_stmnt in get_create_table_statements(statements):
        print create_table_stmnt.get_name()
        for column in get_columns(create_table_stmnt):
            print "\t", column


def get_columns(create_table_stmnt):
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


if __name__ == '__main__':
    import sys
    [path] = sys.argv[1:]
    with open(path) as fp:
        generate_data(fp.read())
