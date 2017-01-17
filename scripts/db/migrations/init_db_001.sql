/*
 * Creating functions for updated and modified timestamp
 */
create or replace function roni_update_modified() returns trigger as $roni_update_modified$
begin
	new.modified_at := current_timestamp;
	return new;
end;
$roni_update_modified$ language plpgsql;


create or replace function roni_update_created() returns trigger as $roni_update_created$
begin
	new.created_at := current_timestamp;
	return new;
end;
$roni_update_created$ language plpgsql;
