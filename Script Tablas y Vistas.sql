
-- Activar claves foráneas
PRAGMA foreign_keys = ON;

-- Tabla de rutas
CREATE TABLE Ruta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    nombre VARCHAR(255) NOT NULL,
    origen VARCHAR(255) NOT NULL,
    destino VARCHAR(255) NOT NULL
);

-- Tabla de paradas
CREATE TABLE Parada (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre VARCHAR(255) NOT NULL,
    ciudad VARCHAR(255) NOT NULL
);

-- Tabla intermedia Ruta-Parada
CREATE TABLE RutaParadas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ruta_id INTEGER NOT NULL,
    parada_id INTEGER NOT NULL,
    orden INTEGER NOT NULL,
    FOREIGN KEY (ruta_id) REFERENCES Ruta(id),
    FOREIGN KEY (parada_id) REFERENCES Parada(id)
);

-- Tabla de buses
CREATE TABLE Bus (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patente VARCHAR(6) NOT NULL UNIQUE, -- Se limita a 6 ya que es el máximo de caracteres que puede tener la patente de un bus en chile
    modelo VARCHAR(255),
    capacidad INTEGER NOT NULL
);

-- Tabla de choferes
CREATE TABLE Chofer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rut VARCHAR(12) NOT NULL UNIQUE, -- Formato: 12.345.678-9
    nombre VARCHAR(255) NOT NULL ,
    telefono VARCHAR(20),
    email VARCHAR(255)
);

-- Tabla de clientes
CREATE TABLE Cliente (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rut VARCHAR(12) NOT NULL UNIQUE, -- Formato: 12.345.678-9
    nombre VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    telefono VARCHAR(20),
    direccion VARCHAR(255)
);

-- Tabla de servicios
CREATE TABLE Servicio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    ruta_id INTEGER NOT NULL,
    bus_id INTEGER NOT NULL,
    chofer_id INTEGER NOT NULL,
    fecha_salida TEXT NOT NULL, -- Formato: YYYY-MM-DD HH:MM
    fecha_llegada TEXT, -- Formato: YYYY-MM-DD HH:MM
    FOREIGN KEY (ruta_id) REFERENCES Ruta(id),
    FOREIGN KEY (bus_id) REFERENCES Bus(id),
    FOREIGN KEY (chofer_id) REFERENCES Chofer(id)
);

-- Tabla de tarifas
CREATE TABLE Tarifa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ruta_id INTEGER NOT NULL,
    nombre VARCHAR(255),
    monto INTEGER NOT NULL,
    fecha_inicio TEXT, -- Formato: YYYY-MM-DD HH:MM
    fecha_fin TEXT, -- Formato: YYYY-MM-DD HH:MM
    FOREIGN KEY (ruta_id) REFERENCES Ruta(id)
);

-- Tabla de boletos
CREATE TABLE Boleto (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo VARCHAR(20) NOT NULL UNIQUE,
    servicio_id INTEGER NOT NULL,
    cliente_id INTEGER NOT NULL,
    asiento INTEGER NOT NULL,
    precio INTEGER NOT NULL,
    FOREIGN KEY (servicio_id) REFERENCES Servicio(id),
    FOREIGN KEY (cliente_id) REFERENCES Cliente(id)
);

-- Tabla de pagos
CREATE TABLE Pago (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    boleto_id INTEGER NOT NULL UNIQUE,
    monto INTEGER NOT NULL ,
    fecha_pago TEXT, -- Formato: YYYY-MM-DD HH:MM
    metodo VARCHAR(13) NOT NULL, -- 'Efectivo', 'Debito', 'Credito', 'Transferencia'
    FOREIGN KEY (boleto_id) REFERENCES Boleto(id)
);



-- CREACIÓN DE ÍNDICES

-- Índice para búsquedas por código de ruta
CREATE INDEX idx_ruta_codigo ON Ruta(codigo);

-- Índice compuesto para secuencia de paradas de una ruta
CREATE INDEX idx_rutaparadas_ruta_orden ON RutaParadas(ruta_id, orden);

-- Índice para búsquedas por patente de bus
CREATE INDEX idx_bus_patente ON Bus(patente);

-- Índice para consultas por RUT del chofer
CREATE INDEX idx_chofer_rut ON Chofer(rut);

-- Índices para mejorar consultas en la tabla Servicio
CREATE INDEX idx_servicio_ruta ON Servicio(ruta_id);
CREATE INDEX idx_servicio_bus ON Servicio(bus_id);
CREATE INDEX idx_servicio_chofer ON Servicio(chofer_id);
CREATE INDEX idx_servicio_salida ON Servicio(fecha_salida);

-- Índice para localizar clientes por RUT
CREATE INDEX idx_cliente_rut ON Cliente(rut);

-- Índice compuesto para determinar tarifas vigentes
CREATE INDEX idx_tarifa_ruta_vigencia ON Tarifa(ruta_id, fecha_inicio, fecha_fin);

-- Índices para reportes de ventas en boletos
CREATE INDEX idx_boleto_servicio ON Boleto(servicio_id);
CREATE INDEX idx_boleto_cliente ON Boleto(cliente_id);



-- CREACIÓN DE VISTAS

-- Vista: boletos vendidos por servicio
CREATE VIEW vw_boletos_por_servicio AS
SELECT s.id AS servicio_id, s.codigo, COUNT(b.id) AS boletos_vendidos
FROM Servicio s
LEFT JOIN Boleto b ON s.id = b.servicio_id
GROUP BY s.id;

-- Vista: ingresos totales por ruta
CREATE VIEW vw_ingresos_ruta AS
SELECT r.nombre AS ruta, SUM(p.monto) AS total_ingresos
FROM Ruta r
JOIN Servicio s ON s.ruta_id = r.id
JOIN Boleto b ON b.servicio_id = s.id
JOIN Pago p ON p.boleto_id = b.id
GROUP BY r.id;









