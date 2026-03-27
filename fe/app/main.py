import os

import requests
from flask import Flask, flash, redirect, render_template, request, session, url_for


app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "frontend_secret_key"
API = os.getenv("API_BASE_URL", "http://localhost:8000")


ROOM_TYPE_LABELS = {
    "single": "Sencilla",
    "double": "Doble",
    "suite": "Suite",
    "family": "Familiar",
}

STATUS_LABELS = {
    "available": "Disponible",
    "occupied": "Ocupada",
    "cleaning": "Limpieza",
    "maintenance": "Mantenimiento",
    "confirmed": "Confirmada",
    "checked_in": "Hospedado",
    "checked_out": "Salida registrada",
    "cancelled": "Cancelada",
}


@app.context_processor
def inject_labels():
    return {
        "label_status": lambda value: STATUS_LABELS.get(value, value),
        "label_room_type": lambda value: ROOM_TYPE_LABELS.get(value, value),
    }


def auth_headers():
    token = session.get("token")
    return {"Authorization": f"Bearer {token}"} if token else {}


def login_required():
    return "token" in session


def prepare_response(response):
    response.encoding = "utf-8"
    return response


def api_detail(response):
    response = prepare_response(response)
    try:
        data = response.json()
        if isinstance(data, dict):
            return data.get("detail") or data.get("message") or "Ocurrió un error"
        return "Ocurrió un error"
    except Exception:
        return response.text.strip() or "Ocurrió un error inesperado"


def parse_json(response, default=None):
    response = prepare_response(response)
    try:
        return response.json()
    except Exception:
        return default


def room_payload_from_form(form):
    room_number = form.get("room_number", "").strip()
    if not room_number.isdigit() or int(room_number) <= 0:
        raise ValueError("El número de habitación debe ser un entero positivo")
    return {
        "room_number": str(int(room_number)),
        "room_type": form.get("room_type", "single"),
        "floor": int(form.get("floor", "1")),
        "price_per_night": float(form.get("price_per_night", "0")),
        "capacity": int(form.get("capacity", "1")),
        "description": form.get("description", "").strip() or None,
        "status": form.get("status", "available"),
    }


def reservation_payload_from_form(form):
    return {
        "room_id": int(form.get("room_id", "0")),
        "guest_id": int(form.get("guest_id", "0")),
        "check_in_date": form.get("check_in_date", ""),
        "check_out_date": form.get("check_out_date", ""),
        "notes": form.get("notes", "").strip() or None,
    }


