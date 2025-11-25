CREATE DATABASE IF NOT EXISTS contabilidad_db;
USE contabilidad_db;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL UNIQUE,
    role VARCHAR(50) DEFAULT 'cliente',
    password VARCHAR(255)
);

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255) NOT NULL,
    rfc VARCHAR(20),
    regimen_fiscal VARCHAR(100)
);

CREATE TABLE transacciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cliente_id INT,
    fecha DATE DEFAULT '2025-01-01',
    concepto TEXT,
    monto DECIMAL(15,2),
    tipo_transaccion ENUM('ingreso', 'gasto'),
    FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
);