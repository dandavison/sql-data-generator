"""
Parse (my)SQL schema.

For each CREATE TABLE statement output a parsed table of the form:

{'name': <table_name>, 'columns': [column]}

where `column` is of the form

{
  'name': string,
  'type': "int"|"varchar"|etc,
  'type_arguments': [int],
  'foreign_key_table': string|None,
  'foreign_key_column': string|None,
}
"""
import mock
import sqlparse


COLUMN_TYPES = {
    'bigint',
    'char',
    'datetime',
    'decimal',
    'int',
    'longtext',
    'smallint',
    'tinyint',
    'varchar',
}

CONSTRAINT = 'CONSTRAINT'
FOREIGN = 'FOREIGN'
KEY = 'KEY'
REFERENCES = 'REFERENCES'

KEYWORDS = dict(
    sqlparse.keywords.KEYWORDS.items() + [
        ('DATETIME', sqlparse.tokens.Name.Builtin),
        ('LONGTEXT', sqlparse.tokens.Name.Builtin),
    ]
)

# Add missing keywords to parser
@mock.patch.object(sqlparse.lexer, 'KEYWORDS', KEYWORDS)
def parse_schema(text):
    statements = sqlparse.parse(text)
    tables = []
    for create_table_stmnt in get_create_table_statements(statements):
        table_name = next_atomic_token_by_type(create_table_stmnt,
                                               sqlparse.tokens.Name).value
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

    columns = {}
    for group in token_groups:

        if isinstance(group[0], sqlparse.sql.Identifier):
            token, group = group[0], group[1:]
            column = {'name': token.value}
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

            columns[column['name']] = column

        else:
            # key/constraint declaration
            if is_keyword(group[0], CONSTRAINT):
                group = iter(group)
                for token in group:
                    if is_keyword(token, FOREIGN):
                        assert is_keyword(next(group), KEY)
                        fk_column_name = (
                            parse_single_parenthesized_expression(next(group)))
                        assert is_keyword(next(group), REFERENCES)
                        target_table_name, target_column_name = (
                            parse_unary_function(next(group)))
                        columns[fk_column_name].update({
                            'foreign_key_table': target_table_name,
                            'foreign_key_column': target_column_name,
                        })

    return columns.values()


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


def get_atomic_tokens(obj):
    for child in obj.tokens:
        if hasattr(child, 'tokens'):
            for token in get_atomic_tokens(child):
                yield token
        else:
            yield child


def next_atomic_token_by_type(obj, ttype):
    return next(tok
                for tok in get_atomic_tokens(obj)
                if tok.ttype == ttype)


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
    fn_name = identifier.value
    value = parse_single_parenthesized_expression(parenthesis)
    return fn_name, value


def parse_single_parenthesized_expression(token):
    assert isinstance(token, sqlparse.sql.Parenthesis)
    open_paren, value, close_paren = token.tokens
    assert is_punctuation(open_paren, '(')
    assert is_punctuation(close_paren, ')')
    return value.value


def is_punctuation(token, value):
    return token.match(sqlparse.tokens.Punctuation, value)


def is_token(obj, ttype):
    return hasattr(obj, 'ttype') and obj.ttype == ttype


def is_keyword(obj, keyword):
    return is_token(obj, sqlparse.tokens.Keyword) and obj.value == keyword


if __name__ == '__main__':
    import sys
    [path] = sys.argv[1:]
    with open(path) as fp:
        tables = parse_schema(fp.read())

    for table in tables:
        print table['name']
        for column in table['columns']:
            print '\t', column
