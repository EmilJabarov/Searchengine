import openai
from serpapi import GoogleSearch
from app.models import Search, ClickedResult
from app import db
import json
from datetime import datetime

class SearchService:
    @staticmethod
    def personalize_query(query, user_preferences, search_history):
        try:
            # Create context from user preferences and recent searches
            recent_searches = [s.original_query for s in search_history[:5]]
            context = {
                "preferences": user_preferences,
                "recent_searches": recent_searches
            }

            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a search query optimizer that personalizes queries based on user preferences and search history."},
                    {"role": "user", "content": f"Context: {json.dumps(context)}\nOriginal query: {query}\nProvide a personalized search query."}
                ],
                temperature=0.7,
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error personalizing query: {e}")
            return query

    @staticmethod
    def get_search_results(query, page=1, results_per_page=10):
        try:
            search = GoogleSearch({
                "q": query,
                "num": results_per_page,
                "start": (page - 1) * results_per_page,
                "api_key": os.getenv('SERPAPI_API_KEY')
            })
            results = search.get_dict()
            
            # Enhanced results processing
            processed_results = []
            for result in results.get('organic_results', []):
                processed_results.append({
                    'title': result.get('title'),
                    'link': result.get('link'),
                    'snippet': result.get('snippet'),
                    'displayed_link': result.get('displayed_link'),
                    'position': result.get('position'),
                    'rich_snippet': result.get('rich_snippet', {})
                })
            
            return {
                'results': processed_results,
                'total_results': results.get('search_information', {}).get('total_results', 0),
                'time_taken': results.get('search_information', {}).get('time_taken_displayed', 0)
            }
        except Exception as e:
            print(f"Error fetching search results: {e}")
            return {'results': [], 'total_results': 0, 'time_taken': 0}

    @staticmethod
    def record_click(search_id, url, title):
        try:
            clicked_result = ClickedResult(
                search_id=search_id,
                url=url,
                title=title
            )
            db.session.add(clicked_result)
            db.session.commit()
        except Exception as e:
            print(f"Error recording click: {e}")
            db.session.rollback()