# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# Import Python libraries
import numpy as np
import datetime as dt

# Import Flask
from flask import Flask, jsonify

# 1. Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Reflect an existing database into a new model
Base = automap_base()

# Reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# 2. Flask Setup
app = Flask(__name__)

# Define Homepage route


@app.route("/")
def homepage():
    print("Server received request for 'Home' page...")
    return (
        "Welcome to Hawaii Climate Analysis homepage! The list of available routes is below: <br/>"
        f"<br/>"
        f"Precipitation Data for One Year:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"<br/>"
        f"List of Active Stations:<br/>"
        f"/api/v1.0/stations<br/>"
        f"<br/>"
        f"Dates and Temperature Observations of the Most Active Station for the previous year:<br/>"
        f"/api/v1.0/tobs<br/>"
        f"<br/>"
        f"The Minimum, Maximum, and Average Temperature for a specified Start Date:<br/>"
        f"Please enter the start date after / in URL box with the format yy-mm-dd <br/>"
        f"/api/v1.0/<start><br/>"
        f"<br/>"
        f"The Minimum, Maximum, and Average Temperatures for a specified Start and End Date:<br/>"
        "Please enter the start date and end date after / in URL box with the format yy-mm-dd/yy-mm-dd <br/>"
        f"/api/v1.0/<start>/<end>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Find the most recent date in the data set.
    most_recent_date = session.query(Measurement.date).order_by(
        Measurement.date.desc()).first()

    # Calculate the date one year from the last date in data set.
    one_year_ago_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Perform a query to retrieve the data and precipitation scores
    precipitation_data = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= one_year_ago_date).all()

    print(precipitation_data)

    # Close Session
    session.close()

    # Create a list of dictionaries to store the date and the precipitation
    prcp_list = []

    for date, precipitation in precipitation_data:
        prcp_dict = {}
        prcp_dict[date] = precipitation
        prcp_list.append(prcp_dict)

    return jsonify(prcp_list)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Retrieving data for all stations from station table
    all_stations = session.query(Station.name, Station.station,
                                 Station.elevation, Station.latitude, Station.longitude).all()

    # Close Session
    session.close()

    # Create a list of dictionary to store station data
    station_data = []
    for station_name, station, elevation, latitude, longitude in all_stations:
        station_dict = {}
        station_dict["Station Name"] = station_name
        station_dict["Station ID"] = station
        station_dict["Elevation"] = elevation
        station_dict["Latitude"] = latitude
        station_dict["Longitude"] = longitude
        station_data.append(station_dict)

    return jsonify(station_data)


@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Calculate the date one year from the last date in data set.
    one_year_ago_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Retrieving the dates and temperature observations
    active_station = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date >= one_year_ago_date).all()

    # Close Session
    session.close()

    # Create a list of dictionaries to store data
    most_active_station = []
    for date, temp in active_station:
        active_dict = {}
        active_dict[date] = temp
        most_active_station.append(active_dict)

    return jsonify(most_active_station)


@app.route("/api/v1.0/<start>")
def start(start):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Retrieving the minimum, maximum, and average temp for a specified start date to the end of the dataset
    query_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Close Session
    session.close()

    # Create a list of dictionary to store station data
    start_date = []
    for tmin, tmax, tavg in query_results:
        start_dict = {}
        start_dict["Minimum Temperature"] = tmin
        start_dict["Maxium Temperature"] = tmax
        start_dict["Average Temperature"] = tavg
        start_date.append(start_dict)

    return jsonify(start_date)


@app.route("/api/v1.0/<start>/<end>")
def range_date(start, end):

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Preform a query to retrieve the minimum, maximum, and average temperature for a specified start date to the end of the dataset
    query_results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()

    # Close Session
    session.close()

    # Create a dictionary from the row data and append to list range_date
    range_date = []
    for tmin, tmax, tavg in query_results:
        range_dict = {}
        range_dict["Minimum Temperature"] = tmin
        range_dict["Maxium Temperature"] = tmax
        range_dict["Average Temperature"] = tavg
        range_date.append(range_dict)

    return jsonify(range_date)


if __name__ == "__main__":
    app.run(debug=True)
