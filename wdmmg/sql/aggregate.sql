-- Play pen for lib/aggregate.py

select * from key;

select * from slice;

select
    sum(p.amount),
    (select value from key_value where object_id = a.id
        and key_id = '8204e14c-d4c4-4a8f-876b-b61c30d49091') as dept,
    (select value from key_value where object_id = a.id
        and key_id = '4722e29a-cfea-44d1-8785-96a458453e91') as region
from account a, posting p, 'transaction' t
where a.slice_id = 'd7b2cab1-4a4e-4313-86a6-828a63535616' -- CRA
and a.id = p.account_id
and a.id not in (select object_id from key_value where value = 'yes'
    and key_id = '0b05ee0b-6a20-4ed3-b36f-329888908dcc') -- spender
and t.id = p.transaction_id
and t.timestamp >= '1000-01-01'
and t.timestamp < '3000-01-01'
group by dept, region;

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

ak_1 1b3a4ebf-a599-4f9f-b240-a3945969ea58
ak_0 6f681fe5-6cba-4063-bdde-d91e2d5f8ee5
v_0 yes%
v_1 ENGLAND%
slice_id aeab1d75-6655-4ca6-aa45-5e0c1302c341
k_1 d13836fd-876e-4432-b308-a06713d03d02
k_0 a2281133-553b-494a-acaa-654518a5d090

