#Hello, I do not know why it keeps having erros when i run the codes for each route
#run successfully api/v1.0/precipitation<br, then error with station rout, then fix station route, the precipitaiton has errors? @@
#and it keeps repeating the same errors for other routes
#so we need to clear browser/cache everytime? i am not sure the issue solution


import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite")


# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
# Flask Setup
app = Flask(__name__)



#Creating flask routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
#/api/v1.0/precipitation
def precipitation():

    # Creates session link from Python to SQLite database
    session = Session(engine)

    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    precipitation = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= prev_year).all()
    precip = {date: prcp for date, prcp in precipitation}
    return jsonify(precip)

    session.close()

#/api/v1.0/stations
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    # query to find the weather stations
    results = session.query(Measurement.station).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).all()

    session.close()

    station_list = list(np.ravel(results))
    
    return jsonify(station_list)

    #return jsonify(station_result)

##/api/v1.0/tobs
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    # Get date one year from tobs
    active_tobs = session.query(Measurement.date).\
        order_by(Measurement.date.desc()).first()
    
    active_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    # Get tobs and date from a year ago
    tob_results = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.date >= active_year).\
        order_by(Measurement.date.desc()).all()

    session.close()

    all_tobs = []
    for date, tobs in tob_results:
        tobs_dict = {}
        tobs_dict[date] = tobs
        all_tobs.append(tobs_dict)

    return jsonify(all_tobs)

##api/v1.0/start_date/<start>
@app.route("/api/v1.0/<start>")
def start_date(start):
    session = Session(engine)
    # calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date
    start_result = session.query(func.min(Measurement.tobs),func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    
    session.close()

    tobs_list_start = []
    for min, avg, max in start_result:
        start_tobs_dict = {}
        start_tobs_dict["min"] = min
        start_tobs_dict["average"] = avg
        start_tobs_dict["max"] = max
        tobs_list_start.append(start_tobs_dict)
    
    return jsonify(tobs_list_start)

##api/v1.0/startend/<start>/<end>
@app.route("/api/v1.0/<start>/<end>")
def Start_end(start, end):
    session = Session(engine)
   
    # When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than and equal to the start date
    end_result = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()

    session.close()

    # Create a dictionary from the row data and append to a list of all_temp_normals
    tobs_list_end = []
    for min, avg, max in end_result:
        end_tobs_dict = {}
        end_tobs_dict["min_tobs"] = min
        end_tobs_dict["ave_tobs"] = avg
        end_tobs_dict["max_tobs"] = max
        tobs_list_end.append(end_tobs_dict)

    return jsonify(tobs_list_end)


if __name__ == '__main__':
    app.run(debug=True)
