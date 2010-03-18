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

