-- Create Database
CREATE DATABASE IF NOT EXISTS pmo_db;
USE pmo_db;

-- 1. Departamento
CREATE TABLE IF NOT EXISTS departamento (
    departamento_id INT PRIMARY KEY,
    nombre_departamento VARCHAR(100)
);

-- 2. Rol
CREATE TABLE IF NOT EXISTS rol (
    rol_id INT PRIMARY KEY,
    nombre_rol VARCHAR(100)
);

-- 3. Empleado
CREATE TABLE IF NOT EXISTS empleado (
    empleado_id INT PRIMARY KEY,
    nombre VARCHAR(150),
    rol_id INT,
    departamento_id INT,
    FOREIGN KEY (rol_id) REFERENCES rol(rol_id),
    FOREIGN KEY (departamento_id) REFERENCES departamento(departamento_id)
);

-- 4. Cliente
CREATE TABLE IF NOT EXISTS cliente (
    cliente_id INT PRIMARY KEY,
    nombre VARCHAR(150),
    sector VARCHAR(100),
    pais VARCHAR(100)
);

-- 5. Tipo Proyecto
CREATE TABLE IF NOT EXISTS tipo_proyecto (
    tipo_proyecto_id INT PRIMARY KEY,
    nombre VARCHAR(100)
);

-- 6. Estado
CREATE TABLE IF NOT EXISTS estado (
    estado_id INT PRIMARY KEY,
    nombre_estado VARCHAR(50)
);

-- 7. Catalogo Tareas (needed before Proyecto due to FK in some designs, or Proyecto first? 
-- In the generator, Proyecto has catalogo_id, and Catalogo has catalogo_id. 
-- Usually 1:1. Let's create Catalogo first if Proyecto references it, or vice versa.
-- Generator: df_proyecto["catalogo_id"] = df_proyecto["proyecto_id"]. 
-- Let's create Catalogo first.)
CREATE TABLE IF NOT EXISTS catalogo_tareas (
    catalogo_id INT PRIMARY KEY,
    nombre_catalogo VARCHAR(150)
);

-- 8. Proyecto
CREATE TABLE IF NOT EXISTS proyecto (
    proyecto_id INT PRIMARY KEY,
    nombre VARCHAR(150),
    descripcion TEXT,
    fecha_inicio_plan DATE,
    fecha_fin_plan DATE,
    fecha_inicio_real DATE,
    fecha_fin_real DATE,
    horas_planificadas INT, -- mapped from horas_totales
    horas_trabajadas INT,
    estado_id INT,
    tipo_proyecto_id INT,
    cliente_id INT,
    defectos_detectados INT,
    catalogo_id INT,
    metadata_extraccion BOOLEAN DEFAULT 0,
    FOREIGN KEY (estado_id) REFERENCES estado(estado_id),
    FOREIGN KEY (tipo_proyecto_id) REFERENCES tipo_proyecto(tipo_proyecto_id),
    FOREIGN KEY (cliente_id) REFERENCES cliente(cliente_id),
    FOREIGN KEY (catalogo_id) REFERENCES catalogo_tareas(catalogo_id)
);

-- 9. Tarea
CREATE TABLE IF NOT EXISTS tarea (
    tarea_id INT PRIMARY KEY,
    nombre_tarea VARCHAR(150),
    tipo_tarea VARCHAR(50),
    prioridad VARCHAR(20),
    completada BOOLEAN,
    fecha_entrega DATE,
    fecha_completado DATE,
    catalogo_tareas_id INT,
    metadata_extraccion BOOLEAN DEFAULT 0,
    FOREIGN KEY (catalogo_tareas_id) REFERENCES catalogo_tareas(catalogo_id)
);

-- 10. Proyecto Empleado (Asignaciones)
CREATE TABLE IF NOT EXISTS proyecto_empleado (
    proyecto_id INT,
    empleado_id INT,
    metadata_extraccion BOOLEAN DEFAULT 0,
    PRIMARY KEY (proyecto_id, empleado_id),
    FOREIGN KEY (proyecto_id) REFERENCES proyecto(proyecto_id),
    FOREIGN KEY (empleado_id) REFERENCES empleado(empleado_id)
);

-- 11. Finanzas Proyecto
CREATE TABLE IF NOT EXISTS finanzas_proyecto (
    id INT PRIMARY KEY,
    proyecto_id INT,
    monto_presupuestado DECIMAL(15,2),
    monto_real_acumulado DECIMAL(15,2),
    ingreso_proyecto DECIMAL(15,2),
    metadata_extraccion BOOLEAN DEFAULT 0,
    FOREIGN KEY (proyecto_id) REFERENCES proyecto(proyecto_id)
);

-- 12. Tipo Defecto
CREATE TABLE IF NOT EXISTS tipo_defecto (
    tipo_defecto_id INT PRIMARY KEY,
    categoria VARCHAR(100),
    subtipo VARCHAR(100)
);

-- 13. Fase SDLC
CREATE TABLE IF NOT EXISTS fase_sdlc (
    fase_id INT PRIMARY KEY,
    nombre_fase VARCHAR(100)
);

-- 14. Defecto
CREATE TABLE IF NOT EXISTS defecto (
    defecto_id INT PRIMARY KEY,
    proyecto_id INT,
    tipo_defecto_id INT,
    fase_id INT,
    severidad VARCHAR(20),
    descripcion TEXT,
    fecha_registro DATE,
    metadata_extraccion BOOLEAN DEFAULT 0,
    FOREIGN KEY (proyecto_id) REFERENCES proyecto(proyecto_id),
    FOREIGN KEY (tipo_defecto_id) REFERENCES tipo_defecto(tipo_defecto_id),
    FOREIGN KEY (fase_id) REFERENCES fase_sdlc(fase_id)
);
