import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect
import datetime as dt
engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect = True)
Measurement = Base.classes.measurement
Station = Base.classes.station
from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return "Available routes: <br> /api/v1.0/precipitation <br> /api/v1.0/stations <br> /api/v1.0/tobs <br> /api/v1.0/yyyy-mm-dd <br> /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"


# 4. Define what to do when a user hits the /about route
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    precip_data = session.query(Measurement.date,Measurement.prcp).all()
    session.close()
   
    precipitation = []
    for date, prcp in precip_data:
        dict = {}
        dict["date"] = date
        dict["prcp"] = prcp
        precipitation.append(dict)
    return jsonify(precipitation)
    # return jsonify(all_precip)

@app.route("/api/v1.0/stations")
def station():
    session = Session(engine)
    station_data = session.query(Station.name).all()
    session.close()
    all_stations = []
    for name in station_data:
        dict = {}
        dict["name"] = name
        all_stations.append(dict)
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    year_ago = dt.date(2017,8,23) - dt.timedelta(days=365)
    session = Session(engine)
    station_year_data = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= year_ago).filter(Measurement.station == 'USC00519281').order_by((Measurement.date).desc()).all()
    last_year_tobs = list(np.ravel(station_year_data))
    session.close()
    return jsonify (last_year_tobs)

@app.route("/api/v1.0/<start_date>")
def temp_by_start(start_date):
    session = Session(engine)
    stats = session.query(Measurement.date,func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date == start_date).group_by(Measurement.date).all()
    session.close()
    return jsonify(stats)
    return jsonify({"error": "Date not found."}), 404

@app.route("/api/v1.0/<start_date>/<end_date>")
def temp_by_start_end(start_date,end_date):
    session = Session(engine)
    time_stats = session.query(Measurement.date,func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).group_by(Measurement.date).all()
    session.close()
    return jsonify(time_stats)
    return jsonify({"error": "Date not found."}), 404

if __name__ == "__main__":
    app.run(debug=True)
