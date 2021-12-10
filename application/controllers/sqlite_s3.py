from functools import partial

from sqlite_s3_query import sqlite_s3_query

from config.config import Config

class SqliteS3Controller:
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
