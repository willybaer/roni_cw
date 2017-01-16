import psycopg2
import os

DB_NAME = 'pld'
DB_USER = 'pld'


def connection():
    return psycopg2.connect('dbname=%s user=%s' % (DB_NAME, DB_USER))


def init_db():
    # 1. Check migrations
    conn = connection()
    cur = conn.cursor()

    # 2. Check migrations log table
    # Check if migration log table exists
    cur.execute('select exists(select * from information_schema.tables where table_name=%s)',
                ('roni_mig_log',))
    if not cur.fetchone()[0]:
        print('creating migrations log table')
        s = open('scripts/db/migrations/mig_log.sql', 'r').read()
        cur.execute(s)
        conn.commit()

    for file in os.listdir('scripts/db/migrations'):  # Return the name of the files in directory
        if file.endswith('.sql') and ('mig_log' not in file):
            print(file)

            # Other migrations files
            log_level = file.replace('.sql', '').split('_')
            log_level = log_level[len(log_level) - 1]

            # Check if migration exists
            cur.execute("SELECT * FROM roni_mig_log ORDER BY current_mig_level DESC;")
            last_entry = cur.fetchone()
            print(last_entry)

            if last_entry and last_entry[1] >= int(log_level):
                print('Migration already exists %s' % file)
            else:
                # Execute sql
                print('executing migration for file %s' % file)
                s = open('scripts/db/migrations/%s' % file, 'r').read()
                cur.execute(s)
                conn.commit()

                # Add migration log entry
                print('Adding log entry for level: %s' % log_level)
                cur.execute('INSERT INTO roni_mig_log(current_mig_level) VALUES (%s);', (int(log_level),))
                conn.commit()

    cur.close()
    conn.close()
