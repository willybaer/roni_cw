/*
 * Creating functions for updated and modified timestamp
 */
create or replace function update_modified() returns trigger as $update_modified$
begin
	new.modified_at := current_timestamp;
	return new;
end;
$update_modified$ language plpgsql;


create or replace function update_created() returns trigger as $update_created$
begin
	new.created_at := current_timestamp;
	return new;
end;
$update_created$ language plpgsql;
