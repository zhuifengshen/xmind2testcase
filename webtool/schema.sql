drop table if exists records;

create table records (
  id integer primary key autoincrement,
  name text not null,
  create_on text not null,
  note text,
  is_deleted integer DEFAULT 0
);