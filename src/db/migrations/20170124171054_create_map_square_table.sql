/*
 * Map square object
 */
create table map_square (
		uuid                          varchar(128) not null,
    bottom_left                   decimal ARRAY[2],
    top_right                     decimal ARRAY[2],
    query_type                    varchar(256),
    queried_at                    timestamp,
    constraint pk_map_square      primary key (uuid)
);