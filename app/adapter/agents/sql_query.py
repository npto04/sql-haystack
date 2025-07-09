from typing import List, Optional

import pandas as pd
from haystack import component
from sqlalchemy.engine import Engine

from app.adapter.database.connection import engine


@component
class SQLQuery:
    def __init__(self, connection: Optional[Engine] = None):
        self.connection = connection if connection else engine.connect()

    @component.output_types(results=List[str], queries=List[str])
    def run(self, queries: List[str]):
        results = []
        for query in queries:
            result = pd.read_sql(query, self.connection)
            results.append(f"{result}")
        return {"results": results, "queries": queries}
