from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
from datetime import timedelta

app = Flask(__name__)
CORS(app)

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='Trishla1!',
        database='flight_tracking'
    )

# -------------------- FLIGHTS --------------------

@app.route("/flights")
def get_flights():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM flight;")
    flights = cursor.fetchall()
    cursor.close()
    conn.close()

    for f in flights:
        for key, value in f.items():
            if isinstance(value, timedelta):
                f[key] = str(value)

    return jsonify(flights)

@app.route("/create_flight", methods=["POST"])
def create_flight():
    data = request.json
    required = ["flightID", "routeID", "support_airline", "support_tail", "cost"]
    if not all(data.get(key) for key in required):
        return jsonify({"error": "Missing flight data"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO flight (flightID, routeID, support_airline, support_tail, cost)
            VALUES (%s, %s, %s, %s, %s)
        """, tuple(data[key] for key in required))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": f"Flight {data['flightID']} created successfully."}), 200

@app.route("/cancel_flight", methods=["POST"])
def cancel_flight():
    data = request.json
    flight_id = data.get("flightID")
    if not flight_id:
        return jsonify({"error": "Missing flight ID"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM flight WHERE flightID = %s", (flight_id,))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": f"Flight {flight_id} cancelled successfully."}), 200

# -------------------- AIRLINES --------------------

@app.route("/airlines")
def get_airlines():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM airline;")
    airlines = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(airlines)


@app.route("/create_airline", methods=["POST"])
def create_airline():
    data = request.json
    airline_id = data.get("airlineID")
    revenue = data.get("revenue", 0)
    if not airline_id:
        return jsonify({"error": "Missing airline ID"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO airline (airlineID, revenue) VALUES (%s, %s)", (airline_id, revenue))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": f"Airline {airline_id} created successfully."}), 200

@app.route("/delete_airline", methods=["POST"])
def delete_airline():
    data = request.json
    airline_id = data.get("airlineID")
    if not airline_id:
        return jsonify({"error": "Missing airline ID"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM airline WHERE airlineID = %s", (airline_id,))
        conn.commit()
        return jsonify({"message": f"Airline {airline_id} successfully deleted."}), 200
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# -------------------- PERSON --------------------

@app.route("/create_person", methods=["POST"])
def create_person():
    data = request.json
    required = ["personID", "first_name", "last_name"]
    if not all(data.get(k) for k in required):
        return jsonify({"error": "Missing required person data"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO person (personID, first_name, last_name, locationID)
            VALUES (%s, %s, %s, %s)
        """, (data["personID"], data["first_name"], data["last_name"], data.get("locationID")))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": f"Person {data['personID']} created successfully."}), 200

@app.route("/persons")
def get_persons():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM person;")
    persons = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(persons)

@app.route("/delete_persons", methods=["POST"])
def delete_persons():
    data = request.json
    person_ID = data.get("personID")
    if not person_ID:
        return jsonify({"error": "Missing person ID"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM person WHERE personID = %s", (person_ID,))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

# -------------------- AIRPORTS --------------------

@app.route("/airports")
def get_airports():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM airport;")
    airports = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(airports)

@app.route("/create_airport", methods=["POST"])
def create_airport():
    data = request.json
    required = ["airportID", "airport_name", "city", "state", "country"]
    if not all(data.get(k) for k in required):
        return jsonify({"error": "Missing required airport data"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO airport (airportID, airport_name, city, state, country, locationID)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (data["airportID"], data["airport_name"], data["city"], data["state"], data["country"], data.get("locationID")))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": f"Airport {data['airportID']} created successfully."}), 200

@app.route("/delete_airport", methods=["POST"])
def delete_airport():
    data = request.json
    airport_id = data.get("airportID")
    if not airport_id:
        return jsonify({"error": "Missing airport ID"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM airport WHERE airportID = %s", (airport_id,))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": f"Airport {airport_id} deleted successfully."}), 200

# -------------------- PILOTS --------------------

@app.route("/pilots")
def get_pilots():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pilot;")
    pilots = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(pilots)

@app.route("/create_pilot", methods=["POST"])
def create_pilot():
    data = request.json
    pid = data.get("personID")
    airline_id = data.get("airlineID")
    if not pid or not airline_id:
        return jsonify({"error": "Missing required pilot data"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO pilot (personID, airlineID) VALUES (%s, %s)", (pid, airline_id))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": f"Pilot {pid} created successfully."}), 200

@app.route("/delete_pilot", methods=["POST"])
def delete_pilot():
    data = request.json
    pid = data.get("personID")
    if not pid:
        return jsonify({"error": "Missing pilot ID"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM pilot WHERE personID = %s", (pid,))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": f"Pilot {pid} deleted successfully."}), 200

# -------------------- PASSENGERS --------------------

@app.route("/passengers")
def get_passengers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM passenger;")
    passengers = cursor.fetchall()
    cursor.close()
    conn.close()

    for p in passengers:
        for key, value in p.items():
            if isinstance(value, timedelta):
                p[key] = str(value)

    return jsonify(passengers)

@app.route("/add_passenger", methods=["POST"])
def add_passenger():
    data = request.json
    pid = data.get("personID")
    funds = data.get("funds", 0)
    if not pid:
        return jsonify({"error": "Missing passenger ID"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO passenger (personID, funds) VALUES (%s, %s)", (pid, funds))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": f"Passenger {pid} added successfully!"}), 200

@app.route("/delete_passenger", methods=["POST"])
def delete_passenger():
    data = request.json
    pid = data.get("personID")
    if not pid:
        return jsonify({"error": "Missing passenger ID"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM passenger WHERE personID = %s", (pid,))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": f"Passenger {pid} deleted successfully."}), 200

# -------------------- BOARDING --------------------

@app.route("/board_passenger", methods=["POST"])
def board_passenger():
    data = request.json
    pid = data.get("pid")
    fid = data.get("fid")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM passenger WHERE personID = %s", (pid,))
    passenger = cursor.fetchone()
    if not passenger:
        return jsonify({"error": "Passenger not found"}), 404

    cursor.execute("SELECT * FROM flight WHERE flightID = %s", (fid,))
    flight = cursor.fetchone()
    if not flight:
        return jsonify({"error": "Flight not found"}), 404

    fare = flight["cost"]
    if passenger["funds"] < fare:
        return jsonify({"error": "Insufficient funds"}), 400

    plane_id = flight["support_tail"]
    cursor.execute("SELECT seat_capacity FROM airplane WHERE tail_num = %s", (plane_id,))
    airplane = cursor.fetchone()
    if not airplane:
        return jsonify({"error": "Airplane not found"}), 404
    capacity = airplane["seat_capacity"]

    cursor.execute("SELECT person_list FROM people_in_the_air WHERE flight_list LIKE %s", (f"%{fid}%",))
    row = cursor.fetchone()
    onboard = len(row["person_list"].split(",")) if row and row["person_list"] else 0

    if onboard >= capacity:
        return jsonify({"error": "Flight is full"}), 400

    new_funds = passenger["funds"] - fare
    cursor.execute("UPDATE passenger SET funds = %s WHERE personID = %s", (new_funds, pid))

    cursor.execute("SELECT airlineID FROM airplane WHERE tail_num = %s", (plane_id,))
    airline_id = cursor.fetchone()["airlineID"]

    cursor.execute("UPDATE airline SET revenue = revenue + %s WHERE airlineID = %s", (fare, airline_id))

    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": f"Passenger {pid} boarded flight {fid}."}), 200

# -------------------- AIRPLANES --------------------

@app.route("/airplanes")
def get_airplanes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM airplane;")
    airplanes = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(airplanes)


@app.route("/add_airplane", methods=["POST"])
def add_airplane():
    data = request.json
    required = ["airlineID", "tail_num", "seat_capacity", "speed"]
    if not all(data.get(k) for k in required):
        return jsonify({"error": "Missing required airplane information"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO airplane (airlineID, tail_num, seat_capacity, speed, locationID, plane_type, model)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (data["airlineID"], data["tail_num"], data["seat_capacity"], data["speed"], data.get("locationID"), data.get("plane_type"), data.get("model")))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": f"Airplane {data['tail_num']} added successfully."}), 200

@app.route("/delete_airplane", methods=["POST"])
def delete_airplane():
    data = request.json
    tail_num = data.get("tail_num")
    if not tail_num:
        return jsonify({"error": "Missing tail number"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM airplane WHERE tail_num = %s", (tail_num,))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": f"Airplane {tail_num} deleted successfully."}), 200

if __name__ == "__main__":
    app.run(debug=True)
