import requests
from funsecret import read_secret


class Unsplash:
    """
    api doc https://unsplash.com/documentation#search-users
    """

    def __init__(self, access_key=None, secret_key=None):
        self.access_key = access_key or read_secret(
            "funmaterial", "unsplash", "access_key"
        )
        self.secret_key = secret_key or read_secret(
            "funmaterial", "unsplash", "secret_key"
        )
        self.base_url = "https://api.unsplash.com/"

    def _get(self, uri, params):
        params["client_id"] = self.access_key
        return requests.get(f"{self.base_url}/{uri}", params=params).json()

    def list_photos(self, page=1, per_page=10):
        """
        :param page:	    Page number to retrieve. (Optional; default: 1)
        :param per_page:    Number of items per page. (Optional; default: 10)
        Returns:
        """
        payload = {
            "page": page,
            "per_page": per_page,
        }
        return self._get("photos", payload)

    def get_photo(self, photo_id):
        """
        :param photo_id:The photo’s ID. Required.
        Returns:
        """
        payload = {}
        return self._get("photos/{photo_id}".format(photo_id=photo_id), payload)

    def get_photo_random(
        self,
        collections=None,
        topics=None,
        username=None,
        query=None,
        orientation=None,
        content_filter="low",
        count=1,
    ):
        """
        :param collections:	Public collection ID(‘s) to filter selection. If multiple, comma-separated
        :param topics:	Public topic ID(‘s) to filter selection. If multiple, comma-separated
        :param username:	Limit selection to a single user.
        :param query:	Limit selection to photos matching a search term.
        :param orientation:	Filter by photo orientation. (Valid values: landscape, portrait, squarish)
        :param content_filter:	Limit results by content safety. Default: low. Valid values are low and high.
        :param count:	The number of photos to return. (Default: 1; max: 30)
        Returns:

        """
        payload = {
            "collections": collections,
            "topics": topics,
            "username": username,
            "query": query,
            "orientation": orientation,
            "content_filter": content_filter,
            "count": count,
        }
        return self._get("photos/random", payload)

    def search_photos(
        self,
        query,
        page=1,
        per_page=10,
        order_by="relevant",
        collections="",
        content_filter="low",
        color="",
        orientation="",
    ):
        """
        :param query:	        Search terms.
        :param page:	        Page number to retrieve. (Optional; default: 1)
        :param per_page:	    Number of items per page. (Optional; default: 10)
        :param order_by:	    How to sort the photos. (Optional; default: relevant). Valid values are latest and relevant.
        :param collections:	    Collection ID(‘s) to narrow search. Optional. If multiple, comma-separated.
        :param content_filter:	Limit results by content safety. (Optional; default: low). Valid values are low and high.
        :param color:	        Filter results by color. Optional. Valid values are: black_and_white, black, white, yellow, orange, red, purple, magenta, green, teal, and blue.
        :param orientation:	    Filter by photo orientation. Optional. (Valid values: landscape, portrait, squarish)
        Returns:

        """
        payload = {
            "query": query,
            "page": page,
            "per_page": per_page,
            "order_by": order_by,
            "collections": collections,
            "content_filter": content_filter,
            "color": color,
            "orientation": orientation,
        }
        return self._get("search/photos", params=payload)

    def search_collection(self, query, page=1, per_page=10):
        """
        :param query:	    Search terms.
        :param page:	    Page number to retrieve. (Optional; default: 1)
        :param per_page:	Number of items per page. (Optional; default: 10)
        Returns:

        """
        payload = {
            "query": query,
            "per_page": per_page,
            "page": page,
        }
        return self._get("search/collections", params=payload)

    def search_users(self, query, page=1, per_page=10):
        """
        :param query:	Search terms.
        :param page:	Page number to retrieve. (Optional; default: 1)
        :param per_page:	Number of items per page. (Optional; default: 10)
        Returns:

        """
        payload = {
            "query": query,
            "per_page": per_page,
            "page": page,
        }
        return self._get("search/users", params=payload)

    def list_topic(self, ids=None, page=1, per_page=10, order_by="position"):
        """
        :param ids:	        Limit to only matching topic ids or slugs. (Optional; Comma separated string)
        :param page:	    Page number to retrieve. (Optional; default: 1)
        :param per_page:	Number of items per page. (Optional; default: 10)
        :param order_by:	How to sort the topics. (Optional; Valid values: featured, latest, oldest, position; default: position)

        Returns:

        """
        payload = {
            "ids": ids,
            "page": page,
            "per_page": per_page,
            "order_by": order_by,
        }
        return self._get("topics", params=payload)

    def topic_detail(self, id=None, slug=None):
        """
        :param id:   The topics’s ID. Required.
        :param slug: The topics’s slug. Required.
        Args:
            id_or_slug:
        Returns:
        """
        payload = {}
        return self._get(f"topics/{id or slug}", params=payload)

    def topic_photos(
        self,
        id=None,
        slug=None,
        page=1,
        per_page=10,
        orientation=None,
        order_by="latest",
    ):
        """
        :param id:	        The topics’s ID. Required.
        :param slug:	    The topics’s slug. Required.
        :param page:	    Page number to retrieve. (Optional; default: 1)
        :param per_page:	Number of items per page. (Optional; default: 10)
        :param orientation:	Filter by photo orientation. (Optional; Valid values: landscape, portrait, squarish)
        :param order_by:	How to sort the photos. (Optional; Valid values: latest, oldest, popular; default: latest)
        Returns:

        """
        payload = {
            "page": page,
            "per_page": per_page,
            "orientation": orientation,
            "order_by": order_by,
        }
        return self._get(f"topics/{id or slug}/photos", params=payload)

    def stats_total(self):
        return self._get("stats/total", params={})

    def stats_month(self):
        return self._get("stats/month", params={})
