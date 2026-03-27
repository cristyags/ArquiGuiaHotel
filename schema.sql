CREATE DATABASE IF NOT EXISTS stayease CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE stayease;

CREATE TABLE users (
    id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100) NULL,
    role ENUM('staff','manager') NOT NULL DEFAULT 'staff',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_users_username (username),
    UNIQUE KEY uq_users_email (email)
);

CREATE TABLE rooms (
    id INT NOT NULL AUTO_INCREMENT,
    room_number VARCHAR(10) NOT NULL,
    room_type ENUM('single','double','suite','family') NOT NULL DEFAULT 'single',
    floor INT NOT NULL DEFAULT 1,
    price_per_night DECIMAL(8,2) NOT NULL,
    capacity INT NOT NULL DEFAULT 1,
    description TEXT NULL,
    status ENUM('available','occupied','cleaning','maintenance') NOT NULL DEFAULT 'available',
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_rooms_number (room_number)
);

CREATE TABLE guests (
    id INT NOT NULL AUTO_INCREMENT,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(100) NOT NULL,
    phone VARCHAR(30) NULL,
    document_id VARCHAR(50) NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_guest_email (email)
);

CREATE TABLE reservations (
    id INT NOT NULL AUTO_INCREMENT,
    room_id INT NOT NULL,
    guest_id INT NOT NULL,
    staff_id INT NOT NULL,
    check_in_date DATE NOT NULL,
    check_out_date DATE NOT NULL,
    nightly_rate DECIMAL(8,2) NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL DEFAULT 0.00,
    status ENUM('confirmed','checked_in','checked_out','cancelled') NOT NULL DEFAULT 'confirmed',
    notes TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_res_room FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_res_guest FOREIGN KEY (guest_id) REFERENCES guests(id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_res_staff FOREIGN KEY (staff_id) REFERENCES users(id) ON DELETE RESTRICT ON UPDATE CASCADE
);

CREATE TABLE notifications (
    id INT NOT NULL AUTO_INCREMENT,
    user_id INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    type ENUM('reservation_created','guest_checked_in','guest_checked_out','reservation_cancelled','general') NOT NULL DEFAULT 'general',
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    related_reservation_id INT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_notif_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_notif_reservation FOREIGN KEY (related_reservation_id) REFERENCES reservations(id) ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE INDEX idx_res_staff ON reservations (staff_id);
CREATE INDEX idx_res_status ON reservations (status);
CREATE INDEX idx_rooms_status_type ON rooms (status, room_type);
CREATE INDEX idx_res_room ON reservations (room_id);
CREATE INDEX idx_res_guest ON reservations (guest_id);
CREATE INDEX idx_notif_user_unread ON notifications (user_id, is_read);

INSERT INTO users (username, email, password_hash, full_name, role) VALUES
('recepcion1', 'recepcion1@stayease.local', '$2b$12$wsyXenlQM3RetG4P4ZPXFuTZdZFde9nyfAyfGCjaRB6ih8cGwPWSS', 'Ana Recepción', 'staff'),
('gerente1', 'gerente1@stayease.local', '$2b$12$30mrmHLZTzeQoyAtLDtOmuo4I3hyhuXBH5m.B0869eaRjMIG384lm', 'Carlos Gerencia', 'manager');

INSERT INTO rooms (room_number, room_type, floor, price_per_night, capacity, description, status) VALUES
('101', 'single', 1, 65.00, 1, 'Habitación individual con vista al jardín.', 'available'),
('102', 'double', 1, 95.00, 2, 'Habitación doble cerca de recepción.', 'occupied'),
('201', 'suite', 2, 180.00, 3, 'Suite amplia con sala privada.', 'cleaning'),
('202', 'family', 2, 140.00, 4, 'Habitación familiar para grupos pequeños.', 'available'),
('301', 'double', 3, 120.00, 2, 'Habitación doble con balcón.', 'maintenance');

INSERT INTO guests (full_name, email, phone, document_id) VALUES
('María López', 'maria.lopez@example.com', '+50370000001', 'A1234567'),
('Jorge Pérez', 'jorge.perez@example.com', '+50370000002', 'B7654321'),
('Lucía Torres', 'lucia.torres@example.com', '+50370000003', 'P9988776');

INSERT INTO reservations (room_id, guest_id, staff_id, check_in_date, check_out_date, nightly_rate, total_amount, status, notes) VALUES
(2, 1, 1, '2026-03-26', '2026-03-29', 95.00, 285.00, 'checked_in', 'Ingreso temprano solicitado.'),
(3, 2, 1, '2026-03-24', '2026-03-26', 180.00, 360.00, 'checked_out', 'Salida completada esta mañana.'),
(4, 3, 2, '2026-03-30', '2026-04-02', 140.00, 420.00, 'confirmed', 'Reserva familiar confirmada.');

INSERT INTO notifications (user_id, title, message, type, is_read, related_reservation_id) VALUES
(1, 'Reserva creada', 'La reserva de Lucía Torres fue registrada correctamente.', 'reservation_created', FALSE, 3),
(1, 'Huésped registrado', 'María López ya realizó su check-in.', 'guest_checked_in', TRUE, 1),
(1, 'Habitación en limpieza', 'La habitación 201 pasó a limpieza tras el checkout.', 'guest_checked_out', FALSE, 2);
