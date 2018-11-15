/*
 * City object
 */
create table city (
		uuid                      varchar(128)  not null,
		parent_city_uuid          varchar(128),
    postal_code               text[]   not null,
    name                      varchar(256)  not null,
    state                     varchar(256),
    country                   varchar(128)  not null,
    latitude                  double precision,
    longitude                 double precision,
    website                   varchar(256),
    alpha_2_code              varchar(2)    not null,
    created_at                timestamp     not null default current_timestamp,
		modified_at               timestamp     not null default current_timestamp,
		constraint pk_city primary key (uuid),
    constraint fk_city__city foreign key (parent_city_uuid) references city (uuid)
);
create trigger city_update
before insert or update on city
for each row execute procedure update_modified();