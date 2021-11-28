"""Database connection handling."""
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import pandas as pd

class AbstractDbClient:
    """Base class to implement DB Connection."""
    def __init__(self, db, user= None, passw= None, host=None, driver=None, port=None):
        self.db = db
        self._engine = None
        self._Session_Factory = None

    def _get_engine(self):
        """Abstract method to get engine according to dialects."""
        raise NotImplementedError("Please Implement this method")

    def get_session(self):
        if not self._Session_Factory:
            self._Session_Factory = sessionmaker(bind = self._get_engine())
        return self._Session_Factory()

    def _connect(self):
        return self._get_engine().connect()

    @staticmethod
    def _cursor_columns(cursor):
        if hasattr(cursor, 'keys'):
            return cursor.keys()
        else:
            return [c[0] for c in cursor.description]

    def execute(self, sql, connection=None):
        if connection is None:
            connection = self._connect()
        return connection.execute(sql)

    def insert_from_frame(self, df, table, if_exists='append', index=False, **kwargs):
        connection = self._connect()
        with connection:
            df.to_sql(table, connection, if_exists=if_exists, index=index, **kwargs)

    def to_frame(self, *args, **kwargs):
        cursor = self.execute(*args, **kwargs)
        if not cursor:
            return
        data = cursor.fetchall()
        if data:
            df = pd.DataFrame(data, columns=self._cursor_columns(cursor))
        else:
            df = pd.DataFrame()
        return df

class SqLiteClient(AbstractDbClient):
    def __init__(self, db):
        AbstractDbClient.__init__(self, db)

    def _get_engine(self):
        db_uri = f'sqlite:///{self.db}'
        if not self._engine:
            self._engine = create_engine(db_uri)
        return self._engine

class PostgresClient(AbstractDbClient):
    def __init__(self, db, user, passw, host, port=None, driver='psycopg2'):
        self._user = user
        self._passw = passw
        self._host = host
        self._port = port
        self._driver=driver
        AbstractDbClient.__init__(self, db)

    def _get_engine(self):
        aux_conn=f'postgresql'
        aux_conn+= f'+{self._driver}' if self._driver else ''
        aux_host = f'{self._host}'
        aux_host+= f'+{self._port}' if self._port else ''
        db_uri = f'{aux_conn}://{self._user}:{self._passw}@{aux_host}/{self.db}'
        if not self._engine:
            self._engine = create_engine(db_uri)
        return self._engine