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
