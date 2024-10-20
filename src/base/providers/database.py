import asyncpg

# RDS Proxyを利用する場合は以下のクラスをcreate_poolにサブクラスとして渡す
# https://note.com/xaiondata/n/nf6f1b7fb081d
class PostgresConnection(asyncpg.connection.Connection):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._server_caps = asyncpg.connection.ServerCapabilities(
            advisory_locks=False,  # Interacting with locks using functions
            notifications=False,  # Listening related function
            plpgsql=False,  # Listening related function
            sql_reset=False,  # Using SET function
            sql_close_all=False,  # Cursor related function
            sql_copy_from_where=False,
            jit=False,
        )