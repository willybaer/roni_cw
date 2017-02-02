/*
 * Added stuff for handling yelp venues
 */
alter table map_square add column yelp_queried_at timestamp;
alter table category add column yelp_alias varchar(256);
alter table location add column yelp_id varchar(128);