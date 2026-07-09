-- Run this once in the Supabase SQL editor (Project -> SQL Editor -> New query)

create table cocktails (
  id bigint generated always as identity primary key,
  name text unique not null,
  instructions text not null
);

create table cocktail_ingredients (
  id bigint generated always as identity primary key,
  cocktail_id bigint not null references cocktails(id) on delete cascade,
  name text not null,
  amount text not null
);

-- One row per (user, ingredient they own)
create table inventory_items (
  id bigint generated always as identity primary key,
  user_id uuid not null references auth.users(id) on delete cascade,
  name text not null,
  unique (user_id, name)
);

alter table inventory_items enable row level security;

create policy "Users manage their own inventory"
  on inventory_items
  for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- Seed data, migrated from recipes.py
insert into cocktails (name, instructions) values
  ('Mojito', 'Muddle mint, add rum and lime.'),
  ('Margarita', 'Shake and serve.');

insert into cocktail_ingredients (cocktail_id, name, amount)
select id, 'Rum', '1oz' from cocktails where name = 'Mojito'
union all
select id, 'Mint', '1-2 leaves' from cocktails where name = 'Mojito'
union all
select id, 'Lime', '1oz' from cocktails where name = 'Mojito'
union all
select id, 'Tequila', '1.5oz' from cocktails where name = 'Margarita'
union all
select id, 'Lime', '1oz' from cocktails where name = 'Margarita'
union all
select id, 'Triple sec', '1oz' from cocktails where name = 'Margarita';

-- Migration: run this next, in the SQL editor, to add shareable read-only links.
-- Lets each account holder share a code/link that shows "what can be made"
-- to anyone who has it, without a login and without exposing inventory or edit access.
create table profiles (
  user_id uuid primary key references auth.users(id) on delete cascade,
  share_code text unique not null
);

alter table profiles enable row level security;

create policy "Users manage their own profile"
  on profiles
  for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- Migration: run this next, in the SQL editor, to make cocktails per-user.
-- Previously every cocktail was global and visible to all users; now each
-- user only sees the cocktails they added. Existing cocktails (the seed
-- data and anything added before this migration) are assigned to whichever
-- account was created first, so they aren't silently deleted.
alter table cocktails add column user_id uuid references auth.users(id) on delete cascade;

update cocktails set user_id = (select id from auth.users order by created_at asc limit 1)
where user_id is null;

alter table cocktails alter column user_id set not null;

alter table cocktails drop constraint if exists cocktails_name_key;
alter table cocktails add constraint cocktails_user_id_name_key unique (user_id, name);

alter table cocktails enable row level security;

create policy "Users manage their own cocktails"
  on cocktails
  for all
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

alter table cocktail_ingredients enable row level security;

create policy "Users manage their own cocktail ingredients"
  on cocktail_ingredients
  for all
  using (exists (
    select 1 from cocktails c
    where c.id = cocktail_ingredients.cocktail_id and c.user_id = auth.uid()
  ))
  with check (exists (
    select 1 from cocktails c
    where c.id = cocktail_ingredients.cocktail_id and c.user_id = auth.uid()
  ));

-- Migration: run this next, in the SQL editor, to split inventory into
-- spirits and mixers. Existing items default to 'mixer' since we can't
-- infer which category they were before.
alter table inventory_items add column category text not null default 'mixer'
  check (category in ('spirit', 'mixer'));

-- Migration: run this next, in the SQL editor, to let each account holder
-- name their bar. Defaults to "Anonymous' Bar" for existing profiles.
alter table profiles add column bar_name text not null default 'Anonymous'' Bar';
