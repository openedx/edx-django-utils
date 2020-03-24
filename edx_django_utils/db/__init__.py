"""
Utilities for working effectively with databases in django.

read_replica: Tools for making queries from the read-replica.
"""

from .read_replica import (
    ReadReplicaRouter,
    read_queries_only,
    read_replica_or_default,
    use_read_replica_if_available,
    write_queries
)
