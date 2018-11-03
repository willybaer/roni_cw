/*
 * Location category
 */
create table location_category (
		uuid                                                varchar(128) not null,
    location_uuid                                       varchar(128) not null,
    category_uuid                                       varchar(128) not null,
    constraint pk_location_category                     primary key (uuid),
    constraint pk_location_category__location           foreign key (location_uuid) references location (uuid),
    constraint pk_location_category__category           foreign key (category_uuid) references category (uuid)
);