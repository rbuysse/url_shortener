drop table if exists urls;
create table urls (
	id integer primary key autoincrement,
	date_added date not null default (CURRENT_DATE),
	key text not null unique,
	dest text not null,
	access_count integer not null default(0)
	);