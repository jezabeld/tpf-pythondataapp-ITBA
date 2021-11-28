from utils.db_connections import PostgresClient

db_name = "db_name" 
user = "user" 
passw = "passw" 
db_url = "db_url"

def test_get_engine_creation(mocker):
    print("[Test PostgresClient Get Engine] should return new engine instance.")

    engine_returned_instace = "engine_returned_instace"
    mocker.patch('utils.db_connections.create_engine', return_value = engine_returned_instace)

    pg_cli = PostgresClient(db_name, user, passw, db_url)
    assert  pg_cli._get_engine() == engine_returned_instace
    pg_cli._engine = None

def test_get_engine_cached(mocker):
    print("[Test PostgresClient Get Engine] should return existing engine instance.")

    cached_engine = "cached_engine"
    engine_returned_instace = "engine_returned_instace"
    mocker.patch('utils.db_connections.create_engine', return_value = engine_returned_instace)

    pg_cli = PostgresClient(db_name, user, passw, db_url)
    pg_cli._engine = cached_engine
    assert  pg_cli._get_engine() == cached_engine
    pg_cli._engine = None

def test_get_session(mocker):
    print("[Test PostgresClient Get Session] should return driver session")

    driver_session = 'driver_session'
    engine_returned_instace = "engine_returned_instace"

    def SessionMock(**kwargs):
        return driver_session

    mocker.patch('utils.db_connections.create_engine', return_value = engine_returned_instace)
    mocker.patch('utils.db_connections.sessionmaker', return_value = SessionMock)

    pg_cli = PostgresClient(db_name, user, passw, db_url)

    assert pg_cli.get_session() == driver_session
    pg_cli._engine = None