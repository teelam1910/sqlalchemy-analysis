## Import the dependencies.

import numpy as np
from flask import Flask, jsonify
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.ext.automap import automap_base




#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

## reflect an existing database into a new model
Base = automap_base()

## reflect the tables
Base.prepare(engine, reflect=True)

## Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

## Create our session (link) from Python to the DB
session = Session(engine) 




#################################################
## Flask Setup
#################################################
app = Flask(__name__)




#################################################
## Flask Routes
#################################################
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/&lt;start&gt;<br/>"
        f"/api/v1.0/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the JSON representation of your dictionary."""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for the dates and precipitation values for the last 12 months
    last_year_precipitation = session.query(Measurement.date, Measurement.prcp).\
                                filter(Measurement.date >= '2016-08-23').all()

    session.close()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in last_year_precipitation}

    return jsonify(precipitation_data)

@app.route("/api/v1.0/stations")
def stations():
    """Return a JSON list of stations from the dataset."""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for the stations
    stations_list = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    stations_list = list(np.ravel(stations_list))

    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations (TOBS) for the previous year."""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for the most active station for the last year of temperature data
    most_active_station = session.query(Measurement.station).\
                            group_by(Measurement.station).\
                            order_by(func.count(Measurement.station).desc()).first()[0]

    # Query for the dates and temperature observations for the most active station for the last year of data
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.station == most_active_station).\
                    filter(Measurement.date >= '2016-08-23').all()

    session.close()

    # Convert list of tuples into normal list
    tobs_list = list(np.ravel(tobs_data))

    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
def temp_start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start date."""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for the minimum, average, and maximum temperatures for a specified start date
    temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).all()

    # temperature_stats = session.query(np.min(Measurement.tobs),
    #                                 np.avg(Measurement.tobs),
    #                                 np.max(Measurement.tobs)).filter(Measurement.date >= start).all()

    session.close()

    # Convert list of tuples into normal list
    temp_data = list(np.ravel(temperature_stats))

    return jsonify(temp_data)

@app.route("/api/v1.0/<start>/<end>")
def temp_range(start, end):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified start-end range."""
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query for the minimum, average, and maximum temperatures for a specified start-end range
    # temperature_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    #                         filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    temperature_stats = session.query(
    np.min(Measurement.tobs),
    np.avg(Measurement.tobs),
    np.max(Measurement.tobs)
).filter(Measurement.date >= start).all()

    session.close()

    # Convert list of tuples into normal list
    temp_data = list(np.ravel(temperature_stats))

    return jsonify(temp_data)

if __name__ == '__main__':
    app.run(debug=True)
