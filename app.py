# Climate App

# Make necessary imports
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import numpy as np
import datetime as dt

# Setup database
# Generate the engine to correct sqlite file
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table in the sqlite file
station = Base.classes.station
measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    return (
        f"SQLAlchemy Challenge - Surfs Up!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
    )

# Precipitation Data
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Returns the jsonified precipitation data for the last year in the database
    recent_date = (session.query(measurement.date).order_by(measurement.date.desc()).first().date)
    prior_year = (dt.datetime.strptime(recent_date, "%Y-%m-%d")).date() - dt.timedelta(days=365)
    data_prcp = session.query(measurement.date, measurement.prcp).filter(measurement.date >= prior_year).all()
    
    session.close()
    
    # Query results to a dictionary
    prcp_dict = {} 
    for date, prcp in data_prcp:
        prcp_dict[date] = prcp
   
    # Return the JSON representation of your dictionary
    return jsonify(prcp_dict)

# Stations Data
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Perform a query to retrieve all the station data
    station_results = session.query(station.station).all()

    session.close()

    #Convert tuples into normal list
    station_list = list(np.ravel(station_results))

    # Return the JSON representation of your dictionary
    return jsonify(station_list)

# Tobs Data; Returns jsonified data for the most active station (USC00519281) for the last year of data
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Query tobs
    recent_date = (session.query(measurement.date).order_by(measurement.date.desc()).first().date)
    prior_year = (dt.datetime.strptime(recent_date, "%Y-%m-%d")).date() - dt.timedelta(days=365)
    active_stations = session.query(measurement.station, func.count(measurement.date)).group_by(measurement.station).\
                  order_by(func.count(measurement.date).desc()).all()
    most_active_station = active_stations[0][0]
    tobs_results = session.query(measurement.date, measurement.tobs).\
                                filter((measurement.station == most_active_station)\
                                        & (measurement.date >= prior_year)\
                                        & (measurement.date <= recent_date)).all()
    
    session.close()
    
    #Convert tuples into normal list
    tobs_list = list(np.ravel(tobs_results))
    
    return jsonify(tobs_list)

# Start route
# Route accepts the start date as a parameter from the URL
# Returns the min, max, and average temperatures calculated from the given start date to the end of the dataset
@app.route("/api/v1.0/start")
def start(start_date):
    session = Session(engine)
    
    temperatures = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).filter(measurement.date >= start_date).all()
    
    session.close()
    
    # Query results to a dictionary
    list = []
    for data in temperatures:
        start_dict = {}
        start_dict['Date'] = data[0]
        start_dict['Min Temp'] = data[1]
        start_dict['Avg Temp'] = round(data[2],2)
        start_dict['Max Temp'] = data[3]
        list.append(start_dict)

    #Return a JSON list
    return jsonify(list)

# Start/end route
# Route accepts the start and end dates as parameters from the URL
# Returns the min, max, and average temperatures calculated from the given start date to the given end date



if __name__ == "__main__":
    app.run(debug=True)