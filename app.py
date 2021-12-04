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
        f"/api/v1.0/[start_date] (YYYY-MM-DD)<br/>"
        f"/api/v1.0/[start_date]/[end_date] (YYYY-MM-DD)<br/>"
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

# Tobs Data

if __name__ == "__main__":
    app.run(debug=True)