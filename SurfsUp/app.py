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

#1 (/)
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

#2 (/api/v1.0/precipitation)
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return the JSON representation of your dictionary."""
    # Query for the dates and precipitation values for the last 12 months
    last_year_precipitation = session.query(Measurement.date, Measurement.prcp).\
                                filter(Measurement.date >= '2016-08-23').all()

    session.close()

    # Convert the query results to a dictionary
    precipitation_data = {date: prcp for date, prcp in last_year_precipitation}

    return jsonify(precipitation_data)


#3 (/api/v1.0/stations)
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    # Query for the stations
    stations_list = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    stations_list = list(np.ravel(stations_list))

    return jsonify(stations_list)


#4 (/api/v1.0/tobs)
@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of temperature observations (TOBS) for the previous year."""
    # Query for the most active station for the last year of temperature data
    most_active_station = session.query(Measurement.station).\
                        group_by(Measurement.station).\
                        order_by(Measurement.station.desc()).first()[0]

    # Query for the dates and temperature observations for the most active station for the last year of data
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.station == most_active_station).\
                    filter(Measurement.date >= '2016-08-23').all()

    session.close()

    # Convert list of tuples into normal list
    tobs_list = list(np.ravel(tobs_data))

    return jsonify(tobs_list)




# #5 part 1 (/api/v1.0/<start>)
@app.route("/api/v1.0/<start>")
def temperature_stats_start(start):
    session = Session(engine)
    
    # Query for temperature stats
    temperature_stats = session.query(
        np.min(Measurement.tobs).label('min_temperature'),
        np.mean(Measurement.tobs).label('avg_temperature'),
        np.max(Measurement.tobs).label('max_temperature')).filter(Measurement.date >= start).all()
    
    # Close the session
    session.close()
    
    # Convert to JSON format
    result = {
        "start_date": start,
        "end_date": None,
        "temperature_stats": [{
            "min_temperature": stat.min_temperature,
            "avg_temperature": stat.avg_temperature,
            "max_temperature": stat.max_temperature
        } for stat in temperature_stats]
    }
    
    # Return the JSON response
    return jsonify(result)


# #5 part 2 (/api/v1.0/<start>/<end>)
@app.route("/api/v1.0/<start>/<end>")
def temperature_stats_range(start, end):
    session = Session(engine)
    
    # Query for temperature stats within the specified range
    temperature_stats = session.query(
        np.min(Measurement.tobs).label('min_temperature'),
        np.mean(Measurement.tobs).label('avg_temperature'),
        np.max(Measurement.tobs).label('max_temperature')).filter(Measurement.date >= start, Measurement.date <= end).all()
    
    # Close the session
    session.close()
    
    # Convert results to JSON format
    result = {
        "start_date": start,
        "end_date": end,
        "temperature_stats": [{
            "min_temperature": stat.min_temperature,
            "avg_temperature": stat.avg_temperature,
            "max_temperature": stat.max_temperature
        } for stat in temperature_stats]
    }
    
    # Return the JSON response
    return jsonify(result)
if __name__ == '__main__':
    app.run(debug=True)
