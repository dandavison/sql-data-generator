from sql_data_generator import parse_schema, populate_mysql


if __name__ == '__main__':
    import sys
    [schema_file] = sys.argv[1:]

    with open(schema_file, 'r') as f:
        schema = f.read()

    parsed_schema = parse_schema.parse_schema(schema)
    tables = populate_mysql.Tables(parsed_schema)

    tables.generate_rows_all_tables()
