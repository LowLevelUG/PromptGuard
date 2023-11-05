from os import getenv

from certifi.core import where
from pydantic.types import Json
from pymongo.collection import Collection
from pymongo.cursor import Cursor
from pymongo.database import Database
from pymongo.mongo_client import MongoClient
from pymongo.results import (DeleteResult, InsertManyResult, InsertOneResult,
                             UpdateResult)


class DB(object):
    """
    A simple database handler for MongoDB using PyMongo.

    Parameters
    ----------
    uri: `str` | `None`
        The MongoDB connection URI. If not provided, it will use the 'MONGO_CLIENT' environment variable. Default is None.

    Attributes
    ----------
    client: `MongoClient`
        The MongoDB client instance.
    db: `Database`
        The MongoDB database instance.
    table: `Collection`
        The MongoDB collection instance.
    """

    __slots__ = ("client", "db", "table")

    def __init__(self, uri: str | None = None) -> None:
        """
        Initialize the DB class and establish a connection to the MongoDB database.

        Parameters
        ----------
        uri: `str` | `None`
            The MongoDB connection URI. If not provided, it will use the 'MONGO_CLIENT' environment variable. Default is None.
        """

        if uri is None:
            uri = getenv("MONGO_CLIENT")

        db_env: str = str(getenv("DATABASE"))
        table_env: str = str(getenv("TABLE"))

        self.client: MongoClient = MongoClient(
            uri, uuidRepresentation="standard", tlsCAFile=where()
        )
        self.db: Database = self.client.get_database(db_env)
        self.table: Collection = self.db[table_env]

    def insert_one_data(self, data: dict | Json) -> str:
        """
        Insert a single document into the MongoDB collection.

        Parameters
        ----------
        data: `dict`
            The data to be inserted into the collection.

        Returns
        -------
        `str`
            The ObjectId of the inserted document.
        """
        result: InsertOneResult = self.table.insert_one(data)
        return str(result.inserted_id)

    def insert_data(self, data: list[dict] | Json) -> list[str] | Json:
        """
        Insert multiple documents into the MongoDB collection.

        Parameters
        ----------
        data: `list[dict]`
            A list of data (documents) to be inserted into the collection.

        Returns
        -------
        `list[str]`
            A list of ObjectIds for the inserted documents.
        """

        result: InsertManyResult = self.table.insert_many(data)
        return [str(oid) for oid in result.inserted_ids]

    def find(self) -> Cursor:
        """
        Find all documents in the MongoDB collection.

        Returns
        -------
        `Cursor`
            A cursor object containing all the documents in the collection.
        """

        data: Cursor = self.table.find()
        return data

    def find_one_data(self, query: dict | Json) -> dict | Json | None:
        """
        Find a single document in the MongoDB collection based on the given query.

        Parameters
        ----------
        query: `dict`
            The query to find the document.

        Returns
        -------
        `dict` | `None`
            The matched document or None if not found.
        """

        data: dict | None = self.table.find_one(query)
        return data

    def find_data(self, query: dict | Json) -> list[dict] | Json:
        """
        Find documents in the MongoDB collection based on the given query.

        Parameters
        ----------
        query: `dict`
            The query to filter the documents.

        Returns
        -------
        `list[dict]`
            A list of documents matching the query.
        """

        data: Cursor = self.table.find(query)
        return list(data)

    def update_one_data(self, query: dict | Json, update_data: dict | Json) -> bool:
        """
        Update a single document in the MongoDB collection based on the given query.

        Parameters
        ----------
        query: `dict`
            The query to find the document to update.

        update_data: `dict`
            The data to update the matched document.

        Returns
        -------
        `bool`
            True if the document was successfully updated, False otherwise.
        """

        result: UpdateResult = self.table.update_one(query, {"$set": update_data})
        return result.modified_count > 0

    def update_data(self, query: dict | Json, update_data: dict | Json) -> bool:
        """
        Update multiple documents in the MongoDB collection based on the given query.

        Parameters
        ----------
        query: `dict`
            The query to find the documents to update.

        update_data: `dict`
            The data to update the matched documents.

        Returns
        -------
        `bool`
            True if at least one document was successfully updated, False otherwise.
        """

        result: UpdateResult = self.table.update_many(query, {"$set": update_data})
        return result.modified_count > 0

    def delete_one_data(self, query: dict | Json) -> bool:
        """
        Delete a single document from the MongoDB collection based on the given query.

        Parameters
        ----------
        query: `dict`
            The query to find the document to delete.

        Returns
        -------
        `bool`
            True if the document was successfully deleted, False otherwise.
        """

        result: DeleteResult = self.table.delete_one(query)
        return result.deleted_count > 0

    def delete_data(self, query: dict | Json) -> bool:
        """
        Delete multiple documents from the MongoDB collection based on the given query.

        Parameters
        ----------
        query: `dict`
            The query to find the documents to delete.

        Returns
        -------
        `bool`
            True if at least one document was successfully deleted, False otherwise.
        """

        result: DeleteResult = self.table.delete_many(query)
        return result.deleted_count > 0

    def close(self) -> None:
        """
        Closes the MongoDB client connection.
        """

        self.client.close()


# Create an instance of the DB class
db: DB = DB()
