/*
 * Location object belongs to city
 */
create table location (
		uuid            varchar(128) not null,
		city_uuid       varchar(128) not null,
		foursquare_id   varchar(128),
		yelp_id 		varchar(128),
		gelbeseiten_id	varchar(128),
		name            varchar(256) not null,
		description     text,
		street          varchar(256),
    	phone           varchar(128),
    	email           varchar(256),
    	website         varchar(256),
		twitter 		varchar(256),
		facebook		varchar(256),
    	latitude        double precision,
    	longitude       double precision,
    	created_at      timestamp    not null default current_timestamp,
		modified_at     timestamp    not null default current_timestamp,
		constraint pk_location primary key (uuid),
		constraint fk_location__city foreign key (city_uuid) references city (uuid),
		constraint uk_location_address unique (street, city_uuid, name),
		constraint uk_location_foursquare_id unique (foursquare_id),
		constraint uk_location_yelp_id unique (yelp_id),
		constraint uk_location_gelbeseiten_id unique (gelbeseiten_id)
);
create trigger location_update
before insert or update on location
for each row execute procedure update_modified();