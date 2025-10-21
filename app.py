import os
import random
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

# --- Configuration ---
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# Configure the database (SQLite, stored in a file named recipes.db)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'recipes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Model ---
class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    photo = db.Column(db.String(255), nullable=True)
    # Store ingredients as a single string, separated by newlines
    ingredients = db.Column(db.Text, nullable=True)
    steps = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Recipe {self.title}>'

# --- Helper Function ---
def placeholder_image(title):
    return f"https://images.unsplash.com/photo-1504674900247-0877df9cc836?auto=format&fit=crop&w=800&q=60&{title}"

# --- Routes ---

# Main page: Show all recipes
@app.route('/')
def home():
    recipes = Recipe.query.order_by(Recipe.id.desc()).all()
    return render_template('index.html', recipes=recipes, picked_recipe=None)

# Handle adding a new recipe
@app.route('/add', methods=['POST'])
def add_recipe():
    title = request.form.get('title')
    ingredients = request.form.get('ingredients', '') # Get as a single string
    steps = request.form.get('steps', '')
    photo = request.form.get('photo', '')

    if not title:
        # Simple validation
        return "Error: Title is required", 400
    
    # Use placeholder if no photo provided
    if not photo:
        photo = placeholder_image(title)

    new_recipe = Recipe(
        title=title,
        photo=photo,
        ingredients=ingredients,
        steps=steps
    )
    db.session.add(new_recipe)
    db.session.commit()

    return redirect(url_for('home')) # Go back to the homepage

# Handle deleting a recipe
@app.route('/delete/<int:recipe_id>')
def delete_recipe(recipe_id):
    recipe = Recipe.query.get_or_404(recipe_id) # Find recipe or show 404
    db.session.delete(recipe)
    db.session.commit()
    return redirect(url_for('home'))

# "Surprise Me": Pick a random recipe
@app.route('/surprise')
def surprise():
    recipes = Recipe.query.all()
    picked = None
    if recipes:
        picked = random.choice(recipes)
    
    # Re-render the homepage, but this time passing the picked recipe
    return render_template('index.html', recipes=recipes, picked_recipe=picked)


# --- Initialize Database ---
# This checks if the db file exists and creates it if not.
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)