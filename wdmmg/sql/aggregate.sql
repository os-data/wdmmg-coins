-- Play pen for lib/aggregate.py

select * from key;

select * from slice;

-- New version.

SELECT
    (SELECT value FROM key_value WHERE object_id = a.id
        AND key_id = '6f681fe5-6cba-4063-bdde-d91e2d5f8ee5') AS axis_0,
    (SELECT value FROM key_value WHERE object_id = a.id
        AND key_id = '1b3a4ebf-a599-4f9f-b240-a3945969ea58') AS axis_1,
    SUM(p.amount) as amount,
    t.timestamp
FROM account a, posting p, "transaction" t
WHERE a.slice_id = 'aeab1d75-6655-4ca6-aa45-5e0c1302c341'
AND a.id = p.account_id
AND a.id NOT IN (SELECT object_id FROM key_value
    WHERE key_id = 'a2281133-553b-494a-acaa-654518a5d090' AND value LIKE 'yes%')
AND a.id IN (SELECT object_id FROM key_value
    WHERE key_id = 'd13836fd-876e-4432-b308-a06713d03d02' AND value LIKE 'ENGLAND%')
AND t.id = p.transaction_id
--AND t.timestamp >= :start_date
--AND t.timestamp < :end_date
GROUP BY t.timestamp, axis_0, axis_1
ORDER BY t.timestamp, axis_0, axis_1
;

-- Population

SELECT ev.name, kv.value
FROM enumeration_value ev, key_value kv
WHERE ev.key_id = '8dc888de-27a7-41f3-ba80-c4c65a46f286'
AND kv.key_id = '18608816-2079-48cb-9ccc-97577710164f'
AND kv.object_id = ev.id
;

