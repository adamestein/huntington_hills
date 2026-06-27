import pymysql

pymysql.install_as_MySQLdb()

from django.db.backends.mysql.operations import DatabaseOperations


# PyMySQL exposes cursor._executed as text; Django's MySQLdb backend expects bytes.
def last_executed_query(self, cursor, sql, params):
    query = getattr(cursor, '_executed', None)
    if isinstance(query, bytes):
        query = query.decode(errors='replace')
    return query


DatabaseOperations.last_executed_query = last_executed_query
