"""
Tour Agency Flask Application
"""

import os
from flask import Flask, request, flash, url_for, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tours.sqlite3'
app.secret_key = 'super secret key'
db = SQLAlchemy(app)


# Define the Tour model
class Tour(db.Model):
    id = db.Column('tour_id', db.Integer, primary_key=True)
    destination = db.Column(db.String(100))
    category = db.Column(db.String(50))  # Relaxation, Adventure, Cultural
    duration = db.Column(db.Integer)  # Duration in days
    service = db.Column(db.String(50))  # First Class, Regular
    price = db.Column(db.Float)
    availability = db.Column(db.String(20))  # Available or Not Available

    def __init__(self, destination, category, duration, service, price, availability):
        self.destination = destination
        self.category = category
        self.duration = duration
        self.service = service
        self.price = price
        self.availability = availability


# Create database tables
db.create_all()


@app.route('/')
def index():
    """
    Home page displays all tours.
    """
    all_tours = db.session.query(Tour).all()
    return render_template('index.html', tours=all_tours)


@app.route('/add', methods=['GET', 'POST'])
def add_tour():
    """
    Add a new tour package.
    """
    if request.method == 'POST':
        if not request.form['destination'] or not request.form['category'] or not request.form['service']:
            flash('Please enter all required fields!', 'error')
        else:
            tour = Tour(
                request.form['destination'],
                request.form['category'],
                int(request.form['duration']),
                request.form['service'],
                float(request.form['price']),
                request.form['availability']
            )
            db.session.add(tour)
            db.session.commit()
            flash('Tour added successfully!')
            return redirect(url_for('index'))

    return render_template('add_tour.html')


@app.route('/update/<int:tour_id>', methods=['GET', 'POST'])
def update_tour(tour_id):
    """
    Update an existing tour package.
    """
    tour = db.session.query(Tour).filter_by(id=tour_id).first()

    if request.method == 'POST':
        if not tour:
            flash('Tour not found!', 'error')
        else:
            tour.destination = request.form['destination']
            tour.category = request.form['category']
            tour.duration = int(request.form['duration'])
            tour.service = request.form['service']
            tour.price = float(request.form['price'])
            tour.availability = request.form['availability']

            db.session.commit()
            flash('Tour updated successfully!')
            return redirect(url_for('index'))

    return render_template('update_tour.html', tour=tour)


@app.route('/delete/<int:tour_id>', methods=['POST'])
def delete_tour(tour_id):
    """
    Delete a tour package.
    """
    tour = db.session.query(Tour).filter_by(id=tour_id).first()
    if tour:
        db.session.delete(tour)
        db.session.commit()
        flash('Tour deleted successfully!')
    else:
        flash('Tour not found!', 'error')

    return redirect(url_for('index'))


@app.route('/search_tours', methods=['GET', 'POST'])
def search_tours():
    if request.method == 'POST':
        destination = request.form.get('destination', '').strip()
        category = request.form.get('category', '').strip()

        # Build the query based on user input
        query = db.session.query(Tour)
        if destination:
            query = query.filter(Tour.destination.ilike(f"%{destination}%"))
        if category:
            query = query.filter(Tour.category == category)

        tours = query.all()

        # Pass results to the search_results.html template
        return render_template('search_results.html', tours=tours)

    # If GET request, render the search_tours.html template
    return render_template('search_tours.html')

@app.route('/reorder_ids', methods=['POST'])
def reorder_ids():
    tours = db.session.query(Tour).order_by(Tour.id).all()
    for index, tour in enumerate(tours, start=1):
        tour.id = index  # Reassign IDs sequentially
    db.session.commit()
    flash("IDs have been reordered.")
    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=os.environ.get('PORT', 8080))
