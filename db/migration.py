import getopt
import sys
import os
import connection as db_con
import config as config_file
import datetime
from psycopg2.extensions import AsIs

DB_CHANGE_LOG = 'database_change_log'


def new(file_name):
    # Creating migrations folder if not exists
    migrations_dir = '%s/migrations' % os.getcwd()
    if not os.path.exists(migrations_dir):
        os.makedirs(migrations_dir)

    # Create new file with current timestamp
    d_file_name = '%s_%s.sql' % (datetime.datetime.now().strftime('%Y%m%d%H%M%S'), file_name)
    open('%s/%s' % (migrations_dir, d_file_name), 'w')
    print('Created new migrations file %s' % d_file_name)


def migrate(env):
    # Migrations file
    migrations_dir = '%s/migrations' % os.getcwd()
    if os.path.exists(migrations_dir):
        # Run migrations
        conn = db_con.connection(config_file.db_config[env])
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
        for file in os.listdir(migrations_dir):  # Return the name of the files in directory
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
                    s = open('%s/%s' % (migrations_dir, file), 'r').read()
                    cur.execute(s)
                    conn.commit()

                    # Add migration log entry
                    print('Adding log entry for timestamp: %s' % log_level)
                    cur.execute('INSERT INTO %s (last_timestamp) VALUES (%s)', (AsIs(DB_CHANGE_LOG), int(log_level),))
                    conn.commit()

        cur.close()
        conn.close()
    else:
        print('No migrations exisiting')


def main(argv):
    # Migration handling
    try:
        opts, args = getopt.getopt(argv[1:], 'n:m:d:', ['new=', 'migrate=', 'db='])
    except getopt.GetoptError:
        sys.exit(2)

    # DB environment
    env = list(filter(lambda x: x[0] in ('-d', '--db'), opts))
    if env and len(env) > 0:
        env = env[0][1]
    else:
        env = next(iter(config_file.db_config.keys()))

    for opt, arg in opts:
        if opt in ('-m', '--migrate'):
            migrate(env)
        elif opt in ('-n', '--new'):
            new(arg)


if __name__ == "__main__":
    main(sys.argv)
