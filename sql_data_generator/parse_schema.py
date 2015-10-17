import sqlparse


COLUMN_TYPES = {
    'bigint',
    'char',
    'decimal',
    'int',
    'smallint',
    'tinyint',
    'varchar',
}


def parse_schema(text):
    statements = sqlparse.parse(text)
    tables = []
    for create_table_stmnt in get_create_table_statements(statements):
        table_name = create_table_stmnt.get_name()
        columns = get_columns(create_table_stmnt)
        tables.append({
            'name': table_name,
            'columns': columns,
        })
    return tables


def get_columns(create_table_stmnt):

    parenthesized_group = get_parenthesized_group(create_table_stmnt)
    tokens = flatten_tokens(parenthesized_group.tokens)
    tokens = drop_ignored_tokens(tokens)
    token_groups = split_tokens_on_commas(tokens)

    columns = []
    for group in token_groups:

        column = {}
        token, group = group[0], group[1:]

        if isinstance(token, sqlparse.sql.Identifier):
            assert 'name' not in column
            column['name'] = token.value
        else:
            assert (hasattr(token, 'ttype') and
                    token.ttype == sqlparse.tokens.Keyword)
            column['name'] = None
            column['keyword'] = token.value

        for token in group:
            if isinstance(token, sqlparse.sql.Function):
                column_type, arguments = parse_unary_function(token)

                if column_type in COLUMN_TYPES:
                    column.update({
                        'type': column_type,
                        'type_arguments': map(int, arguments.split(',')),
                    })
                else:
                    print >>sys.stderr, ("Unrecognized column type: %s" %
                                         column_type)

            elif is_token(token, sqlparse.tokens.Name.Builtin):
                column['type'] = token.value

        columns.append(column)

    return columns


def flatten_tokens(tokens):
    for token in tokens:
        if isinstance(token, sqlparse.sql.IdentifierList):
            for child_token in token.tokens:
                yield child_token
        else:
            yield token


def drop_ignored_tokens(tokens):
    for token in tokens:
        if not (is_token(token, sqlparse.tokens.Whitespace) or
                is_token(token, sqlparse.tokens.Newline) or
                is_punctuation(token, '(') or
                is_punctuation(token, ')')):
            yield token


def split_tokens_on_commas(tokens):
    group = []
    for token in tokens:
        if token.match(sqlparse.tokens.Punctuation, ','):
            yield group
            group = []
        else:
            group.append(token)
    yield group


def get_tokens(obj):
    for child in obj.tokens:
        if hasattr(child, 'tokens'):
            for token in get_tokens(child):
                yield token
        else:
            yield child


def is_complete_column(column):
    return column.viewkeys() == {'name'}


def get_parenthesized_group(create_table_stmnt):
    hack = True
    if hack:
        # FIXME
        return create_table_stmnt.tokens[5].tokens[0].tokens[0].tokens[2]
    else:
        for tok1 in create_table_stmnt.tokens:
            if isinstance(tok1, sqlparse.sql.Function):
                for tok2 in tok1.tokens:
                    if isinstance(tok2, sqlparse.sql.Parenthesis):
                        return tok2
        raise RuntimeError


def get_create_table_statements(statements):
    for stmnt in statements:
        if str(stmnt).strip().startswith('CREATE TABLE'):
            yield stmnt


def is_foreign_key_info(token):
    return token.value == 'FOREIGN'


def parse_unary_function(token):
    identifier, parenthesis = drop_ignored_tokens(token.tokens)
    assert isinstance(identifier, sqlparse.sql.Identifier)
    assert isinstance(parenthesis, sqlparse.sql.Parenthesis)
    open_paren, value, close_paren = parenthesis.tokens
    assert is_punctuation(open_paren, '(')
    assert is_punctuation(close_paren, ')')
    return identifier.value, value.value


def is_punctuation(token, value):
    return token.match(sqlparse.tokens.Punctuation, value)


def is_token(obj, ttype):
    return hasattr(obj, 'ttype') and obj.ttype == ttype


if __name__ == '__main__':
    import sys
    [path] = sys.argv[1:]
    with open(path) as fp:
        tables = parse_schema(fp.read())

    for table in tables:
        print table['name']
        for column in table['columns']:
            print '\t', column
