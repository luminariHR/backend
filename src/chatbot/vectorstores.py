from langchain_postgres.vectorstores import PGVector


class VectorDBConnectionManager:

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__init__()
        return cls.__instance

    def __init__(self):
        self.clients = {}

    @staticmethod
    def create_connection(username, password, host, port, db_name):
        connection = (
            f"postgresql+psycopg://{username}:{password}@{host}:{port}/{db_name}"
        )
        return connection

    def get_connection(
        self, username, password, host, port, db_name, collection_name, embeddings
    ):
        if db_name in self.clients:
            return self.clients[db_name]
        else:
            connection = self.create_connection(username, password, host, port, db_name)
            self.clients[db_name] = PGVector(
                embeddings=embeddings,
                collection_name=collection_name,
                connection=connection,
                use_jsonb=True,
            )
            return self.clients[db_name]
