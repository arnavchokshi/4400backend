from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import mysql.connector
from datetime import timedelta

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={r"/*": {"origins": "*"}})



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


@app.route("/flight_landing", methods=["POST"])
def flight_landing():
    data = request.json
    fid = data.get("flightID")
    if not fid:
        return jsonify({"error": "Missing flight ID"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.callproc("flight_landing", [fid])
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": f"Flight {fid} landed successfully."}), 200


@app.route("/flight_takeoff", methods=["POST"])
def flight_takeoff():
    data = request.json
    fid = data.get("flightID")
    if not fid:
        return jsonify({"error": "Missing flight ID"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.callproc("flight_takeoff", [fid])
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": f"Flight {fid} took off successfully."}), 200

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

# -------------------- PILOT LICENSES --------------------
@app.route("/toggle_pilot_license", methods=["POST"])
def toggle_pilot_license():
    data = request.json
    required = ["personID", "plane_type", "skids", "propellers", "jet_engines"]
    if not all(k in data for k in required):
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.callproc("grant_or_revoke_pilot_license", (
            data["personID"],
            data["plane_type"],
            data["skids"],
            data["propellers"],
            data["jet_engines"]
        ))
        conn.commit()
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()

    return jsonify({"message": f"License toggled for {data['personID']} on plane type {data['plane_type']}."}), 200

@app.route("/pilot_licenses")
def get_pilot_licenses():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pilot_licenses;")
    licenses = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(licenses)



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






@app.route("/filter_table", methods=["POST"])
def filter_table():
    data = request.json
    table = data.get("table")
    conditions = data.get("conditions", {})

    if not table:
        return jsonify({"error": "Missing table name"}), 400

    condition_clauses = []
    values = []

    for col, cond in conditions.items():
        if cond.strip() == "":
            continue  # skip empty inputs
        if cond.startswith(("=", ">", "<", ">=", "<=", "!=")):
            condition_clauses.append(f"{col} {cond}")
        else:
            condition_clauses.append(f"{col} = %s")
            values.append(cond)

    where_clause = " AND ".join(condition_clauses)
    query = f"SELECT * FROM `{table}`"
    if where_clause:
        query += f" WHERE {where_clause}"

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, tuple(values))
        rows = cursor.fetchall()

        # Convert timedelta fields to strings
        for row in rows:
            for key, value in row.items():
                if isinstance(value, timedelta):
                    row[key] = str(value)

        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()




@app.route("/update_entity", methods=["POST"])
def update_entity():
    data = request.json
    table = data.get("table")
    primary_keys = data.get("primary_keys", {})
    updates = data.get("updates", {})

    if not table or not primary_keys or not updates:
        return jsonify({"error": "Missing required fields"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        set_clause = ", ".join(f"{k} = %s" for k in updates)
        where_clause = " AND ".join(f"{k} = %s" for k in primary_keys)
        sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        values = list(updates.values()) + list(primary_keys.values())

        cursor.execute(sql, values)
        conn.commit()

        return jsonify({"message": f"{table} updated successfully."})
    except mysql.connector.Error as err:
        conn.rollback()
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()







@app.route("/table/<table_name>")
def get_table(table_name):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(f"SELECT * FROM `{table_name}`")
        rows = cursor.fetchall()

        # Convert timedelta or datetime to string
        for row in rows:
            for key in row:
                if isinstance(row[key], timedelta):
                    row[key] = str(row[key])

        return jsonify(rows)
    except mysql.connector.Error as err:
        print(f"[ERROR] Failed to fetch {table_name}: {err}")
        return jsonify({"error": str(err)}), 500
    finally:
        cursor.close()
        conn.close()


@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True, port=8000)

