db_config = {
    'test': [
        'user=postgres',
        'dbname=roni_test'
    ],
    'dev': [
        'user=postgres',
        'dbname=roni_dev'
    ],
    'prod': [
        'user=postgres',
        'dbname=roni_prod',
        'password=roni2018'
    ]
}

migration_config = {
    'test': {
        'migration_db': './migrations'
    },
    'dev': {
        'migration_db': './migrations'
    },
    'prod': {
        'migration_db': './migrations'
    }
}