from animethemes.schema import *
from posixpath import join as urljoin
import logging
import json
import requests

from animethemes import __version__

API_URL = "https://animethemes.dev/api"

class AnimeThemesError(Exception):
    """ Exception handler for AnimeThemes API Wrapper """
    pass

class InvalidResponse(AnimeThemesError):
    """ Raised on invalid response (eg. invalid json) """
    pass

class AnimeThemes(object):
    """
    docstring
    """
    
    def __init__(self, api_url=API_URL):
        """ Initializes AnimeThemes API wrapper """
        self.logger = logging.getLogger(__name__)
        self.api_url = api_url
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            # Why on earth does an API even need a browser's User-Agent string??
            # Probably an API bug, or something...
            "User-Agent":  "Mozilla/5.0 (X11; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0"
        }
    
    def _request(self, *endpoint, **kwargs):
        """ Requests an API endpoint """
        endpoint = (str(x) for x in endpoint) # make sure it doesn't complain about ints
        request_url = urljoin(self.api_url, *endpoint)
        res = requests.request(
            method="GET",
            url=request_url,
            headers=self.headers,
            **kwargs
        )
        res.raise_for_status()
        return res
    
    def _request_json(self, *endpoint, **kwargs):
        """ Same as `AnimeThemes._request()` but returns JSON """
        try:
            res = self._request(*endpoint, **kwargs)
            return res.json()
        except json.JSONDecodeError as val_err:
            raise InvalidResponse("Invalid JSON received", val_err) from val_err
    
    def _api_request(self, *endpoint, **kwargs):
        """ Parses query params and sends a request to the API """
        params = {}
        for k, v in kwargs.items():
            if not v:
                continue
            if isinstance(v, dict):
                params.update(self._nested_params(k, v))
            elif isinstance(v, list):
                params[k] = ','.join(v)
            else:
                params[k] = v
        return self._request_json(*endpoint, params=params)

    def _nested_params(self, name, nested):
        """ Transforms a dictionary into nested params accepted by the API """
        params = {}
        for k, v in nested.items():
            key = "{}[{}]".format(name, k)
            params[key] = ','.join(v) if isinstance(v, list) else v
        return params
    
    def search(self, query, limit=5, fields=[]):
        """ Returns relevant resources by search criteria
        
        Args:
            query (str): The search query
            limit (int): The number of each result to return. Accepts range 1-5.
            fields (list): A list of resources to include: anime, artists,
                entries, series, songs, synonyms, themes, videos
        """
        result = self._api_request('search',
            q=query,
            limit=limit,
            fields=fields
        )
        return SearchResult(self, result)
    
    def announcement(self, id, fields={}):
        """ Returns announcement information

        Args:
            id (int): The announcement id
            fields (dict): A dictionary of lists of fields by resource type
        """
        result = self._api_request("announcement", id, fields=fields)
        return Announcement(self, result)
    
    def anime(self, slug, include=[], fields={}):
        """ Returns anime information
        
        Args:
            slug (str): The anime's slug
            include (list): A list of included related resources:
                synonyms, series, themes, themes.entries,
                themes.entries.videos, themes.song, themes.song.artists,
                externalResources
            fields (dict): A dictionary of lists of fields by resource type
        """
        result = self._api_request("anime", slug,
            include=include, fields=fields)
        return Anime(self, result)
    
    def artist(self, slug, include=[], fields={}):
        """ Returns artist information
        
        Args:
            slug (str): The artist's slug
            include (list): A list of included related resources:
                songs, songs.themes, songs.themes.anime, members, groups,
                externalResources
            fields (dict): A dictionary of lists of fields by resource type
        """
        result = self._api_request("artist", slug,
            include=include, fields=fields)
        return Artist(self, result)
    
    def entry(self, id, include=[], fields={}):
        """ Returns entry from id
        
        Args:
            id (int): The entry id
            include (list): A list of included related resources:
                anime, themes, videos
            fields (dict): A dictionary of lists of fields by resource type
        """
        result = self._api_request("entry", id,
            include=include, fields=fields)
        return Entry(self, result)
    
    def resource(self, id, include=[], fields={}):
        """ Returns resource from id
        
        Args:
            id (int): The resource id
            include (list): A list of included related resources:
                anime, artists
            fields (dict): A dictionary of lists of fields by resource type
        """
        result = self._api_request("resource", id,
            include=include, fields=fields)
        return Resource(self, result)
    
    def series(self, slug, include=[], fields={}):
        """ Returns series information
        
        Args:
            slug (str): The series slug
            include (list): A list of included related resources:
                anime.synonyms, anime.themes, anime.themes.entries,
                anime.themes.entries.videos, anime.themes.song,
                anime.themes.song.artists, anime.externalResources
            fields (dict): A dictionary of lists of fields by resource type
        """
        result = self._api_request("series", slug,
            include=include, fields=fields)
        return Series(self, result)
    
    def song(self, id, include=[], fields={}):
        """ Returns song from id
        
        Args:
            id (int): The song id
            include (list): A list of included related resources:
                themes, themes.anime, artists
            fields (dict): A dictionary of lists of fields by resource type
        """
        result = self._api_request("song", id,
            include=include, fields=fields)
        return Song(self, result)
    
    def synonym(self, id, include=[], fields={}):
        """ Returns synonym from id
        
        Args:
            id (int): The synonym id
            include (list): A list of included related resources: anime
            fields (dict): A dictionary of lists of fields by resource type
        """
        result = self._api_request("synonym", id,
            include=include, fields=fields)
        return Synonym(self, result)
    
    def theme(self, id, include=[], fields={}):
        """ Returns theme from id
        
        Args:
            id (int): The theme id
            include (list): A list of included related resources:
                anime, entries, entries.videos, song, song.artists
            fields (dict): A dictionary of lists of fields by resource type
        """
        result = self._api_request("theme", id,
            include=include, fields=fields)
        return Theme(self, result)
    
    def video(self, basename, include=[], fields={}):
        """ Returns video info from basename
        
        Args:
            basename (str): The video's basename
            include (list): A list of included related resources:
                entries, entries.theme, entries.theme.anime
            fields (dict): A dictionary of lists of fields by resource type
        """
        result = self._api_request("video", basename,
            include=include, fields=fields)
        return Video(self, result)