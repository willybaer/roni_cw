# Database setup
sudo apt-get update
sudo apt-get install postgresql-9.4


### Backup pg config files
sudo cp /etc/postgresql/9.4/main/pg_hba.conf /etc/postgresql/9.4/main/pg_hba.conf.bak
sudo cp /etc/postgresql/9.4/main/postgresql.conf /etc/postgresql/9.4/main/postgresql.conf.bak

### Allow uses to access db from local network
sudo nano /etc/postgresql/9.4/main/pg_hba.conf

At the end of this file, enter the following line:

host     all     all     192.168.0.0/24     md5

### Change local authenction method from peer to md5
From

local   all             postgres                                peer

To

local   all             postgres                                md5
### Allow connections from outside
sudo nano /etc/postgresql/9.4/main/postgresql.conf

And change the following line:

listen_addresses = 'localhost'  

To:

listen_addresses = '*'  

### And Finally setup postgres user password
sudo -u postgres psql

\password postgres

\q
# Installation on debian machine
sudo apt-get install python3-pip
sudo apt-get install libpq-dev python-dev
sudo pip3 install psycopg2 // PostgresSQL Adapter python3
sudo pip3 install regex


# Connect to raspberry from outside
https://www.remot3.it/