from dateutil.parser import parse as parsedatetime
import requests

class AnimeThemesObject(object):
    """ Represents an AnimeThemes object """
    
    def __init__(self, client, data: dict, keys=[], dtkeys=['created_at', 'updated_at']):
        self._data = data
        self.client = client

        for key in keys:
            setattr(self, key, data.get(key))
        
        for key in dtkeys:
            if data.get(key):
                parsed_date = parsedatetime(data[key])
                setattr(self, key, parsed_date)

        if isinstance(self._data.get('anime'), dict):
            self.anime = Anime(client, data.get('anime', {}))
        
        if isinstance(self._data.get('theme'), dict):
            self.anime = Theme(client, data.get('theme', {}))
        
        if isinstance(self._data.get('song'), dict):
            self.anime = Song(client, data.get('song', {}))
        
        self._set_list_attrib('songs', Song)
        self._set_list_attrib('anime', Anime)
        self._set_list_attrib('themes', Theme)
        self._set_list_attrib('videos', Video)
        self._set_list_attrib('series', Series)
        self._set_list_attrib('entries', Entry)
        self._set_list_attrib('artists', Artist)
        self._set_list_attrib('synonyms', Synonym)
        self._set_list_attrib('resources', Resource)
        self._set_list_attrib('announcements', Announcement)
    
    def _set_list_attrib(self, key, atcls):
        """ Sets and objectifies lists in data as attributes if they're not None """
        data_val = self._data.get(key)
        if data_val is not None and isinstance(data_val, list):
            setattr(self, key, [atcls(self.client, x) for x in data_val])

class Announcement(AnimeThemesObject):
    """ Announcement Resource """
    
    def __init__(self, client, data: dict):
        super().__init__(client, data, ['id', 'content'])

class Anime(AnimeThemesObject):
    """ Anime Resource """
    
    def __init__(self, client, data: dict):
        super().__init__(client, data, [
            'id', 'name', 'slug', 'year', 'season', 'synopsis', 'cover'])

class Artist(AnimeThemesObject):
    """ Artist Resource """
    
    def __init__(self, client, data: dict):
        super().__init__(client, data, ['id', 'name', 'slug'])

        self.members   = data.get('members', []) # undocumented?
        self.groups    = data.get('groups' , []) # undocumented?

class Entry(AnimeThemesObject):
    """ Entry Resource """
    
    def __init__(self, client, data: dict):
        super().__init__(client, data,
            ['id', 'version', 'episodes', 'nsfw', 'spoiler', 'notes'])

class Resource(AnimeThemesObject):
    """ External Resource """
    
    def __init__(self, client, data: dict):
        super().__init__(client, data,
            ['id', 'external_id', 'link', 'site', 'as'])

class Series(AnimeThemesObject):
    """ Series Resource """
    
    def __init__(self, client, data: dict):
        super().__init__(client, data, ['id', 'name', 'slug'])

class Song(AnimeThemesObject):
    """ Song Resource """

    def __init__(self, client, data: dict):
        super().__init__(client, data, ['id', 'title'])

class Synonym(AnimeThemesObject):
    """ Synonym Resource """
    
    def __init__(self, client, data: dict):
        super().__init__(client, data, ['id', 'text'])

class Theme(AnimeThemesObject):
    """ Theme Resource """
    
    def __init__(self, client, data: dict):
        super().__init__(client, data,
            ['id', 'type', 'sequence', 'group', 'slug'])

class Video(AnimeThemesObject):
    """ Video Resource """
    
    def __init__(self, client, data: dict):
        super().__init__(client, data, 
            ['id', 'basename', 'filename', 'path', 'resolution', 'nc',
            'subbed', 'lyrics', 'uncen', 'source', 'overlap', 'link'])

class SearchResult(AnimeThemesObject):
    """ Search result """
    
    def __init__(self, client, data: dict):
        super().__init__(client, data)

class PagedResult(AnimeThemesObject):
    """ Represents a result containing page information """

    def __init__(self, client, data: dict):
        super().__init__(client, data)
        self.current_page = data.get('meta', {}).get('current_page')
        self.per_page = data.get('meta', {}).get('per_page')
        self.from_result = data.get('meta', {}).get('from')
        self.to_result = data.get('meta', {}).get('to')
    
    def first_page(self):
        """ Return a `PagedResult` of the first page or `None` """
        page_link = self._data.get('links', {}).get('first')
        if not page_link:
            return None
        page_data = requests.get(page_link, headers=self.client.headers)
        page_data.raise_for_status()
        return PagedResult(self.client, page_data.json())
    
    def next_page(self):
        """ Return a `PagedResult` of the next page or `None` if no next page """
        page_link = self._data.get('links', {}).get('next')
        if not page_link:
            return None
        page_data = requests.get(page_link, headers=self.client.headers)
        page_data.raise_for_status()
        return PagedResult(self.client, page_data.json())
    
    def prev_page(self):
        """ Return a `PagedResult` of the previous page or `None` if no previous page """
        page_link = self._data.get('links', {}).get('prev')
        if not page_link:
            return None
        page_data = requests.get(page_link, headers=self.client.headers)
        page_data.raise_for_status()
        return PagedResult(self.client, page_data.json())
    
    def last_page(self):
        """ Return a `PagedResult` of the last page or `None` if no last page """
        page_link = self._data.get('links', {}).get('last')
        if not page_link:
            return None
        page_data = requests.get(page_link, headers=self.client.headers)
        page_data.raise_for_status()
        return PagedResult(self.client, page_data.json())

class SeasonResult(AnimeThemesObject):
    """ Represents a list of anime for each season """
    
    def __init__(self, client, data: dict):
        super().__init__(client, data)
        for season in ['fall', 'spring', 'summer', 'winter']:
            setattr(self, season, [Anime(client, x) for x in data.get(season, {})])
        
        self.no_season = [Anime(client, x) for x in data.get('', {})]