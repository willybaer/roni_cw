/*
 * Location object belongs to city
 */
create table location (
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
		constraint fk_location__city foreign key (city_uuid) references city (uuid),
		constraint uk_location_email unique (email)
);
create trigger location_update
before insert or update on location
for each row execute procedure update_modified();