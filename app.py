import sqlite3
from datetime import date, datetime
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

BASE_DIR = Path(__file__).resolve().parent
DATABASE = BASE_DIR / "petcare.db"
app = Flask(__name__, template_folder="TEMPLATES", static_folder="STATIC", static_url_path="/static")
app.secret_key = "petcare-development-key"


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """
    Inicializa la base de datos usando el archivo database.sql.
    """
    connection = get_db()

    try:
        with open(BASE_DIR / "database.sql", "r", encoding="utf-8") as file:
            sql = file.read()

        connection.executescript(sql)
        connection.commit()
    finally:
        connection.close()


def current_user():
    user_id = session.get("user_id") or session.get("admin_id")
    if not user_id:
        return None
    connection = get_db()
    user = connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    connection.close()
    return user


def appointment_view(row):
    item = dict(row)
    today = date.today()
    appointment_date = date.fromisoformat(item["appointment_date"])
    item["day"] = "today" if appointment_date == today else "tomorrow" if appointment_date == date.fromordinal(today.toordinal() + 1) else "week"
    item["time"] = item.pop("appointment_time")
    item["pet"] = item.pop("pet_name")
    item["species"] = item.pop("pet_species")
    item["color"] = {"Luna": "pet-luna", "Milo": "pet-milo", "Nala": "pet-nala", "Coco": "pet-coco"}.get(item["pet"], "pet-coco")
    return item


def all_appointments():
    connection = get_db()
    rows = connection.execute("SELECT a.*, u.name AS client_name, u.email AS client_email FROM appointments a JOIN users u ON u.id = a.user_id ORDER BY a.appointment_date, a.appointment_time").fetchall()
    connection.close()
    return [appointment_view(row) for row in rows]


def login_required():
    return current_user() is not None


@app.context_processor
def shared_template_data():
    appointments = all_appointments()
    return {"user": current_user(), "appointments": appointments, "today_count": len([a for a in appointments if a["day"] == "today"]), "tomorrow_count": len([a for a in appointments if a["day"] == "tomorrow"]), "week_count": len(appointments)}


@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/registrarse", methods=["GET", "POST"])
def registrarse():
    if request.method == "POST":
        connection = get_db()
        cursor = connection.execute("INSERT INTO users (name, email, password, phone, main_need, notifications) VALUES (?, ?, ?, ?, ?, ?)", (request.form["name"].strip(), request.form["email"].strip().lower(), request.form.get("password", ""), request.form.get("phone", "").strip(), request.form.get("main_need", "Control general"), request.form.get("notifications") == "on"))
        pet_name = request.form.get("pet_name", "").strip()
        if pet_name:
            connection.execute("INSERT INTO pets (user_id, name, species) VALUES (?, ?, ?)", (cursor.lastrowid, pet_name, request.form.get("pet_type", "Perro")))
        connection.commit()
        session["user_id"] = cursor.lastrowid
        connection.close()
        return redirect(url_for("inicio"))
    return render_template("registrarse.html")


@app.route("/sesion", methods=["GET", "POST"])
def sesion():
    error = None
    if request.method == "POST":
        connection = get_db()
        user = connection.execute("SELECT * FROM users WHERE email = ? AND password = ?", (request.form["email"].strip().lower(), request.form.get("password", ""))).fetchone()
        connection.close()
        if user:
            session["user_id"] = user["id"]
            return redirect(url_for("inicio"))
        error = "El correo o la contraseña no son correctos."
    return render_template("sesion.html", error=error)


@app.route("/admin/sesion", methods=["GET", "POST"])
def admin_sesion():
    error = None
    if request.method == "POST":
        connection = get_db()
        admin = connection.execute("SELECT * FROM users WHERE email = ? AND password = ? AND role = 'admin'", (request.form["email"].strip().lower(), request.form.get("password", ""))).fetchone()
        connection.close()
        if admin:
            session["admin_id"] = admin["id"]
            return redirect(url_for("perfil"))
        error = "Las credenciales de administrador no son correctas."
    return render_template("admin_sesion.html", error=error)


@app.route("/admin")
def admin_panel():
    if not session.get("admin_id"):
        return redirect(url_for("admin_sesion"))
    return render_template("admin.html", admin=current_user(), admin_appointments=all_appointments())


@app.post("/admin/citas/<int:appointment_id>/eliminar")
def eliminar_cita(appointment_id):
    if not session.get("admin_id"):
        return redirect(url_for("admin_sesion"))
    connection = get_db()
    connection.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    connection.commit()
    connection.close()
    return redirect(url_for("admin_panel"))


@app.post("/admin/citas/<int:appointment_id>/editar")
def editar_cita(appointment_id):
    if not session.get("admin_id"):
        return redirect(url_for("admin_sesion"))
    connection = get_db()
    connection.execute("UPDATE appointments SET appointment_date = ?, appointment_time = ?, reason = ?, status = ? WHERE id = ?", (request.form["date"], request.form["time"], request.form["reason"], request.form["status"], appointment_id))
    connection.commit()
    connection.close()
    return redirect(url_for("admin_panel"))


@app.route("/cerrar-sesion")
def cerrar_sesion():
    session.clear()
    return redirect(url_for("sesion"))


@app.route("/perfil")
def perfil():
    if session.get("admin_id"):
        return render_template("perfil_admin.html", admin=current_user())
    if not login_required():
        return redirect(url_for("sesion"))
    return render_template("perfil.html")


@app.post("/api/citas")
def crear_cita():
    data = request.get_json() or {}
    if not data.get("pet", "").strip() or not data.get("time") or not data.get("date"):
        return jsonify({"error": "Faltan datos de la cita."}), 400
    user = current_user()
    user_id = user["id"] if user else 1
    connection = get_db()
    cursor = connection.execute("INSERT INTO appointments (user_id, pet_name, pet_species, appointment_date, appointment_time, reason, vet, status) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (user_id, data["pet"].strip(), "Paciente nuevo", data["date"], data["time"], data.get("reason", "Consulta general"), "Dra. Valentina Ruiz", "Confirmada"))
    connection.commit()
    row = connection.execute("SELECT a.*, u.name AS client_name, u.email AS client_email FROM appointments a JOIN users u ON u.id = a.user_id WHERE a.id = ?", (cursor.lastrowid,)).fetchone()
    connection.close()
    appointments = all_appointments()
    return jsonify({"appointment": appointment_view(row), "today_count": len([a for a in appointments if a["day"] == "today"]), "tomorrow_count": len([a for a in appointments if a["day"] == "tomorrow"]), "week_count": len(appointments)})


init_db()

if __name__ == "__main__":
    app.run(debug=True)
    