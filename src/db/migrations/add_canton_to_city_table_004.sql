alter table roni_city add column canton varchar(128);
alter table roni_city add column website varchar(256);
alter table roni_city add column alpha_2_code varchar(2);

update roni_city set alpha_2_code = 'DE' where country = 'Deutschland';