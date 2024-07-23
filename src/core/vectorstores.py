from langchain_community.vectorstores import SupabaseVectorStore


class VectorDBConnectionManager:

    __instance = None

    def __new__(cls):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls.__instance.__init__()
        return cls.__instance

    def __init__(self):
        self.clients = {}

    def get_connection(
        self,
        db_name,
        client,
        embeddings,
        table_name="documents",
        query_name="match_documents",
    ) -> SupabaseVectorStore:
        if db_name in self.clients:
            return self.clients[db_name]
        else:
            self.clients[db_name] = SupabaseVectorStore(
                embedding=embeddings,
                client=client,
                table_name=table_name,
                query_name=query_name,
                chunk_size=1000,
            )
            return self.clients[db_name]