@app.route("/")
def index():
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        payload = {
            "username": request.form.get("username", "").strip(),
            "email": request.form.get("email", "").strip(),
            "password": request.form.get("password", ""),
            "full_name": request.form.get("full_name", "").strip() or None,
        }
        try:
            response = requests.post(f"{API}/auth/register", json=payload, timeout=15)
            if response.status_code == 201:
                flash("Cuenta creada correctamente. Ahora puedes iniciar sesión.", "success")
                return redirect(url_for("login"))
            flash(api_detail(response), "error")
        except requests.RequestException:
            flash("No fue posible conectar con el servidor.", "error")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        payload = {
            "username": request.form.get("username", "").strip(),
            "password": request.form.get("password", ""),
        }
        try:
            response = requests.post(f"{API}/auth/login", json=payload, timeout=15)
            if response.status_code == 200:
                data = parse_json(response, {}) or {}
                session["token"] = data.get("access_token", "")
                session["username"] = payload["username"]
                flash("Sesión iniciada.", "success")
                return redirect(url_for("dashboard"))
            flash("Credenciales inválidas.", "error")
        except requests.RequestException:
            flash("No fue posible conectar con el servidor.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if not login_required():
        return redirect(url_for("login"))
    reservations_data = []
    try:
        response = requests.get(f"{API}/reservations/mine", headers=auth_headers(), timeout=15)
        if response.status_code == 200:
            reservations_data = parse_json(response, []) or []
        else:
            flash(api_detail(response), "error")
    except requests.RequestException:
        flash("No fue posible cargar el tablero.", "error")
    return render_template("dashboard.html", reservations=reservations_data)


@app.route("/rooms")
def rooms():
    if not login_required():
        return redirect(url_for("login"))
    rooms_data = []
    try:
        response = requests.get(f"{API}/rooms/", headers=auth_headers(), timeout=15)
        if response.status_code == 200:
            rooms_data = parse_json(response, []) or []
        else:
            flash(api_detail(response), "error")
    except requests.RequestException:
        flash("No fue posible cargar las habitaciones.", "error")
    return render_template("rooms.html", rooms=rooms_data)


@app.route("/rooms/add", methods=["GET", "POST"])
def add_room():
    if not login_required():
        return redirect(url_for("login"))
    if request.method == "POST":
        try:
            payload = room_payload_from_form(request.form)
            response = requests.post(f"{API}/rooms/", headers=auth_headers(), json=payload, timeout=15)
            if response.status_code == 201:
                flash("Habitación creada correctamente.", "success")
                return redirect(url_for("rooms"))
            flash(api_detail(response), "error")
        except ValueError as error:
            flash(str(error), "error")
        except requests.RequestException:
            flash("No fue posible guardar la habitación.", "error")
    return render_template("add_room.html")


@app.route("/rooms/<int:room_id>/edit", methods=["GET", "POST"])
def edit_room(room_id: int):
    if not login_required():
        return redirect(url_for("login"))
    room = None
    try:
        response = requests.get(f"{API}/rooms/{room_id}", headers=auth_headers(), timeout=15)
        if response.status_code == 200:
            room = parse_json(response, {})
        else:
            flash(api_detail(response), "error")
            return redirect(url_for("rooms"))
    except requests.RequestException:
        flash("No fue posible cargar la habitación.", "error")
        return redirect(url_for("rooms"))

    if request.method == "POST":
        try:
            payload = room_payload_from_form(request.form)
            response = requests.patch(f"{API}/rooms/{room_id}", headers=auth_headers(), json=payload, timeout=15)
            if response.status_code == 200:
                flash("Habitación actualizada correctamente.", "success")
                return redirect(url_for("rooms"))
            flash(api_detail(response), "error")
        except ValueError as error:
            flash(str(error), "error")
        except requests.RequestException:
            flash("No fue posible actualizar la habitación.", "error")
    return render_template("edit_room.html", room=room)


@app.route("/rooms/<int:room_id>/delete", methods=["POST"])
def delete_room(room_id: int):
    if not login_required():
        return redirect(url_for("login"))
    try:
        response = requests.delete(f"{API}/rooms/{room_id}", headers=auth_headers(), timeout=15)
        if response.status_code in {200, 204}:
            flash("Habitación eliminada correctamente.", "success")
        else:
            flash(api_detail(response), "error")
    except requests.RequestException:
        flash("No fue posible eliminar la habitación.", "error")
    return redirect(url_for("rooms"))


@app.route("/rooms/<int:room_id>/status", methods=["POST"])
def update_room_status(room_id: int):
    if not login_required():
        return redirect(url_for("login"))
    payload = {"status": request.form.get("status", "")}
    try:
        response = requests.patch(f"{API}/rooms/{room_id}/status", headers=auth_headers(), json=payload, timeout=15)
        if response.status_code >= 400:
            flash(api_detail(response), "error")
        else:
            flash("Estado de la habitación actualizado.", "success")
    except requests.RequestException:
        flash("No fue posible actualizar la habitación.", "error")
    return redirect(url_for("rooms"))


@app.route("/guests")
def guests():
    if not login_required():
        return redirect(url_for("login"))
    guests_data = []
    try:
        response = requests.get(f"{API}/guests/", headers=auth_headers(), timeout=15)
        if response.status_code == 200:
            guests_data = parse_json(response, []) or []
        else:
            flash(api_detail(response), "error")
    except requests.RequestException:
        flash("No fue posible cargar los huéspedes.", "error")
    return render_template("guests.html", guests=guests_data)


@app.route("/guests/add", methods=["GET", "POST"])
def add_guest():
    if not login_required():
        return redirect(url_for("login"))
    if request.method == "POST":
        payload = {
            "full_name": request.form.get("full_name", "").strip(),
            "email": request.form.get("email", "").strip(),
            "phone": request.form.get("phone", "").strip() or None,
            "document_id": request.form.get("document_id", "").strip() or None,
        }
        try:
            response = requests.post(f"{API}/guests/", headers=auth_headers(), json=payload, timeout=15)
            if response.status_code == 201:
                flash("Huésped creado correctamente.", "success")
                return redirect(url_for("guests"))
            flash(api_detail(response), "error")
        except requests.RequestException:
            flash("No fue posible guardar el huésped.", "error")
    return render_template("add_guest.html")


@app.route("/reservations")
def reservations():
    if not login_required():
        return redirect(url_for("login"))
    reservations_data = []
    try:
        response = requests.get(f"{API}/reservations/", headers=auth_headers(), timeout=15)
        if response.status_code == 200:
            reservations_data = parse_json(response, []) or []
        else:
            flash(api_detail(response), "error")
    except requests.RequestException:
        flash("No fue posible cargar las reservas.", "error")
    return render_template("reservations.html", reservations=reservations_data)


@app.route("/reservations/new", methods=["GET", "POST"])
def new_reservation():
    if not login_required():
        return redirect(url_for("login"))
    rooms_data = []
    guests_data = []
    try:
        rooms_response = requests.get(f"{API}/rooms/available", headers=auth_headers(), timeout=15)
        if rooms_response.status_code == 200:
            rooms_data = parse_json(rooms_response, []) or []
        guests_response = requests.get(f"{API}/guests/", headers=auth_headers(), timeout=15)
        if guests_response.status_code == 200:
            guests_data = parse_json(guests_response, []) or []
    except requests.RequestException:
        flash("No fue posible cargar el formulario.", "error")
    if request.method == "POST":
        try:
            payload = reservation_payload_from_form(request.form)
            response = requests.post(f"{API}/reservations/", headers=auth_headers(), json=payload, timeout=15)
            if response.status_code == 201:
                flash("Reserva creada correctamente.", "success")
                return redirect(url_for("dashboard"))
            flash(api_detail(response), "error")
        except requests.RequestException:
            flash("No fue posible crear la reserva.", "error")
    return render_template("new_reservation.html", rooms=rooms_data, guests=guests_data)


@app.route("/reservations/<int:reservation_id>/edit", methods=["GET", "POST"])
def edit_reservation(reservation_id: int):
    if not login_required():
        return redirect(url_for("login"))
    reservation = None
    rooms_data = []
    guests_data = []
    try:
        reservation_response = requests.get(f"{API}/reservations/{reservation_id}", headers=auth_headers(), timeout=15)
        if reservation_response.status_code == 200:
            reservation = parse_json(reservation_response, {})
        else:
            flash(api_detail(reservation_response), "error")
            return redirect(url_for("reservations"))
        rooms_response = requests.get(f"{API}/rooms/", headers=auth_headers(), timeout=15)
        if rooms_response.status_code == 200:
            rooms_data = parse_json(rooms_response, []) or []
        guests_response = requests.get(f"{API}/guests/", headers=auth_headers(), timeout=15)
        if guests_response.status_code == 200:
            guests_data = parse_json(guests_response, []) or []
    except requests.RequestException:
        flash("No fue posible cargar la reserva.", "error")
        return redirect(url_for("reservations"))

    if request.method == "POST":
        try:
            payload = reservation_payload_from_form(request.form)
            response = requests.patch(f"{API}/reservations/{reservation_id}", headers=auth_headers(), json=payload, timeout=15)
            if response.status_code == 200:
                flash("Reserva actualizada correctamente.", "success")
                return redirect(url_for("reservations"))
            flash(api_detail(response), "error")
        except requests.RequestException:
            flash("No fue posible actualizar la reserva.", "error")
    return render_template("edit_reservation.html", reservation=reservation, rooms=rooms_data, guests=guests_data)


@app.route("/reservations/<int:reservation_id>/delete", methods=["POST"])
def delete_reservation(reservation_id: int):
    if not login_required():
        return redirect(url_for("login"))
    try:
        response = requests.delete(f"{API}/reservations/{reservation_id}", headers=auth_headers(), timeout=15)
        if response.status_code in {200, 204}:
            flash("Reserva eliminada correctamente.", "success")
        else:
            flash(api_detail(response), "error")
    except requests.RequestException:
        flash("No fue posible eliminar la reserva.", "error")
    return redirect(url_for("reservations"))


@app.route("/reservations/<int:reservation_id>/status", methods=["POST"])
def update_reservation_status(reservation_id: int):
    if not login_required():
        return redirect(url_for("login"))
    payload = {"status": request.form.get("status", "")}
    try:
        response = requests.patch(f"{API}/reservations/{reservation_id}/status", headers=auth_headers(), json=payload, timeout=15)
        if response.status_code >= 400:
            flash(api_detail(response), "error")
        else:
            flash("Estado de la reserva actualizado.", "success")
    except requests.RequestException:
        flash("No fue posible actualizar la reserva.", "error")
    return redirect(request.referrer or url_for("reservations"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
