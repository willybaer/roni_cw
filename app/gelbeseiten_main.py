import sys
import getopt
import roni_database.db_config as config_file

import app.gelbeseiten as gelbeseiten

from roni_utils.argsextractor import filter_args
from roni_scrapper.scrap_wrapper import ScrapWarpper


class Gelebeseiten(ScrapWarpper):

    def __init__(self, db_env='test', *arg, **kwargs):
        super().__init__(db_env=db_env, *arg, **kwargs)
        self.process_interupted = False

    def main(self):
        '''
            Starting point here
        '''
        entries = gelbeseiten.take_first_in_next_sitemap(limit=100)
        for entry in entries:
            try:
                gelbeseiten.query_industry_details(entry, gelbeseiten_id=entry.split('/')[-1])
            except Exception as e:
                print(e)
                gelbeseiten.write_failed_details_page(entry)

        if self.process_interupted:
            print('Closing process due to interruption')
            return

        if len(entries) == 100:    
            self.main()    


    def on_pressed_interrupt(self):
        self.process_interupted = True


def main():
    argv = sys.argv
    
    args = filter_args(argv=argv, opts=[('d:', 'db=')])

    # Setup DB environment
    env = 'dev' # Default
    if 'db=' in args.keys():
        env = args['db=']

    # Start main process
    gelbeseiten = Gelebeseiten(db_env=env)        
    gelbeseiten.main()

if __name__ == '__main__':    
    main()