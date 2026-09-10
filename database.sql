PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL DEFAULT '',
    phone TEXT DEFAULT '',
    main_need TEXT DEFAULT 'Control general',
    notifications INTEGER NOT NULL DEFAULT 1,
    role TEXT NOT NULL DEFAULT 'user'
);

CREATE TABLE IF NOT EXISTS pets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    species TEXT NOT NULL,
    breed TEXT DEFAULT 'Paciente nuevo',
    age TEXT DEFAULT '',
    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    pet_id INTEGER,
    pet_name TEXT NOT NULL,
    pet_species TEXT NOT NULL,
    appointment_date TEXT NOT NULL,
    appointment_time TEXT NOT NULL,
    duration TEXT NOT NULL DEFAULT '30 min',
    reason TEXT NOT NULL,
    vet TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Confirmada',

    FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE,

    FOREIGN KEY (pet_id) REFERENCES pets(id)
        ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_appointments_date_time
    ON appointments (appointment_date, appointment_time);

CREATE INDEX IF NOT EXISTS idx_appointments_user
    ON appointments (user_id);

DELETE FROM appointments
WHERE id NOT IN (
    SELECT MIN(id)
    FROM appointments
    GROUP BY user_id, pet_name, appointment_date, appointment_time
);

DELETE FROM pets
WHERE id NOT IN (
    SELECT MIN(id)
    FROM pets
    GROUP BY user_id, name
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_pets_user_name
    ON pets (user_id, name);

CREATE UNIQUE INDEX IF NOT EXISTS uq_appointments_slot
    ON appointments (user_id, pet_name, appointment_date, appointment_time);

INSERT OR IGNORE INTO users (name, email, password, role)
VALUES ('Administrador PetCare', 'admin@petcare.com', 'admin123', 'admin');

INSERT OR IGNORE INTO users (name, email, password, phone)
VALUES ('Laura Méndez', 'cliente@petcare.com', 'petcare123', '300 000 0000');

INSERT OR IGNORE INTO pets (user_id, name, species, breed, age)
SELECT id, 'Luna', 'Perro', 'Golden Retriever', '4 años'
FROM users WHERE email = 'cliente@petcare.com';
INSERT OR IGNORE INTO pets (user_id, name, species, breed, age)
SELECT id, 'Milo', 'Gato', 'Siamés', '2 años'
FROM users WHERE email = 'cliente@petcare.com';
INSERT OR IGNORE INTO pets (user_id, name, species, breed, age)
SELECT id, 'Nala', 'Perro', 'Border Collie', '6 años'
FROM users WHERE email = 'cliente@petcare.com';
INSERT OR IGNORE INTO pets (user_id, name, species, breed, age)
SELECT id, 'Coco', 'Perro', 'Cocker Spaniel', '3 años'
FROM users WHERE email = 'cliente@petcare.com';

INSERT OR IGNORE INTO appointments (user_id, pet_id, pet_name, pet_species, appointment_date, appointment_time, duration, reason, vet, status)
SELECT u.id, p.id, 'Luna', 'Perro · Golden Retriever', date('now'), '09:00', '30 min', 'Consulta general', 'Dra. Valentina Ruiz', 'Confirmada'
FROM users u JOIN pets p ON p.user_id = u.id AND p.name = 'Luna'
WHERE u.email = 'cliente@petcare.com';
INSERT OR IGNORE INTO appointments (user_id, pet_id, pet_name, pet_species, appointment_date, appointment_time, duration, reason, vet, status)
SELECT u.id, p.id, 'Milo', 'Gato · Siamés', date('now'), '10:30', '45 min', 'Vacunación', 'Dra. Valentina Ruiz', 'Por confirmar'
FROM users u JOIN pets p ON p.user_id = u.id AND p.name = 'Milo'
WHERE u.email = 'cliente@petcare.com';
INSERT OR IGNORE INTO appointments (user_id, pet_id, pet_name, pet_species, appointment_date, appointment_time, duration, reason, vet, status)
SELECT u.id, p.id, 'Nala', 'Perro · Border Collie', date('now'), '12:00', '30 min', 'Control dermatológico', 'Dr. Andrés Soto', 'Confirmada'
FROM users u JOIN pets p ON p.user_id = u.id AND p.name = 'Nala'
WHERE u.email = 'cliente@petcare.com';
INSERT OR IGNORE INTO appointments (user_id, pet_id, pet_name, pet_species, appointment_date, appointment_time, duration, reason, vet, status)
SELECT u.id, p.id, 'Coco', 'Perro · Cocker Spaniel', date('now', '+1 day'), '09:30', '30 min', 'Seguimiento', 'Dra. Valentina Ruiz', 'Confirmada'
FROM users u JOIN pets p ON p.user_id = u.id AND p.name = 'Coco'
WHERE u.email = 'cliente@petcare.com';