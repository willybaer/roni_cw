/*
 * Event object
 */
create table event (
		uuid            varchar(128) not null,
		location_uuid   varchar(128) not null,
		description     text,
		created_at      timestamp    not null default current_timestamp,
		modified_at     timestamp    not null default current_timestamp,
		constraint pk_event primary key (uuid),
		constraint fk_event__location foreign key (location_uuid) references location (uuid)
);
create trigger event_update
before insert or update on event
for each row execute procedure update_modified();