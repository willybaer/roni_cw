/*
 * Category object
 */
create table category (
		uuid                          varchar(128) not null,
    parent_category_uuid          varchar(128),
    foursquare_id                 varchar(256),
    foursquare_icon               varchar(256),
    name_de                       varchar(256),
    name_en                       varchar(256),
    name_it                       varchar(256),
    name_fr                       varchar(256),
    name_es                       varchar(256),
    name_ja                       varchar(256),
    created_at    timestamp    not null default current_timestamp,
		modified_at   timestamp    not null default current_timestamp,
		constraint pk_category primary key (uuid)
);
create trigger category_update
before insert or update on category
for each row execute procedure update_modified();

/*
 * Add category relation to location
 */
alter table location add column category_uuid varchar(128);
alter table location add constraint fk_location__category foreign key (category_uuid) references category (uuid)