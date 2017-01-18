/*
 * City object
 */
create table roni_city (
		uuid          varchar(128) not null,
    zip           varchar(64),
    city          varchar(256),
    state         varchar(256),
    country       varchar(128),
    latitude      double precision,
    longitude     double precision,
    created_at    timestamp    not null default current_timestamp,
		modified_at   timestamp    not null default current_timestamp,
		constraint pk_city primary key (uuid),
		constraint uk_city_city unique (city, zip, country)
);
create trigger roni_city_update
before insert or update on roni_city
for each row execute procedure roni_update_modified();