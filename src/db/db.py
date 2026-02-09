#!/usr/bin/python3

from json import load, dumps
from typing import Any

class GitRepoStatsDB:
    """
    Manages the persistence of repository statistics in a JSON database.

    This class provides methods to read and update statistics like views and clones,
    ensuring they are saved across application runs.
    """

    def __init__(self):
        """
        Initializes the database by loading data from 'src/db/db.json'.
        """
        self.__db = None

        self.views = None
        self.views_start = None
        self.views_end = None

        self.clones = None
        self.clones_start = None
        self.clones_end = None

        try:
            with open("src/db/db.json", "r") as db:
                self.__db = load(db)
        except FileNotFoundError:
            # Fallback for different execution contexts
            with open("../src/db/db.json", "r") as db:
                self.__db = load(db)

        self.views = int(self.__db['views']['count'])
        self.views_from_date = self.__db['views']['from']
        self.views_to_date = self.__db['views']['to']

        self.clones = int(self.__db['clones']['count'])
        self.clones_from_date = self.__db['clones']['from']
        self.clones_to_date = self.__db['clones']['to']

    def __update_db(self) -> None:
        """
        Saves the current state of the database to the JSON file.
        """
        try:
            with open("src/db/db.json", "w") as db:
                db.write(dumps(self.__db, indent=2))
        except FileNotFoundError:
            with open("../src/db/db.json", "w") as db:
                db.write(dumps(self.__db, indent=2))

    def set_views_count(self, count: Any) -> None:
        """
        Updates the view count in the database.

        :param count: The new view counts.
        """
        self.views = int(count)
        self.__db['views']['count'] = str(self.views)
        self.__update_db()

    def set_views_from_date(self, date: str) -> None:
        """
        Updates the starting date for views in the database.

        :param date: The starting date string.
        """
        self.views_from_date = date
        self.__db['views']['from'] = self.views_from_date
        self.__update_db()

    def set_views_to_date(self, date: str) -> None:
        """
        Updates the end date for views in the database.

        :param date: The end date string.
        """
        self.views_to_date = date
        self.__db['views']['to'] = self.views_to_date
        self.__update_db()

    def set_clones_count(self, count: Any) -> None:
        """
        Updates the clone count in the database.

        :param count: The new clone count.
        """
        self.clones = int(count)
        self.__db['clones']['count'] = str(self.clones)
        self.__update_db()

    def set_clones_from_date(self, date: str) -> None:
        """
        Updates the starting date for clones in the database.

        :param date: The starting date string.
        """
        self.clones_from_date = date
        self.__db['clones']['from'] = self.clones_from_date
        self.__update_db()

    def set_clones_to_date(self, date: str) -> None:
        """
        Updates the end date for clones in the database.

        :param date: The end date string.
        """
        self.clones_to_date = date
        self.__db['clones']['to'] = self.clones_to_date
        self.__update_db()
