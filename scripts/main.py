import sys
import db.connection as db_con
from events.event import Event


def main(argv):
    db_con.init_db()
    for event in Event.find_all():
        print(event.uuid)
    pass


if __name__ == "__main__":
    main(sys.argv)
