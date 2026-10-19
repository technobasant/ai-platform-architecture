-- The usage mart the assistant answers from: 200 customer accounts, their users, and one
-- row per user, day, event type and platform for the third quarter of 2026. No personal
-- data: users are ids and roles. Seeded, so every build is the same.
\set ON_ERROR_STOP on
select setseed(0.17);

drop schema if exists usage cascade;
create schema usage;
set search_path = usage;

create table accounts (
    account_id int primary key,
    account_name text not null,
    plan_name text not null,
    country text not null,
    signup_date date not null
);
comment on table accounts is 'One row per customer account, as of today.';

create table users (
    user_id int primary key,
    account_id int not null references accounts,
    role text not null,
    created_date date not null
);
comment on table users is 'One row per person on an account. role: admin, member or viewer.';

create table user_daily_activity (
    activity_date date not null,
    account_id int not null,
    user_id int not null,
    event_type text not null,
    platform text not null,
    events int not null,
    primary key (activity_date, user_id, event_type, platform)
);
comment on table user_daily_activity is
    'One row per user, day, event type and platform with at least one event, July to September 2026.';

insert into accounts
select g, 'Account ' || g,
       case when r < 0.40 then 'free' when r < 0.75 then 'team' when r < 0.93 then 'business'
            else 'enterprise' end,
       (array['US', 'GB', 'DE', 'FR', 'NL', 'IN', 'AU', 'CA'])[1 + (g * 7) % 8],
       date '2021-01-01' + (random() * 1950)::int
from (select g, random() as r from generate_series(1, 200) as g) as s;

-- Team size by plan; a fifth of users joined during the quarter.
insert into users
select row_number() over (order by a.account_id, n), a.account_id,
       (array['admin', 'member', 'member', 'member', 'viewer'])[1 + floor(random() * 5)::int],
       case when random() < 0.2 then date '2026-07-01' + (random() * 91)::int
            else date '2019-06-01' + (random() * 2500)::int end
from accounts as a
cross join lateral generate_series(1, case a.plan_name
    when 'free' then 1 + floor(random() * 3)::int
    when 'team' then 3 + floor(random() * 10)::int
    when 'business' then 8 + floor(random() * 23)::int
    else 20 + floor(random() * 41)::int end) as n;

-- Each user has a usual platform and a level of activity; weekdays are busier.
create temporary table user_profile as
select user_id, account_id, created_date,
       (array['web', 'web', 'web', 'ios', 'android'])[1 + floor(random() * 5)::int] as main_platform,
       0.15 + random() * 0.55 as activity
from users;

-- Two steps, so each random() is drawn per row: a condition on random() alone would be
-- pushed down to the VALUES list and drawn once per event type.
create temporary table active_days as
select p.user_id, p.account_id, p.main_platform, d::date as day
from user_profile as p
cross join generate_series(date '2026-07-01', date '2026-09-30', interval '1 day') as d
where d::date >= p.created_date
  and random() < p.activity * (case when extract(isodow from d) in (6, 7) then 0.3 else 1 end);

insert into user_daily_activity
select a.day, a.account_id, a.user_id, e.event_type,
       case when random() < 0.8 then a.main_platform
            else (array['web', 'ios', 'android'])[1 + floor(random() * 3)::int] end,
       1 + floor(random() * e.max_events)::int
from active_days as a
cross join (values ('login', 0.95, 2), ('view_dashboard', 0.85, 9), ('create_report', 0.35, 4),
                   ('share_report', 0.20, 3), ('export_csv', 0.15, 3), ('invite_user', 0.03, 2),
                   ('api_call', 0.10, 40)) as e(event_type, chance, max_events)
where random() < e.chance + 0 * a.user_id;

analyze;

-- Access. One login role per account, read-only, scoped to its own rows by row-level
-- security on every table; the assistant's tool connects as the caller's role. A second
-- role reads everything: it is what the assistant would use if isolation lived only in
-- the prompt.
create table tenant_roles (role_name text primary key, account_id int not null);
insert into tenant_roles select 'acct_' || account_id, account_id from accounts;

drop role if exists reads_everything;
create role reads_everything login;
grant usage on schema usage to reads_everything;
grant select on all tables in schema usage to reads_everything;
alter role reads_everything set default_transaction_read_only = on;
alter role reads_everything set statement_timeout = '15s';
alter role reads_everything set search_path = usage;

do $$
declare r record;
begin
    for r in select role_name from tenant_roles loop
        execute format('drop role if exists %I', r.role_name);
        execute format('create role %I login', r.role_name);
        execute format('grant usage on schema usage to %I', r.role_name);
        execute format('grant select on accounts, users, user_daily_activity, tenant_roles to %I',
                       r.role_name);
        execute format('alter role %I set default_transaction_read_only = on', r.role_name);
        execute format('alter role %I set statement_timeout = %L', r.role_name, '15s');
        execute format('alter role %I set search_path = usage', r.role_name);
    end loop;
end $$;

create function my_account() returns int language sql stable security definer
    set search_path = usage
    as $$ select account_id from tenant_roles where role_name = session_user $$;

alter table accounts enable row level security;
alter table users enable row level security;
alter table user_daily_activity enable row level security;
alter table tenant_roles enable row level security;
create policy own_account on accounts for select using (account_id = my_account());
create policy own_account on users for select using (account_id = my_account());
create policy own_account on user_daily_activity for select using (account_id = my_account());
create policy own_role on tenant_roles for select using (role_name = session_user);
create policy everything on accounts for select to reads_everything using (true);
create policy everything on users for select to reads_everything using (true);
create policy everything on user_daily_activity for select to reads_everything using (true);
create policy everything on tenant_roles for select to reads_everything using (true);
