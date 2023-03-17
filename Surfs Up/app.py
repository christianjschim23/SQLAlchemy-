import datetime as dt
from datetime import timedelta

# Importing dependencies 
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Import Flask
from flask import Flask, jsonify 

# reate engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()
# Reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create an app. being sure to pass __name__
app = Flask(__name__)

# Flask Routes
@app.route("/")
def home():
    """List all available api routes"""
    return (
        f"Welcome to the Home Page <br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

# Route one 
# Precipitation data
@app.route('/api/v1.0/precipitation')
def precipitation():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the most recent data
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_date = dt.datetime.strptime(last_date.date, '%Y-%m-%d') 

    # Calculate the date one year from the last date in data set.
    last_twelve_months = last_date - timedelta(days=365)
    
    # Query the perciptation data for the last twelve months 
    prcp_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_twelve_months).all()
    
    # Create a dictionary for the percipation data
    prcp_dict = {}
    for date, prcp in prcp_data:
        prcp_dict[date] = prcp

    # Close session
    session.close()

    # Return the jsonified dictionary
    return jsonify(prcp_dict)

# Route Two
# Stations Data
@app.route('/api/v1.0/stations')
def stations():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the names of the stations in the database 
    station_data = session.query(Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation).all()

    # Close the session
    session.close()

    # Create a dictionary for the station data
    station_dict = {}
    for station in station_data:
        station_dict[station.station] = {
            "name": station.name,
            "latitude": station.latitude,
            "longitude": station.longitude,
            "elevation": station.elevation
        }

    # Return the jsonified station data 
    return jsonify(station_dict)

# Returns jsonified data for the most active station (USC00519281) (3 points)
# Only returns the jsonified data for the last year of data (3 points)
# Route Three
# Tobs Data
@app.route('/api/v1.0/tobs')
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date 1 year ago from the last date in database
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)
    
    # Query for the most active station for the last year of data
    most_active_station_id = 'USC00519281'
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
                filter(Measurement.station == most_active_station_id).\
                filter(Measurement.date >= year_ago).all()

    # Close the session
    session.close()

    # Create a dictionary from the data and append to a list
    tobs_list = []
    for date, tobs in tobs_data:
        tobs_dict = {}
        tobs_dict['date'] = date
        tobs_dict['tobs'] = tobs
        tobs_list.append(tobs_dict)

    # Return the JSON representation of the list
    return jsonify(tobs_list)

# Route Four
@app.route('/api/v1.0/<start>')
def start(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    most_active_station_id = 'USC00519281'
    start_date = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.station == most_active_station_id).filter(Measurement.date >= start).all()
    
    # Close the session
    session.close()

    # Return the jsonified results
    return jsonify(start_date)

# Route Five
@app.route('/api/v1.0/<start>/<end>')
def range(start, end):

    # Create our session
    session = Session(engine)

    most_active_station_id = 'USC00519281'
    start_end_date = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
            filter(Measurement.station == most_active_station_id).filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    
    # Close Session
    session.close()

    # Return jsonified results 
    return jsonify(start_end_date)

if __name__ == '__main__':
    app.run(debug=True)



