import getopt
import sys
import os
import app.db.connection as db_con
import datetime

from psycopg2.extensions import AsIs
from .config import migration_config, db_config

DB_CHANGE_LOG = 'database_change_log'
MIGRATIONS_DIR = './migrations'

def new(env, file_name):
    # Creating migrations folder if not exists
    migrations_dir = MIGRATIONS_DIR
    if env in migration_config.keys() and 'migration_db' in migration_config[env]:
        migrations_dir = migration_config[env]['migration_db']
    
    full_path = os.path.realpath(__file__)
    file_dir = os.path.split(full_path)[0]
    migrations_dir = '%s/%s' % (file_dir, migrations_dir)

    if not os.path.exists(migrations_dir):
        os.makedirs(migrations_dir)

    # Create new file with current timestamp
    d_file_name = '%s_%s.sql' % (datetime.datetime.now().strftime('%Y%m%d%H%M%S'), file_name)
    open('%s/%s' % (migrations_dir, d_file_name), 'w')
    print('Created new migrations file %s' % d_file_name)


def migrate(env):
    # Migrations file
    db_con.DB_CONFIG = db_config[env]

    migrations_dir = MIGRATIONS_DIR
    if env in migration_config.keys() and 'migration_db' in migration_config[env]:
        migrations_dir = migration_config[env]['migration_db']

    full_path = os.path.realpath(__file__)
    file_dir = os.path.split(full_path)[0]
    migrations_dir = '%s/%s' % (file_dir, migrations_dir)
    
    if os.path.exists(migrations_dir):
        # Run migrations
        conn = db_con.connection()
        cur = db_con.cursor(conn)

        # Check if change log table exists
        cur.execute('select exists(select * from information_schema.tables where table_name=%s)',
                    (DB_CHANGE_LOG,))
        if not cur.fetchone()[0]:
            print('creating database change log table')
            cur.execute('CREATE TABLE %s (id serial primary key, last_timestamp bigint)', (AsIs(DB_CHANGE_LOG),))
            conn.commit()
        else:
            print('database changelog table already exists')

        # Iterate over migration files
        files = os.listdir(migrations_dir)
        files = list(filter(lambda f: f.endswith('.sql') , files))
        ordered_files = sorted(files, key=lambda x: int(x.split('_')[0]))
        try:
            for file in ordered_files:  # Return the name of the files in directory
                if file.endswith('.sql'):
                    # Log timestamp
                    log_level = file.split('_')
                    log_level = log_level[0]

                    # Check if migration exists
                    cur.execute('SELECT * FROM %s ORDER BY last_timestamp DESC', (AsIs(DB_CHANGE_LOG),))
                    last_entry = cur.fetchone()

                    if last_entry and last_entry['last_timestamp'] >= int(log_level):
                        print('Migration already exists for file %s' % file)
                    else:
                        # Execute sql
                        print('executing migration for file %s' % file)
                        s = open('%s/%s' % (migrations_dir, file), 'rb').read().decode('UTF-8')
                        cur.execute(s)
                        conn.commit()

                        # Add migration log entry
                        print('Adding log entry for timestamp: %s' % log_level)
                        cur.execute('INSERT INTO %s (last_timestamp) VALUES (%s)', (AsIs(DB_CHANGE_LOG), int(log_level),))
                        conn.commit()
        except Exception as e:
            print(e)
            conn.rollback()
        finally:
            if cur is not None:
                cur.close()
            if conn is not None:
                conn.close()
    else:
        print('No migrations exisiting')


def main():
    # Migration handling
    argv = sys.argv
    try:
        opts, args = getopt.getopt(argv[1:], 'n:md:', ['new=', 'migrate', 'db='])
    except getopt.GetoptError:
        sys.exit(2)

    # DB environment
    env = list(filter(lambda x: x[0] in ('-d', '--db'), opts))
    if env and len(env) > 0:
        env = env[0][1]
    else:
        env = next(iter(db_config.keys()))

    for opt, arg in opts:
        if opt in ('-n', '--new'):
            new(env, arg)
        elif opt in ('-m', '--migrate'):
            migrate(env)