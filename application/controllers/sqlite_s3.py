from dataclasses import dataclass
from functools import partial
from typing import Optional

from sqlite_s3_query import sqlite_s3_query

from config.config import Config


class SqliteS3Accessor:
    # TODO if this gets any more complicated then we need to instrument sqlalchemy here

    def __init__(self, bucket: str, db_path: str, region="eu-west-2"):
        self.query_session = partial(
            sqlite_s3_query,
            url=f'https://{bucket}.s3.{region}.amazonaws.com/{db_path}',
            get_credentials=self._get_credentials
        )

    @staticmethod
    def _get_credentials(*args, **kwargs):
        return (
            Config.AWS_DEFAULT_REGION,
            Config.AWS_ACCESS_KEY_ID,
            Config.AWS_SECRET_ACCESS_KEY,
            Config.AWS_SESSION_TOKEN,  # Only needed for temporary credentials
        )


    def select(self, table_name: str, columns='*', where_clause='', pagination_clauses=''):

        query_string = f'SELECT {columns} FROM {table_name} '
        if where_clause:
            query_string += 'WHERE {where_clause} '
        query_string += pagination_clauses

        # TODO This syntax is python=>3.10 only, fix this
        with (
            self.query_session() as query,
            query(
                query_string
                #  params=('my-value',)
            ) as (columns, rows)
        ):
            for row in rows:
                yield row


@dataclass
class Database:
    bucket: str
    database_path: str
    query_args: tuple[str]
    query_kwargs: dict
    polling_result: Optional[str]


class SqliteS3Controller:

    def __init__(self, *args, **kwargs):
        # TODO curl https://raw.githubusercontent.com/digital-land/specification/main/specification/dataset.csv and parse to get full dataset artifact list
        self.databases = [
            Database(
                bucket='digital-land-collection',
                database_path='digital-land.sqlite3',
                query_args=('log',),
                query_kwargs={'columns': 'entry_date', 'pagination_clauses': 'ORDER BY entry_date desc LIMIT 1'},
                polling_result=None
            )
        ]

    def get_all_databases(self):
        for database in self.databases:
            cont = SqliteS3Accessor(database.bucket, database.database_path)
            database.polling_result = list(cont.select(*database.query_args, **database.query_kwargs))[0][0]
        return [(database.bucket, database.database_path, database.polling_result) for database in self.databases]
