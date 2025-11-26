-- load_dim_anio
INSERT IGNORE INTO dim_anio (anio_id, anio)
VALUES (%s, %s);

-- load_dim_mes
INSERT IGNORE INTO dim_mes (mes_id, nombre_mes, numero_mes, trimestre, anio_id)
VALUES (%s, %s, %s, %s, %s);

-- load_dim_dia
INSERT IGNORE INTO dim_dia (dia_id, nombre_dia, numero_dia, mes_id)
VALUES (%s, %s, %s, %s);

-- load_dim_tiempo
INSERT IGNORE INTO dim_tiempo (tiempo_id, fecha, dia_id)
VALUES (%s, %s, %s);

-- load_dim_estado
INSERT IGNORE INTO dim_estado (estado_id, nombre_estado)
VALUES (%s, %s);

-- load_dim_tipo_proyecto
INSERT IGNORE INTO dim_tipo_proyecto (tipo_proyecto_id, nombre)
VALUES (%s, %s);

-- load_fact_proyecto
INSERT IGNORE INTO fact_proyecto (
    fact_id,
    proyecto_id,
    nombre,
    descripcion,
    horas_planificadas,
    horas_trabajadas,
    monto_planificado,
    monto_real,
    ganancia_proyecto,
    tareas_planificadas,
    tareas_completadas,
    tareas_retrasadas,
    empleados_asignados,
    roi,
    tuct,
    fecha_inicio_plan,
    fecha_fin_plan,
    fecha_inicio_real,
    fecha_fin_real,
    estado_id,
    tipo_proyecto_id,
    cliente_id
)
VALUES (
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
    %s, %s
);

-- load_dim_cliente
INSERT IGNORE INTO dim_cliente (cliente_id, nombre_cliente, sector, pais)
VALUES (%s, %s, %s, %s);

-- load_dim_tipo_defecto
INSERT IGNORE INTO dim_tipo_defecto (tipo_defecto_id, nombre_tipo_defecto)
VALUES (%s, %s);

-- load_dim_fase_sdlc
INSERT IGNORE INTO dim_fase_sdlc (fase_sdlc_id, nombre_fase)
VALUES (%s, %s);

-- load_fact_defecto
INSERT IGNORE INTO fact_defecto (
    proyecto_id,
    tipo_defecto_id,
    fase_sdlc_id,
    severidad,
    tiempo_id,
    count_defecto
)
VALUES (%s, %s, %s, %s, %s, 1);
