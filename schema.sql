drop table if exists pens;
drop table if exists nodes;
drop table if exists edges;

create table pens (
  id integer primary key autoincrement,
  color text not null,
  material text not null
);

create table nodes (
  id integer primary key autoincrement,
  title text not null,
  has_children integer not null,
  has_parent integer not null,
  pen_id integer not null, foreign key (pen_id) references pens(id)
);

create table edges (
  id integer primary key autoincrement,
  from_graph_id integer not null,
  to_node_id integer not null,
  pen_id integer not null, foreign key (pen_id) references pens(id)
);
