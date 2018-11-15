import signal
import sys

import app.db.config as config_file
import app.db.connection as con

class ScrapWarpper:
    '''
        This class represents our wrapper for a scrapping task. 
        It includes the initialization of the database configuration    
    '''
    def __init__(self, db_env='test', *arg, **kwargs):
        super().__init__(*arg, **kwargs)

        # Init db environment
        self.init_db_config(db_env=db_env)

        # Setup keyboard interruption
        signal.signal(signal.SIGINT, self.on_interrupt)
        signal.signal(signal.SIGTERM, self.on_interrupt)

    def on_interrupt(self, sig, frame):
        print('Pressing keyboard interruption CTR+C or someone is killing the process kill PID')

        if hasattr(self, 'on_pressed_interrupt'):
            on_pressed_interrupt = getattr(self, 'on_pressed_interrupt')
            on_pressed_interrupt()
        else:
            print('Implement the function on_pressed_interrupt(self) to handle the keyboard interruption by yourself')    
            sys.exit()

    def init_db_config(self, db_env='test'):
        con.set_db_config(config_file.db_config[db_env])
    
    #def __init_subclass__(cls, *a, **kw):
    #    assert hasattr(cls, 'main'), 'You need to implement the main() function'
    #    return super().__init_subclass__(*a, **kw)    

