-- RUTAS
INSERT INTO Ruta (codigo, nombre, origen, destino) VALUES
('R001', 'Ruta Santiago - Valparaíso', 'Santiago', 'Valparaíso'),
('R002', 'Ruta Santiago - Chillán', 'Santiago', 'Chillán'),
('R003', 'Ruta Concepción - Temuco', 'Concepción', 'Temuco');

-- PARADAS
INSERT INTO Parada (nombre, ciudad) VALUES
('Terminal Alameda', 'Santiago'),
('Terminal Valparaíso', 'Valparaíso'),
('Terminal Chillán', 'Chillán'),
('Terminal Concepción', 'Concepción'),
('Terminal Temuco', 'Temuco');

-- BUSES
INSERT INTO Bus (patente, modelo, capacidad) VALUES
('ABCD12', 'Mercedes Benz O500', 45),
('BCDE34', 'Volvo B9R', 50),
('CDEF56', 'Scania K400', 48);

-- CHOFERES
INSERT INTO Chofer (rut, nombre, telefono, email) VALUES
('12.345.678-9', 'Juan Pérez', '+56977777777', 'juan.perez@empresa.cl'),
('15.987.654-3', 'Carlos López', '+56988888888', 'carlos.lopez@empresa.cl'),
('17.234.567-1', 'Andrés Muñoz', '+56999999999', 'andres.munoz@empresa.cl');

-- CLIENTES
INSERT INTO Cliente (rut, nombre, email, telefono, direccion) VALUES
('20.123.456-7', 'Beatriz Carvajal', 'bcarvajal@gmail.com', '+56955555555', 'Providencia 123, Santiago'),
('21.765.432-1', 'Cristian Valenzuela', 'cvalenzuela@gmail.com', '+56955553333', 'Centro 456, Chillán'),
('22.456.789-2', 'Felipe Muñoz', 'fmunoz@gmail.com', '+56955551111', 'Aníbal Pinto 789, Concepción');

-- SERVICIOS
INSERT INTO Servicio (codigo, ruta_id, bus_id, chofer_id, fecha_salida, fecha_llegada) VALUES
('S001', 1, 1, 1, '2025-10-22 08:00', '2025-10-22 10:15'),
('S002', 2, 2, 2, '2025-10-22 09:30', '2025-10-22 13:00'),
('S003', 3, 3, 3, '2025-10-23 07:00', '2025-10-23 09:30');

-- TARIFAS
INSERT INTO Tarifa (ruta_id, nombre, monto, fecha_inicio, fecha_fin) VALUES
(1, 'Temporada baja', 8500, '2025-09-01', '2025-11-30'),
(2, 'Temporada baja', 12000, '2025-09-01', '2025-11-30'),
(3, 'Temporada baja', 10500, '2025-09-01', '2025-11-30');

-- BOLETOS
INSERT INTO Boleto (codigo, servicio_id, cliente_id, asiento, precio) VALUES
('B001', 1, 1, 5, 8500),
('B002', 1, 2, 6, 8500),
('B003', 2, 3, 10, 12000),
('B004', 3, 1, 8, 10500);

-- PAGOS
INSERT INTO Pago (boleto_id, monto, fecha_pago, metodo) VALUES
(1, 8500, '2025-10-20', 'Debito'),
(2, 8500, '2025-10-20', 'Efectivo'),
(3, 12000, '2025-10-21', 'Credito'),
(4, 10500, '2025-10-21', 'Transferencia');

-- RUTA-PARADAS (asignación de paradas a rutas con orden)
INSERT INTO RutaParadas (ruta_id, parada_id, orden) VALUES
(1, 1, 1),  -- Ruta R001: Terminal Alameda (Santiago)
(1, 2, 2),  -- Ruta R001: Terminal Valparaíso (Valparaíso)
(2, 1, 1),  -- Ruta R002: Terminal Alameda (Santiago)
(2, 3, 2),  -- Ruta R002: Terminal Chillán (Chillán)
(3, 4, 1),  -- Ruta R003: Terminal Concepción (Concepción)
(3, 5, 2);  -- Ruta R003: Terminal Temuco (Temuco)