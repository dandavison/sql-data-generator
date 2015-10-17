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
    column = {}
    for token in _get_tokens(create_table_stmnt):

        if token.ttype == tokens.Name:
            if 'name' in column:
                assert is_complete_column(column)
                columns.append(column)
                column = {}
            column['name'] = token.value
        else:
            import ipdb ; ipdb.set_trace()

    assert is_complete_column(column)
    columns.append(column)

    return columns


def is_complete_column(column):
    return column.viewkeys() == {'name'}


def _get_tokens(create_table_stmnt):
    for tok1 in create_table_stmnt.tokens:
        if isinstance(tok1, sql.Function):
            for tok2 in tok1.tokens:
                if isinstance(tok2, sql.Parenthesis):
                    for tok3 in tok2.tokens:
                        if isinstance(tok3, sql.Identifier):
                            [tok3] = tok3.tokens
                            yield tok3
                        elif isinstance(tok3, sql.IdentifierList):
                            for tok4 in tok3.tokens:
                                if isinstance(tok4, sql.Identifier):
                                    [tok4] = tok4.tokens
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
