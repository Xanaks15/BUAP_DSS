-- extract_projects
SELECT p.proyecto_id,
       p.nombre,
       p.descripcion,
       p.fecha_inicio_plan,
       p.fecha_fin_plan,
       p.fecha_inicio_real,
       p.fecha_fin_real,
       p.horas_planificadas,
       p.horas_trabajadas,
       p.estado_id,
       p.tipo_proyecto_id,
       p.cliente_id,
       p.catalogo_id
FROM proyecto AS p
WHERE p.metadata_extraccion = 0;

-- extract_tasks
SELECT t.tarea_id,
       t.nombre_tarea,
       t.tipo_tarea,
       t.prioridad,
       t.completada,
       t.fecha_entrega,
       t.fecha_completado,
       t.catalogo_tareas_id
FROM tarea AS t
WHERE t.metadata_extraccion = 0;

-- extract_project_employees
SELECT pe.proyecto_id,
       pe.empleado_id
FROM proyecto_empleado AS pe
WHERE pe.metadata_extraccion = 0;

-- extract_states
SELECT e.estado_id,
       e.nombre_estado
FROM estado AS e;

-- extract_types
SELECT tp.tipo_proyecto_id,
       tp.nombre
FROM tipo_proyecto AS tp;

-- extract_finances
SELECT f.id,
       f.proyecto_id,
       f.monto_presupuestado,
       f.monto_real_acumulado,
       f.ingreso_proyecto
FROM finanzas_proyecto AS f
WHERE f.metadata_extraccion = 0;

-- extract_catalogues
SELECT c.catalogo_id,
       c.nombre_catalogo
FROM catalogo_tareas AS c;

-- extract_clients
SELECT c.cliente_id,
       c.nombre,
       c.sector,
       c.pais
FROM cliente AS c;

-- extract_defect_types
SELECT td.tipo_defecto_id,
       td.categoria,
       td.subtipo
FROM tipo_defecto AS td;

-- extract_phases
SELECT f.fase_id,
       f.nombre_fase
FROM fase_sdlc AS f;

-- extract_defects
SELECT d.defecto_id,
       d.proyecto_id,
       d.tipo_defecto_id,
       d.fase_id,
       d.severidad,
       d.fecha_registro
FROM defecto AS d
WHERE d.metadata_extraccion = 0;