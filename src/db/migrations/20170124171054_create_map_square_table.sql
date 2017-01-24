/*
 * Category object
 */
create table map_square (
		id                            serial primary key,
    bottom_left                   decimal ARRAY[2],
    top_right                     decimal ARRAY[2],
    query_type                    varchar(256),
    queried_at                    timestamp
);