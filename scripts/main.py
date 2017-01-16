import sys
import db.connection as DB_CON


def main(argv):
    DB_CON.init_db()
    pass


if __name__ == "__main__":
    main(sys.argv)
