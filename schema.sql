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
