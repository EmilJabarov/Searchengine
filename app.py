from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os
from dotenv import load_dotenv
from datetime import datetime
import openai
from serpapi import GoogleSearch

load_dotenv()

os.environ["OPENAI_API_KEY"] = os.getenv('OPENAI_API_KEY')

app = Flask(__name__, 
    template_folder='app/templates',
    static_folder='app/static'
)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    preferences = db.Column(db.Text, nullable=True)
    searches = db.relationship('Search', backref='user', lazy=True)

class Search(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(200), nullable=False)
    modified_query = db.Column(db.String(200), nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/')
def home():
    if current_user.is_authenticated:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = db.session.query(User).filter(User.username == username).first()
        
        if user and user.password == password:
            login_user(user)
            return redirect(url_for('home'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        existing_user = db.session.query(User).filter(User.username == username).first()
        if existing_user:
            flash('Username already exists')
            return redirect(url_for('register'))
        
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    page = request.args.get('page', 1, type=int)
    if request.method == 'POST':
        query = request.form.get('query')
        if not query:
            flash('Please enter a search query')
            return redirect(url_for('search'))
        
        try:
            # Log the original query
            print(f"Original query: {query}")
            
            # Get modified query and log it
            modified_query = modify_query_with_gpt(query, current_user.preferences)
            print(f"Modified query: {modified_query}")
            
            # Get search results and log them
            results, total_results = get_search_results(modified_query, page)
            print(f"Number of results: {len(results)}")
            
            if not results:
                flash('No results found. Please try a different search term.')
                return redirect(url_for('search'))
            
            search_record = Search(
                query=query,
                modified_query=modified_query,
                user_id=current_user.id
            )
            db.session.add(search_record)
            db.session.commit()
            
            total_pages = min(10, (total_results + 9) // 10)
            
            return render_template('results.html', 
                                results=results,
                                original_query=query,
                                modified_query=modified_query,
                                current_page=page,
                                total_pages=total_pages)
        except Exception as e:
            print(f"Search error: {str(e)}")
            flash('An error occurred while searching. Please try again.')
            return redirect(url_for('search'))
    
    return render_template('search.html')

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        preferences = request.form.get('preferences')
        current_user.preferences = preferences
        db.session.commit()
        flash('Preferences updated successfully!')
    return render_template('profile.html')

@app.route('/history')
@login_required
def history():
    searches = db.session.query(Search)\
        .filter(Search.user_id == current_user.id)\
        .order_by(Search.timestamp.desc())\
        .all()
    return render_template('history.html', searches=searches)

def modify_query_with_gpt(query, preferences):
    # Return original query if preferences are None, "None", or empty
    if not preferences or preferences == "None":
        return query
        
    try:
        client = openai.OpenAI()
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system", 
                    "content": """You are a search query optimizer that helps enhance search queries based on user preferences. Follow these guidelines:
                    1. Keep the query natural and readable
                    2. Add relevant context words based on preferences
                    3. Avoid excessive use of search operators (+, "", -)
                    4. Maintain the original search intent
                    5. Keep the query concise
                    6. Return only the enhanced query"""
                },
                {
                    "role": "user", 
                    "content": f"Context: User preferences: {preferences}\nOriginal query: {query}\nCreate an enhanced search query."
                }
            ],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        return query

def get_search_results(query, page=1):
    try:
        search = GoogleSearch({
            "q": query,
            "api_key": os.getenv('SERPAPI_API_KEY'),
            "num": 10,
            "start": (page - 1) * 10
        })
        results = search.get_dict()
        search_results = results.get('organic_results', [])
        total_results = results.get('search_information', {}).get('total_results', 0)
        return search_results, total_results
    except Exception as e:
        print(f"SerpAPI error: {e}")
        return [], 0

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)