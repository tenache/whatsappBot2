-- Creación de la tabla Servicios_Programados
CREATE TABLE Servicios_Programados (
    Domicilio TEXT NOT NULL,
    Horario_ser TEXT NOT NULL,
    telefono_cliente TEXT NOT NULL,
    desea_reprogramar BOOLEAN
);

-- Insertar datos ficticios en la tabla Servicios_Programados
INSERT INTO Servicios_Programados (Domicilio, Horario_ser, telefono_cliente, desea_reprogramar) VALUES
('Calle Falsa 123', 'Lunes 10:00', '555-1234', NULL),
('Avenida Siempre Viva 456', 'Martes 15:00', '555-5678', 1),
('Boulevard Broken Dreams 789', 'Miércoles 09:00', '555-9101', 0);

-- Creación de la tabla Horarios_pub
CREATE TABLE Horarios_pub (
    Cuando TEXT NOT NULL,
    Horario_apertura1 TEXT NOT NULL,
    Horario_cierre1 TEXT NOT NULL,
    Horario_apertura2 TEXT,
    Horario_cierre2 TEXT
);

-- Insertar datos ficticios en la tabla Horarios_pub
INSERT INTO Horarios_pub (Cuando, Horario_apertura1, Horario_cierre1, Horario_apertura2, Horario_cierre2) VALUES
('Lunes a Viernes', '9:00', '13:00', '17:00', '21:00'),
('Sabado', '10:00', '14:00', NULL, NULL);

-- Creación de la tabla Tels
CREATE TABLE Tels (
    telefono TEXT NOT NULL
);

-- Insertar datos ficticios en la tabla Tels
INSERT INTO Tels (telefono) VALUES
('555-2222'),
('555-3333'),
('555-4444');
