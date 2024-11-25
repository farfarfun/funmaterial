from funsecret import read_secret
from requests import get


class PixabayAPI:
    """
    @brief Handle Pixabay video and image searches
    """

    def __init__(self, api_key=None, base_url="https://pixabay.com/api/"):
        """Constructor
        @param api_key str Your Pixabay API key.
        @see https://pixabay.com/en/accounts/register/ to register and get an API key.
        @param base_url: URL for Pixabay API
        """
        self.api_key = api_key or read_secret("funmaterial", "pixabay", "api_key")
        self.base_url = base_url

    def search_image(
        self,
        q,
        lang="en",
        id="",
        response_group="image_details",
        image_type="all",
        orientation="all",
        category="",
        min_width=0,
        min_height=0,
        editors_choice="false",
        safesearch="false",
        order="popular",
        page=1,
        per_page=20,
        callback="",
        pretty="false",
    ):
        """
        Image search
        @brief Search for Pixabay images using default arguments if no optional arguments supplied.
        @param q str A URL encoded search term. If omitted, all images are returned. This value may not exceed 100 characters.
        Example: "cat dog"
        Default: "yellow flower"

        @param lang str Language code of the language to be searched in.
        Accepted values: cs, da, de, en, es, fr, id, it, hu, nl, no, pl, pt, ro, sk, fi, sv, tr, vi, th, bg, ru, el, ja, ko, zh
        Default: "en"

        @param id str ID, hash ID, or a comma separated list of values for retrieving specific images.
        In a comma separated list, IDs and hash IDs cannot be used together.
        Default: " "

        @param response_group str Choose between retrieving high resolution images and image details.
        When selecting details, you can access images up to a dimension of 960 x 720 px.
        Accepted values: "image_details", "high_resolution" (requires permission)
        Default: "image_details"

        @param image_type str Filter results by image type.
        Accepted values: "all", "photo", "illustration", "vector"
        Default: "all"

        @param orientation str Whether an image is wider than it is tall, or taller than it is wide.
        Accepted values: "all", "horizontal", "vertical"
        Default: "all"

        @param category str  Filter results by category.
        Accepted values: fashion, nature, backgrounds, science, education, people, feelings, religion, health, places, animals, industry, food, computer, sports, transportation, travel, buildings, business, music
        Default: " "

        @param min_width int Minimum image width.
        Default: 0

        @param min_height int Minimum image height.
        Default: 0

        @param editors_choice bool Select images that have received an Editor's Choice award.
        Accepted values: "true", "false"
        Default: "false"

        @param safesearch bool A flag indicating that only images suitable for all ages should be returned.
        Accepted values: "true", "false"
        Default: "false"

        @param order str How the results should be ordered.
        Accepted values: "popular", "latest"
        Default: "popular"

        @param page int Returned search results are paginated. Use this parameter to select the page number.
        Default: 1

        @param per_page int Determine the number of results per page.
        Accepted values: 3 - 200
        Default: 20

        @param callback string JSONP callback function name
        Default: " "

        @param pretty bool Indent JSON output. This option should not be used in production.
        Accepted values: "true", "false"
        Default: "false"

        @return Image search data in JSON format.
        """

        payload = {
            "key": self.api_key,
            "q": q,
            "lang": lang,
            "id": id,
            "response_group": response_group,
            "image_type": image_type,
            "orientation": orientation,
            "category": category,
            "min_width": min_width,
            "min_height": min_height,
            "editors_choice": editors_choice,
            "safesearch": safesearch,
            "order": order,
            "page": page,
            "per_page": per_page,
            "callback": callback,
            "pretty": pretty,
        }

        resp = get(self.base_url, params=payload)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise ValueError(resp.text)

    def search_video(
        self,
        q,
        lang="en",
        id="",
        video_type="all",
        category="",
        min_width=0,
        min_height=0,
        editors_choice="false",
        safesearch="false",
        order="popular",
        page=1,
        per_page=20,
        callback="",
        pretty="false",
    ):
        """
        Video search
        @brief Search for Pixabay video using default arguments if no optional arguments supplied.
        @param q str A URL encoded search term. If omitted, all images are returned. This value may not exceed 100 characters.
        Example: "cat dog"
        Default: "yellow flower"

        @param lang str Language code of the language to be searched in.
        Accepted values: cs, da, de, en, es, fr, id, it, hu, nl, no, pl, pt, ro, sk, fi, sv, tr, vi, th, bg, ru, el, ja, ko, zh
        Default: "en"

        @param id str ID, hash ID, or a comma separated list of values for retrieving specific images.
        In a comma separated list, IDs and hash IDs cannot be used together.
        Default: " "

        @param video_type str Filter results by video type.
        Accepted values: "all", "film", "animation"
        Default: "all"

        @param category str  Filter results by category.
        Accepted values: fashion, nature, backgrounds, science, education, people, feelings, religion, health, places, animals, industry, food, computer, sports, transportation, travel, buildings, business, music
        Default: " "

        @param min_width int Minimum image width.
        Default: 0

        @param min_height int Minimum image height.
        Default: 0

        @param editors_choice bool Select images that have received an Editor's Choice award.
        Accepted values: "true", "false"
        Default: "false"

        @param safesearch bool A flag indicating that only images suitable for all ages should be returned.
        Accepted values: "true", "false"
        Default: "false"

        @param order str How the results should be ordered.
        Accepted values: "popular", "latest"
        Default: "popular"

        @param page int Returned search results are paginated. Use this parameter to select the page number.
        Default: 1

        @param per_page int Determine the number of results per page.
        Accepted values: 3 - 200
        Default: 20

        @param callback string JSONP callback function name
        Default: " "

        @param pretty bool Indent JSON output. This option should not be used in production.
        Accepted values: "true", "false"
        Default: "false"

        @return Video search data in JSON format.
        """

        payload = {
            "key": self.api_key,
            "q": q,
            "lang": lang,
            "id": id,
            "video_type": video_type,
            "category": category,
            "min_width": min_width,
            "min_height": min_height,
            "editors_choice": editors_choice,
            "safesearch": safesearch,
            "order": order,
            "page": page,
            "per_page": per_page,
            "callback": callback,
            "pretty": pretty,
        }

        resp = get(self.base_url + "videos/", params=payload)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise ValueError(resp.text)
