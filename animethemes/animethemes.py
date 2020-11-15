from animethemes.schema import *
from posixpath import join as urljoin
import logging
import json
import requests

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
        """Initializes AnimeThemes API wrapper

        Args:
            api_url (str, optional): URL of the API location. Defaults to
                "https://animethemes.dev/api".
        """
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
    
    def _paged_request(self, *endpoint, page=None, per_page=None, **kwargs):
        """ Same as `AnimeThemes._api_request()` but handles page params better """
        page = {
            'number': page,
            'size': per_page
        }
        return self._api_request(*endpoint, page=page, **kwargs)

    def _nested_params(self, name, nested):
        """ Transforms a dictionary into nested params accepted by the API """
        params = {}
        for k, v in nested.items():
            if not v:
                continue
            key = "{}[{}]".format(name, k)
            params[key] = ','.join(v) if isinstance(v, list) else v
        return params
    
    def search(self, query, limit=5, fields=[]):
        """ Returns relevant resources by search criteria
        
        Args:
            query (str): The search query
            limit (int, optional): The number of each result to return.
                Accepts range 1-5.
            fields (list, optional): A list of resources to include:
                anime, artists, entries, series, songs, synonyms, themes, videos
        """
        result = self._api_request('search',
            q=query,
            limit=limit,
            fields=fields
        )
        return SearchResult(self, result)
    
    def announcements(self, **kwargs):
        """ Returns a PagedResult of Announcement

        Args:
            page (int, optional): The page number of resources to return
            per_page (int, optional): The number of resources to return per page
            sort (str, optional): Sort by fields:
                announcement_id, created_at, updated_at
            fields (dict, optional): A dictionary of lists of fields by
                resource type

        Returns:
            PagedResult: A PagedResult containing Announcement objects
        """
        result = self._paged_request("announcement", **kwargs)
        return PagedResult(self, result)
    
    def announcement(self, id, fields={}):
        """ Returns announcement information

        Args:
            id (int): The announcement id
            fields (dict, optional): A dictionary of lists of fields by
                resource type
        """
        result = self._api_request("announcement", id, fields=fields)
        return Announcement(self, result)
    
    def animes(self, **kwargs):
        """Returns a PagedResult of Anime

        Args:
            include (list, optional): A list of included related resources:
                synonyms, series, themes, themes.entries, themes.entries.videos,
                themes.song, themes.song.artists, externalResources
            year (int, optional): Filter anime by year
            season (str, optional): Filter anime by season:
                Winter, Spring, Summer, Fall
            page (int, optional): The page number of resources to return
            per_page (int, optional): The number of resources to return per page
            sort (str, optional): Sort by fields:
                anime_id, created_at, updated_at, slug, name, year, season
            fields (dict, optional): A dictionary of lists of fields by
                resource type

        Returns:
            PagedResult: A PagedResult containing Anime objects
        """
        fparam = {
            'year': kwargs.get('year'),
            'season': kwargs.get('season')
        }
        result = self._paged_request("anime", filter=fparam, **kwargs)
        return PagedResult(self, result)

    def anime(self, slug, include=[], fields={}):
        """ Returns anime information
        
        Args:
            slug (str): The anime's slug
            include (list, optional): A list of included related resources:
                synonyms, series, themes, themes.entries,
                themes.entries.videos, themes.song, themes.song.artists,
                externalResources
            fields (dict, optional): A dictionary of lists of fields by
                resource type
        """
        result = self._api_request("anime", slug,
            include=include, fields=fields)
        return Anime(self, result)
    
    def years(self):
        """ Returns a list of unique years """
        return self._request_json("year")
    
    def year(self, year, **kwargs):
        """ Returns a SeasonResult listing of Anime in the given year by season

        Args:
            include (list, optional): A list of included related resources:
                synonyms, series, themes, themes.entries, themes.entries.videos,
                themes.song, themes.song.artists, externalResources
        """
        result = self._api_request("year", year, **kwargs)
        return SeasonResult(self, result)
    
    def artists(self, **kwargs):
        """ Returns a PagedResult of Artist

        Args:
            include (list, optional): A list of included related resources:
                songs, songs.themes, songs.themes.anime, members, groups,
                externalResources
            page (int, optional): The page number of resources to return
            per_page (int, optional): The number of resources to return per page
            sort (str, optional): Sort by fields:
                artist_id, created_at, updated_at, slug, name
            fields (dict, optional): A dictionary of lists of fields by
                resource type

        Returns:
            PagedResult: A PagedResult containing Artist objects
        """
        result = self._paged_request("artist", **kwargs)
        return PagedResult(self, result)
    
    def artist(self, slug, include=[], fields={}):
        """ Returns artist information
        
        Args:
            slug (str): The artist's slug
            include (list, optional): A list of included related resources:
                songs, songs.themes, songs.themes.anime, members, groups,
                externalResources
            fields (dict, optional): A dictionary of lists of fields by
                resource type
        """
        result = self._api_request("artist", slug,
            include=include, fields=fields)
        return Artist(self, result)
    
    def entries(self, **kwargs):
        """ Returns a PagedResult of Entry

        Args:
            include (list, optional): A list of included related resources:
                anime, themes, videos
            version (int, optional): Filter entries by version
            nsfw (bool, optional): Filter entries by NSFW
            spoiler (bool, optional): Filter entries by spoiler
            page (int, optional): The page number of resources to return
            per_page (int, optional): The number of resources to return per page
            sort (str, optional): Sort by fields:
                entry_id, created_at, updated_at, version, nsfw, spoiler,
                theme_id
            fields (dict, optional): A dictionary of lists of fields by
                resource type

        Returns:
            PagedResult: A PagedResult containing Entry objects
        """
        fparam = {
            'verison': kwargs.get('version'),
            'nsfw': kwargs.get('nsfw'),
            'spoilter': kwargs.get('spoiler')
        }
        result = self._paged_request("entry", filter=fparam, **kwargs)
        return PagedResult(self, result)
    
    def entry(self, id, include=[], fields={}):
        """ Returns entry from id
        
        Args:
            id (int): The entry id
            include (list, optional): A list of included related resources:
                anime, themes, videos
            fields (dict, optional): A dictionary of lists of fields by
                resource type
        """
        result = self._api_request("entry", id,
            include=include, fields=fields)
        return Entry(self, result)
    
    def resources(self, **kwargs):
        """ Returns a PagedResult of Resource

        Args:
            include (list, optional): A list of included related resources:
                anime, artists
            type (str, optional): Filter resources by type:
                official_site, twitter, anidb, anilist, anime_planet, ann, 
                kitsu, mal, wiki
            page (int, optional): The page number of resources to return
            per_page (int, optional): The number of resources to return per page
            sort (str, optional): Sort by fields:
                resource_id, created_at, updated_at, type, link, external_id
            fields (dict, optional): A dictionary of lists of fields by
                resource type

        Returns:
            PagedResult: A PagedResult containing Resource objects
        """
        result = self._paged_request("resource", **kwargs)
        return PagedResult(self, result)
    
    def resource(self, id, include=[], fields={}):
        """ Returns resource from id
        
        Args:
            id (int): The resource id
            include (list, optional): A list of included related resources:
                anime, artists
            fields (dict, optional): A dictionary of lists of fields by
                resource type
        """
        result = self._api_request("resource", id,
            include=include, fields=fields)
        return Resource(self, result)
    
    def series(self, slug=None, **kwargs):
        """ Returns a single series information if slug is given, otherwise
            returns a PagedResult of series
        
        Args:
            slug (str): The series slug (for a single series)
            include (list, optional): A list of included related resources:
                anime.synonyms, anime.themes, anime.themes.entries,
                anime.themes.entries.videos, anime.themes.song,
                anime.themes.song.artists, anime.externalResources
            fields (dict, optional): A dictionary of lists of fields by
                resource type
            page (int, optional): For paged results. The page number of
                resources to return
            per_page (int, optional): For paged results. The number of
                resources to return per page
            sort (str, optional): For paged results. Sort by fields:
                series_id, created_at, updated_at, slug, name
        
        Returns:
            An instance of `Series` if slug is provided, or `PagedResult` if
            otherwise
        """
        if not slug:
            result = self._paged_request("series", **kwargs)
            return PagedResult(self, result)
        result = self._api_request("series", slug, **kwargs)
        return Series(self, result)
    
    def songs(self, **kwargs):
        """ Returns a PagedResult of Song

        Args:
            include (list, optional): A list of included related resources:
                themes, themes.anime, artists
            page (int, optional): The page number of resources to return
            per_page (int, optional): The number of resources to return per page
            sort (str, optional): Sort by fields:
                song_id, created_at, updated_at, title
            fields (dict, optional): A dictionary of lists of fields by
                resource type

        Returns:
            PagedResult: A PagedResult containing Song objects
        """
        result = self._paged_request("song", **kwargs)
        return PagedResult(self, result)
    
    def song(self, id, include=[], fields={}):
        """ Returns song from id
        
        Args:
            id (int): The song id
            include (list, optional): A list of included related resources:
                themes, themes.anime, artists
            fields (dict, optional: A dictionary of lists of fields by
                resource type
        """
        result = self._api_request("song", id,
            include=include, fields=fields)
        return Song(self, result)
    
    def synonyms(self, **kwargs):
        """ Returns a PagedResult of Synonym

        Args:
            include (list, optional): A list of included related resources:
                anime
            page (int, optional): The page number of resources to return
            per_page (int, optional): The number of resources to return per page
            sort (str, optional): Sort by fields:
                synonym_id, created_at, updated_at, text, anime_id
            fields (dict, optional): A dictionary of lists of fields by
                resource type

        Returns:
            PagedResult: A PagedResult containing Synonym objects
        """
        result = self._paged_request("synonym", **kwargs)
        return PagedResult(self, result)

    def synonym(self, id, include=[], fields={}):
        """ Returns synonym from id
        
        Args:
            id (int): The synonym id
            include (list, optional): A list of included related resources: anime
            fields (dict, optional): A dictionary of lists of fields by
                resource type
        """
        result = self._api_request("synonym", id,
            include=include, fields=fields)
        return Synonym(self, result)
    
    def themes(self, **kwargs):
        """ Returns a PagedResult of Theme

        Args:
            include (list, optional): A list of included related resources:
                anime, entries, entries.videos, song, song.artists
            type (str, optional): Filter themes by type: OP, ED
            sequence (int, optional): Filter themes by sequence
            group (str, optional): Filter themes by group
            page (int, optional): The page number of resources to return
            per_page (int, optional): The number of resources to return per page
            sort (str, optional): Sort by fields:
                theme_id, created_at, updated_at, group, type, sequence, slug,
                anime_id, song_id
            fields (dict, optional): A dictionary of lists of fields by
                resource type

        Returns:
            PagedResult: A PagedResult containing Theme objects
        """
        fparam = {
            'type': kwargs.get('type'),
            'sequence': kwargs.get('sequence'),
            'group': kwargs.get('group')
        }
        result = self._paged_request("theme", filter=fparam, **kwargs)
        return PagedResult(self, result)
    
    def theme(self, id, include=[], fields={}):
        """ Returns theme from id
        
        Args:
            id (int): The theme id
            include (list, optional): A list of included related resources:
                anime, entries, entries.videos, song, song.artists
            fields (dict, optional): A dictionary of lists of fields by
                resource type
        """
        result = self._api_request("theme", id,
            include=include, fields=fields)
        return Theme(self, result)
    
    def videos(self, **kwargs):
        """ Returns a PagedResult of Video

        Args:
            include (list, optional): A list of included related resources:
                entries, entries.theme, entries.theme.anime
            resolution (int, optional): Filter videos by resolution
            nc (bool, optional): Filter videos by NC
            subbed (bool, optional): Filter by subtitled videos
            lyrics (bool, optional): Filter by videos containing lyrics
            source (str, optional): Filter by source: WEB, RAW, BD, DVD, VHS
            overlap (str, optional): Filter by type of overlap:
                None, Trans, Over
            page (int, optional): The page number of resources to return
            per_page (int, optional): The number of resources to return per page
            sort (str, optional): Sort by fields:
                video_id, created_at, updated_at, filename, path, basename,
                resolution, nc, subbed, lyrics, uncen, source & overlap
            fields (dict, optional): A dictionary of lists of fields by
                resource type

        Returns:
            PagedResult: A PagedResult containing Video objects
        """
        result = self._paged_request("video", **kwargs)
        return PagedResult(self, result)

    def video(self, basename, include=[], fields={}):
        """ Returns video info from basename
        
        Args:
            basename (str): The video's basename
            include (list, optional): A list of included related resources:
                entries, entries.theme, entries.theme.anime
            fields (dict, optional): A dictionary of lists of fields by
                resource type
        """
        result = self._api_request("video", basename,
            include=include, fields=fields)
        return Video(self, result)