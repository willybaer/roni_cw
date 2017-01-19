/*
 * Event location object
 */
create table roni_location (
		uuid            varchar(128) not null,
		city_uuid       varchar(128),
		name            varchar(256) not null,
		description     text,
		street          varchar(256),
    phone           varchar(128),
    email           varchar(256),
    website         varchar(256),
    created_at      timestamp    not null default current_timestamp,
		modified_at     timestamp    not null default current_timestamp,
		constraint pk_location primary key (uuid),
		constraint fk_location__city foreign key (city_uuid) references roni_city (uuid),
		constraint uk_location_email unique (email)
);
create trigger roni_location_update
before insert or update on roni_location
for each row execute procedure roni_update_modified();


/*
 * Event object
 */
create table roni_event (
		uuid            varchar(128) not null,
		location_uuid   varchar(128) not null,
		description     text,
		created_at      timestamp    not null default current_timestamp,
		modified_at     timestamp    not null default current_timestamp,
		constraint pk_event primary key (uuid),
		constraint fk_event__location foreign key (location_uuid) references roni_location (uuid)
);
create trigger roni_event_update
before insert or update on roni_event
for each row execute procedure roni_update_modified();