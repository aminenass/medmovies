# 🎬 Medmovies App

This is a **Django-based web application** that provides a clean and interactive interface for discovering movies and TV shows. The app includes **simple authentication** features such as login and registration.

## 🔧 Tech Stack

- **Backend**: Django (Python)
- **Authentication**: Custom authentication (Login & Register)
- **Database**: PostgreSQL (hosted on [Supabase](https://supabase.com))
- **Frontend**: Tailwind CSS
- **API**: [TMDb (The Movie Database)](https://www.themoviedb.org/documentation/api)
- **Asynchronous Code**: This project utilizes asynchronous functionality with **Uvicorn** as the ASGI server for handling concurrent requests efficiently.


## 📺 Features

- 🔐 Simple User authentication system (register & login)
- 🎞️ Search for movies and TV shows
- 👥 View full cast details
- 🎥 Watch trailers
- 📍 Discover where to watch (platform availability)

## 🚀 Setup & Run

```bash
# Clone the repo
git clone https://github.com/aminenass/medmovies.git
cd medmovies

# Create virtual environment & activate
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt

# Add your environment variables (e.g., TMDB API Key, Supabase DB credentials)

# Run the server
python manage.py runserver

# or 
uvicorn medmovies.asgi:application --reload

📝 Notes
Make sure to set up your .env or environment configuration for the API key and Supabase database credentials.
