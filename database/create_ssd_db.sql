
/*=========================================
  DIMENSIONES EXISTENTES (DEL SSD ORIGINAL)
=========================================*/

CREATE TABLE IF NOT EXISTS dim_estado (
    estado_id INT PRIMARY KEY,
    nombre_estado VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS dim_tipo_proyecto (
    tipo_proyecto_id INT PRIMARY KEY,
    nombre VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS dim_anio (
    anio_id INT PRIMARY KEY,
    anio INT
);

CREATE TABLE IF NOT EXISTS dim_mes (
    mes_id INT PRIMARY KEY,
    nombre_mes VARCHAR(255),
    numero_mes INT,
    trimestre INT,
    anio_id INT,
    FOREIGN KEY (anio_id) REFERENCES dim_anio(anio_id)
);

CREATE TABLE IF NOT EXISTS dim_dia (
    dia_id INT PRIMARY KEY,
    nombre_dia VARCHAR(255),
    numero_dia INT,
    mes_id INT,
    FOREIGN KEY (mes_id) REFERENCES dim_mes(mes_id)
);

CREATE TABLE IF NOT EXISTS dim_tiempo (
    tiempo_id INT PRIMARY KEY,
    fecha DATE,
    dia_id INT,
    FOREIGN KEY (dia_id) REFERENCES dim_dia(dia_id)
);

/*=========================================
   NUEVA DIMENSIÓN: CLIENTE
=========================================*/
CREATE TABLE IF NOT EXISTS dim_cliente (
    cliente_id INT PRIMARY KEY,
    nombre_cliente VARCHAR(255),
    sector VARCHAR(255),
    pais VARCHAR(255)
);

/*=========================================
   NUEVAS DIMENSIONES PARA DEFECTOS
=========================================*/
CREATE TABLE IF NOT EXISTS dim_tipo_defecto (
    tipo_defecto_id INT PRIMARY KEY,
    nombre_tipo_defecto VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS dim_fase_sdlc (
    fase_sdlc_id INT PRIMARY KEY,
    nombre_fase VARCHAR(255)
);

/*=========================================
  FACT: PROYECTO (SSD ORIGINAL)
  → SOLO LE AGREGAMOS proyecto_id (PMO)
=========================================*/
CREATE TABLE IF NOT EXISTS fact_proyecto (
    fact_id INT PRIMARY KEY,
    
    /* === NUEVO CAMPO PARA COMPATIBILIDAD PMO === */
    proyecto_id INT,

    nombre VARCHAR(255),
    descripcion VARCHAR(255),
    horas_planificadas DECIMAL(10,2),
    horas_trabajadas DECIMAL(10,2),
    monto_planificado DECIMAL(10,2),
    monto_real DECIMAL(10,2),
    ganancia_proyecto DECIMAL(10,2),
    tareas_planificadas INT,
    tareas_completadas INT,
    tareas_retrasadas INT,
    empleados_asignados INT,
    roi DECIMAL(10,2),
    tuct DECIMAL(10,2),

    fecha_inicio_plan INT,
    fecha_fin_plan INT,
    fecha_inicio_real INT,
    fecha_fin_real INT,

    estado_id INT,
    tipo_proyecto_id INT,
    cliente_id INT NULL,

    FOREIGN KEY (fecha_inicio_plan) REFERENCES dim_tiempo(tiempo_id),
    FOREIGN KEY (fecha_fin_plan) REFERENCES dim_tiempo(tiempo_id),
    FOREIGN KEY (fecha_inicio_real) REFERENCES dim_tiempo(tiempo_id),
    FOREIGN KEY (fecha_fin_real) REFERENCES dim_tiempo(tiempo_id),

    FOREIGN KEY (estado_id) REFERENCES dim_estado(estado_id),
    FOREIGN KEY (tipo_proyecto_id) REFERENCES dim_tipo_proyecto(tipo_proyecto_id),
    FOREIGN KEY (cliente_id) REFERENCES dim_cliente(cliente_id),
    
    UNIQUE (proyecto_id)
);

/*=========================================
   FACT: DEFECTO (NUEVA)
   → AHORA REFERENCIA proyecto_id (PMO)
=========================================*/
CREATE TABLE IF NOT EXISTS fact_defecto (
    defecto_id INTEGER PRIMARY KEY AUTOINCREMENT, -- SQLite syntax
    proyecto_id INT NOT NULL,
    tipo_defecto_id INT,
    fase_sdlc_id INT,
    severidad VARCHAR(50),
    tiempo_id INT,
    count_defecto INT DEFAULT 1,

    FOREIGN KEY (proyecto_id) REFERENCES fact_proyecto(proyecto_id),
    FOREIGN KEY (tipo_defecto_id) REFERENCES dim_tipo_defecto(tipo_defecto_id),
    FOREIGN KEY (fase_sdlc_id) REFERENCES dim_fase_sdlc(fase_sdlc_id),
    FOREIGN KEY (tiempo_id) REFERENCES dim_tiempo(tiempo_id)
);



