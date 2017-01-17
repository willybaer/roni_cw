import getopt
import sys

import db.connection as db_con
from events.event import Event


def main(argv):
    # Setup connection credentials
    try:
        opts, args = getopt.getopt(argv[1:], 'n:p:u:')
    except getopt.GetoptError:
        sys.exit(2)
    for opt, arg in opts:
        print(opt)
        if opt == '-n':
            db_con.DB_NAME = arg
        elif opt == '-p':
            db_con.DB_PASSWORD = arg
        elif opt == '-u':
            db_con.DB_USER = arg

    db_con.init_db()
    for event in Event.find_all():
        print(event.uuid)


if __name__ == "__main__":
    main(sys.argv)
