db_config = {
    'test': [
        'user=postgres',
        'dbname=postgres_test'
    ],
    'dev': [
        'user=postgres',
        'dbname=postgres'
    ],
    'prod': [
        'user=postgres',
        'dbname=postgres',
        'password=roni2017'
    ]
}

migration_config = {
    'dev': {
        'migration_db': './migrations'
    },
    'prod': {
        'migration_db': './migrations'
    }
}