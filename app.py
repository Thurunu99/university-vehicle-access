import os
import csv
import io
from flask import Flask, render_template, request, redirect, Response
from flask_sqlalchemy import SQLAlchemy

# Get the exact path of the current folder
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)

# Force the database to be created exactly in this folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'vehicles.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the Vehicle Table 
class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vehicle_no = db.Column(db.String(20), nullable=False)
    owner_id = db.Column(db.String(20), nullable=False)

# Create the database and tables automatically
with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def home():
    success_message = None 
    error_message = None

    if request.method == 'POST':
        vehicle_no = request.form.get('vehicle_no')
        owner_id = request.form.get('owner_id')
        
        existing_vehicle = Vehicle.query.filter_by(vehicle_no=vehicle_no).first()
        
        if existing_vehicle:
            error_message = f"Error! Vehicle {vehicle_no} is already registered."
        else:
            new_vehicle = Vehicle(vehicle_no=vehicle_no, owner_id=owner_id)
            db.session.add(new_vehicle)
            db.session.commit()
            success_message = f"Success! Vehicle {vehicle_no} has been registered."
        
    search_query = request.args.get('search')
    
    if search_query:
        all_vehicles = Vehicle.query.filter(Vehicle.vehicle_no.ilike(f'%{search_query}%')).all()
    else:
        all_vehicles = Vehicle.query.all()
        
    # Get the total count of registered vehicles
    total_vehicles = Vehicle.query.count()
        
    return render_template('index.html', message=success_message, error=error_message, vehicles=all_vehicles, search_query=search_query, total_vehicles=total_vehicles)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    vehicle_to_update = Vehicle.query.get_or_404(id)
    
    if request.method == 'POST':
        vehicle_to_update.vehicle_no = request.form.get('vehicle_no')
        vehicle_to_update.owner_id = request.form.get('owner_id')
        
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "There was a problem updating the vehicle."
    else:
        return render_template('update.html', vehicle=vehicle_to_update)

@app.route('/delete/<int:id>')
def delete(id):
    vehicle_to_delete = Vehicle.query.get_or_404(id)
    
    try:
        db.session.delete(vehicle_to_delete)
        db.session.commit()
        return redirect('/')
    except:
        return "There was a problem deleting that vehicle."

# Route to export all vehicles to a CSV file
@app.route('/export')
def export_csv():
    # Fetch all vehicles from the database
    all_vehicles = Vehicle.query.all()
    
    # Create an in-memory string buffer
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write the column headers
    writer.writerow(['ID', 'Vehicle Number', 'Owner ID'])
    
    # Write the data rows
    for vehicle in all_vehicles:
        writer.writerow([vehicle.id, vehicle.vehicle_no, vehicle.owner_id])
        
    # Create the response object with the CSV data
    response = Response(output.getvalue(), mimetype='text/csv')
    response.headers["Content-Disposition"] = "attachment; filename=vehicles_database.csv"
    
    return response

if __name__ == '__main__':
    app.run(debug=True)