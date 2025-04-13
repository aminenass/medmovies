from django.shortcuts import render
from .tests import *
from random import choice
import asyncio
from asgiref.sync import sync_to_async
import asyncio
from django.http import Http404


# Helper function to run synchronous code (like `choice`) in async context
async def async_choice(items):
    return await sync_to_async(choice)(items)


# Main view
async def hello(request):

    # Fetch all data concurrently using asyncio.gather
    movie_data, tvshow_data, anime_data, kdrama_data, trdrama_data , genre_data = await asyncio.gather(
        movies(1),
        tv_shows(1),
        anime(1, "10759"),
        drama(1, "ko"),
        drama(1, "tr"), 
        genre(),
    )

    # Get random movie/tvshow trailer
    random_movie_trailer = await async_choice(tvshow_data)
    trailer_data = await trailer(random_movie_trailer["id"],"tv")

    context = {
        "movie": movie_data,
        "tvshow": tvshow_data,
        "anime_action": anime_data,
        "kdrama": kdrama_data,
        "trdrama": trdrama_data,
        "random_tv_movie": await async_choice(movie_data + tvshow_data ),
        "random_tv_movie2": random_movie_trailer,
        "trailer": trailer_data,
        "genre": genre_data,
    }

    return await sync_to_async(render)(request, 'main.html', context)

# Movie view
async def movie(request):
    page = int(request.GET.get('page', 1))
    page = max(1, min(page, 100))  # Clamp page between 1-100
    total_pages = 100

    # Fetch movie and genre data concurrently
    movie_data, genre_data = await asyncio.gather(
        movies(page),
        genre(),
    )
 
    context = {
        "name": "MOVIES",
        "movie": movie_data,
        "page": page,
        "genre": genre_data,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }
    return await sync_to_async(render)(request, 'movie.html', context)

# TV Shows view
async def tvshows(request, category: str = None):
    page = int(request.GET.get('page', 1))
    page = max(1, min(page, 100))  # Clamp page between 1-100
    total_pages = 100

    # Fetch TV shows and genre data concurrently
    tvshow_data, genre_data = await asyncio.gather(
        tv_shows(page, category),
        genre(),
    )

    context = {
        "name": f"{category.upper() + ' ' if category else 'TV SHOWS'}",
        "tvshow": tvshow_data,
        "genre": genre_data,
        "page": page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
        "current_category": category or 'all',
    }
    return await sync_to_async(render)(request, 'tvshows.html', context)

async def search_results(request):
    
    query = request.GET.get('q', '')
    page = int(request.GET.get('page', 1))
    
    results = []
    total_pages = 1  # Default to 1 page in case of break

    
    if query:
        try:
            results,total_pages = await search_media(page, query, media_type='both')      
        except Exception as e:
            print(f"Search error: {e}")
                
    page = max(1, min(page, total_pages))  

    context = {
        'query': query,
        'results': results,
        'page': page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }
    return await sync_to_async(render)(request, 'search_results.html', context)


async def media_detail_view(request, item_id,types,page=1):

    data,credits = await get_details_by_id(item_id,types)
    trailer_data = await trailer(data["id"],types) if data else None
    
    # suggesstion  = await movies(page,genre_ids=[genres["id"] for genres in data["genres"]]) if types == "movie" else await tv_shows(page,genre_ids=[genres["id"] for genres in data["genres"]])
    
    # Limit genres initially
    list_genre = lambda n : [g["id"] for g in data.get("genres", [])][:n] if data else []
    # Proper async suggestion handling
    suggestion = []
    if data:
        try:
            if types == "movie":
                n = 4 
                while n > 0 : 
                    # Movies function should accept genre_ids parameter
                    suggestion = await movies(page=page, genre_ids=list_genre(n)) 
                    if len(suggestion) >= 5 :
                        break # good enough, stop retrying
                    n - 1
                        
            else:
                n = 4 
                while n > 0 : 
                    # async def tv_shows(page: int, category: str, genre_ids: List[int])
                    suggestion = await tv_shows(
                        page=page,
                        category="all",  # Or None if you want trending
                        genre_ids=list_genre(n)
                    )
                    if len(suggestion) >= 5 : 
                        break # good enough, stop retrying
                    n - 1
                        
        except Exception as e:
            print(f"Suggestion fetch error: {e}")
            suggestion = []    
    
    if not data :
        raise Http404("Content not found")

    context = {
        'data': data,
        "credits":credits,
        "trailer":trailer_data,
        "suggestion":  suggestion ,
        "types" : "movies" if types == "movie" else "tvshows" ,  
         
    }

    return await sync_to_async(render)(request, "view_details.html", context)
