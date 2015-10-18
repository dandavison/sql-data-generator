from sql_data_generator import parse_schema, populate_mysql

SCHEMA_FILE = "schema.sql"


if __name__ == '__main__':
    with open(SCHEMA_FILE, 'r') as f:
        schema = f.read()

    parsed_schema = parse_schema.parse_schema(schema)
    tables = populate_mysql.Tables(parsed_schema)

    tables.generate_rows_all_tables()
