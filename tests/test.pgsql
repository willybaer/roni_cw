select * from "location"
    where name = 'Speisegaststätte Am Aicha';

delete from location_category
    where location_uuid = '0b6d80fb-2be4-448a-84d4-396f7563678d';

select * from "city"
    where postal_code = '73433';


SELECT location.*, category.uuid AS category_uuid,category.name_de AS category_name_de  
    FROM location 
    JOIN location_category ON location.uuid = location_category.uuid 
    JOIN category ON location_category.uuid = category_uuid 
    WHERE gelbeseiten_id = '14e2e3be-4545-4b21-adda-73705ad630c4'

select count(*) from city;

select count(*) from location;

select * from city
 where zip LIKE '724%' and alpha_2_code = 'DE';

select * from map_square
where yelp_queried_at > NOW() - INTERVAL '1 day' 

select a.uuid, a.name, a.street, o.uuid as o_uuid, o.name as o_name, o.street as o_street from location a
            inner join location o 
                on o.street = a.street 
                and o.city_uuid = a.city_uuid 
                and o.name = a.name
                and o.uuid != a.uuid
            limit 1;

delete from location_category
    where location_uuid IN 
    (
        select o.uuid as o_uuid from location a
            inner join location o 
                on o.street = a.street 
                and o.city_uuid = a.city_uuid 
                and o.name = a.name
                and o.uuid != a.uuid
    );

delete from location
    where uuid IN 
    (
        select o.uuid as o_uuid from location a
            inner join location o 
                on o.street = a.street 
                and o.city_uuid = a.city_uuid 
                and o.name = a.name
                and o.uuid != a.uuid
    );
