"""This module provides functionality for postgres interactions."""

import os
import asyncpg

from core.decorators import aioshield, aiowait


class PoolManager:
    """Class that provides postgres executions via pool manager."""

    def __init__(self):
        """Initialize connections pool manager from env configs."""
        self.pool = None

        self.dsn = os.environ.get("POSTGRES_DSN")
        self.host = os.environ.get("POSTGRES_HOST")
        self.port = os.environ.get("POSTGRES_PORT")

        self.user = os.environ["POSTGRES_USER"]
        self.password = os.environ["POSTGRES_PASSWORD"]
        self.database = os.environ["POSTGRES_DB"]

        self.connection_min_size = os.environ.get("POSTGRES_CONNECTION_MIN_SIZE", 10)
        self.connection_max_size = os.environ.get("POSTGRES_CONNECTION_MAX_SIZE", 10)

    @classmethod
    async def create(cls):
        """Create and initialize pool manager for postgres connections."""
        instance = cls()
        instance.pool = await asyncpg.create_pool(
            dsn=instance.dsn,
            host=instance.host,
            port=instance.port,
            database=instance.database,
            user=instance.user,
            password=instance.password,
            min_size=instance.connection_min_size,
            max_size=instance.connection_max_size
        )

        return instance

    @aiowait(timeout=10)
    async def close(self):
        """
        Close gracefully all connections in the pool with a timeout.
        Errors raised will cause immediate pool termination.
        """
        await self.pool.close()

    @aioshield
    async def execute(self, query, *query_args, timeout=5.0):
        """Execute an SQL command (or commands)."""
        async with self.pool.acquire() as con:
            return await con.execute(query, *query_args, timeout=timeout)

    async def fetch(self, query, timeout=5.0):
        """Run a query and return the results as a list."""
        async with self.pool.acquire() as con:
            return await con.fetch(query, timeout=timeout)

    async def fetchone(self, query, timeout=5.0):
        """Run a query and return the first row."""
        async with self.pool.acquire() as con:
            return await con.fetchrow(query, timeout=timeout)
