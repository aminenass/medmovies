from cachetools import TTLCache
from typing import Any, Dict, List, Optional
import aiohttp
import asyncio
from functools import wraps
from datetime import date
from django.conf import settings


# Initialize a cache with a 10-minute TTL 
cache = TTLCache(maxsize=100, ttl=600)

headers = {
    "accept": "application/json",
    "Authorization": f'Bearer {settings.SECRET_TOKEN}'
}

BASE_URL = "https://api.themoviedb.org/3"
    
# Async version of cached decorator (requires async-compatible cache)
def async_cached(cache):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{args}:{kwargs}"
            if key in cache:
                return cache[key]
            result = await func(*args, **kwargs)
            cache[key] = result
            return result
        return wrapper
    return decorator

async def build_url(endpoint: str, params: Optional[Dict[str, Any]] = None) -> str:
    """Async-compatible URL builder"""
    params = params or {}
    query = "&".join(
        f"{k}={v}" for k, v in params.items() 
        if v is not None and not isinstance(v, (list, dict))
    )
    return f"{BASE_URL}/{endpoint}?{query}" if query else f"{BASE_URL}/{endpoint}"

@async_cached(cache)  # Use async-compatible caching
async def fetch_data(url: str) -> List[Dict[str, Any]]:
    """Async data fetcher with error handling"""
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, headers=headers, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("results", [])
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            print(f"Error fetching {url}: {e}")
            return []

# Async Movie endpoints
async def movies(page: int , genre_ids : List[int] = None) -> List[Dict[str, Any]] :
    
    base_url = "discover/movie" if genre_ids else "trending/movie/day"

    params = {
        "include_adult": "false",
        "language": "en-US",
        "page": page, 
        "with_genres": ",".join(map(str, genre_ids)) if genre_ids else None
    }
    url = await build_url(base_url, params)
    return await fetch_data(url)

async def trailer(movie_id: int , types : str = None) -> List[Dict[str, Any]]:
    try:
        # First try movies endpoint  
        url = await build_url(f"{types}/{movie_id}/videos")
        data = await fetch_data(url)
        if data :
            return  [video for video in data if ( video["site"] == "YouTube" and video["type"] == "Trailer") or (video["site"] == "YouTube" and video["type"] == "Teaser")  ]
      
    except Exception as e:
        pass  # Ignore error and try TV endpoint
    
    # If movies failed or had no results, try TV
    try:
        url = await build_url(f"tv/{movie_id}/videos")
        data = await fetch_data(url)
        return  [video for video in data if ( video["site"] == "YouTube" and video["type"] == "Trailer") or (video["site"] == "YouTube" and video["type"] == "Teaser")  ]
    except Exception as e:
        return []
        
# Async TV Show endpoints
async def tv_shows(page: int , category: str = None ,genre_ids: List[int] = None ) -> List[Dict[str, Any]]:
    base_url = "discover/tv" if category else "trending/tv/day"
    
    params = {
        
        "language": "en-US",
        "page": page,
        "include_video": "true"
        
    }
    
    if category:
        category_filters = {
            "all": {},
            "korean": {"with_original_language": "ko"},
            "turkish": {"with_original_language": "tr"},
            "french": {"with_original_language": "fr"},
            "anime": {"with_genres":  "16", "with_original_language": "ja"},
        }
    # .join(map(str, genre_ids))
        if category.lower() in category_filters:
            params.update(category_filters[category.lower()])
    # Add genre filter if provided
    if genre_ids : 
            params["with_genres"] = ",".join(map(str, genre_ids)) 
        

    url = await build_url(base_url, params)
    return await fetch_data(url)

async def drama(page: int, language_code: str ) -> List[Dict[str, Any]]:
    params = {
        "air_date.gte": date.today(),
        "page": page,
        "language": "en-US",
        "with_original_language": language_code,
        "sort_by": "popularity.desc",
    }
   
    url = await build_url("discover/tv", params)
    return await fetch_data(url)

async def anime(page: int, genre_id: Optional[int] = None) -> List[Dict[str, Any]]:
    params = {
        "air_date.gte": date.today(),
        "page": page,
        "language": "en-US",
        "with_genres": f"16,{genre_id}" if genre_id else "16",
        "with_original_language": "ja"
    }
    url = await build_url("discover/tv", params)
    return await fetch_data(url)

# Async Genre endpoint
async def genre() -> List[Dict[str, Any]]:
    try:
        url = await build_url("genre/tv/list", {"language": "en"})
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=10) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("genres", [])
    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        print(f"Error fetching genres: {e}")
        return []
    
async def search_media(page: int, query_search: str, media_type: str = 'both'):
    try:
        results = []
        async with aiohttp.ClientSession() as session:
            # Create a list of media types to search
            search_types = []
            if media_type in ['both', 'movie']:
                search_types.append('movie')
            if media_type in ['both', 'tv']:
                search_types.append('tv')

            # Create tasks for all search types
            tasks = []
            for st in search_types:
                url = await build_url(f"search/{st}")
                params = {
                    "query": query_search,
                    "include_adult": "false",
                    "language": "en-US", 
                    "page": page,
                }
                tasks.append(
                    session.get(url, headers=headers, params=params, timeout=10)
                )

            # Process all responses
            responses = await asyncio.gather(*tasks)
            json_data = await asyncio.gather(*(r.json() for r in responses))

            results = [item for data in json_data for item in data.get("results", [])]
            
            total_pages = int(sum([data.get("total_pages") for data in json_data]) * 0.7)
            
            # Sort results by popularity
            results.sort(key=lambda x: x.get('popularity', 0), reverse=True)
            
        return results,total_pages

    except Exception as e:
        print(f"Search error: {str(e)}")
        return [] 
    

async def get_details_by_id(item_id: int, types: str):
    try:
        url = await build_url(f"{types}/{item_id}")
        url_credits = await build_url(f"{types}/{item_id}/credits")

        async with aiohttp.ClientSession() as session:
        # Create both requests 
        
            task1 = session.get(url, headers=headers)
            task2 = session.get(url_credits, headers=headers)
        
        # Run requests in parallel
            responses = await asyncio.gather(task1, task2)
        
        # Process responses
            details = await responses[0].json()
            credits = await responses[1].json()


        return details, credits

    except (aiohttp.ClientError, asyncio.TimeoutError) as e:
        print(f"Error fetching data: {str(e)}")
        return None, None  # Return None in case of an error


