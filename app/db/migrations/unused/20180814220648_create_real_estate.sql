/*
 * Real estate
 */
create type prop_action as enum ('rent', 'buy');
create type prop_type as enum ('apartment', 'house', 'plot', 'garage', 'other');
create table real_estate (
		uuid                                                varchar(128) not null,
    location_uuid                                       varchar(128) not null,
    property_type                                       prop_type not null default 'apartment',
    property_action                                     prop_action not null default 'rent',
    title                                               text not null,
    description                                         text,

    price                                               double precision,
    currency                                            varchar(3),
    living_space                                        double precision,
    land_area                                           double precision,
    area                                                double precision,
    rooms                                               smallint,

		created_at                                          timestamp    not null default current_timestamp,
		modified_at                                         timestamp    not null default current_timestamp,
    constraint pk_real_estate                           primary key (uuid),
    constraint fk_real_estate__location                 foreign key (location_uuid) references location (uuid)
);
create trigger event_update
before insert or update on real_estate
for each row execute procedure update_modified();
