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
    
    suggestion = await recomendation(page=1, movie_id= item_id, types=types)


    context = {
        'data': data,
        "credits":credits,
        "trailer":trailer_data,
        "suggestion":  suggestion[0] ,
        "types" : f"recomendation/{types}/{item_id}"
         
    }

    return await sync_to_async(render)(request, "view_details.html", context)


async def media_recomendation(request,item_id,types,page=1):
    
    page = int(request.GET.get('page', 1))
    
    total_pages = 1 
    
    data , total_pages = await recomendation(page, movie_id = item_id, types=types)
    
    page = max(1, min(page, total_pages ))  

    context = {
        "name": "SUGGESTION",
        'items': data,      
        'page': page,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_previous": page > 1,
    }

    return await sync_to_async(render)(request, "recommendation.html", context)






