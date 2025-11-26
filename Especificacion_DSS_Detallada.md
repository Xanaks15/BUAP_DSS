# Especificación Analítica para Implementación del DSS

Este documento define, de forma operativa y orientada a implementación, los componentes analíticos que deben construirse encima de las bases de datos PMO y SSD: cubos OLAP, conjunto de KPI para el dashboard, Balanced Scorecard (OKRs) y el modelo predictivo de defectos basado en distribución de Rayleigh. Todas las referencias a tablas y columnas corresponden al esquema de la base de datos SSD.

## 1. Definición de Cubos OLAP

Se trabajará al menos con dos cubos OLAP lógicos:
• **CuboProyecto** (principal, centrado en proyectos).
• **CuboDefecto** (centrado en defectos, para calidad).

### 1.1 CuboProyecto

**Tabla de hechos base**: `fact_proyecto`

| Elemento | Definición |
| :--- | :--- |
| **Grano (granularity)** | Una fila por proyecto cargado en SSD. Identificado por `fact_proyecto.fact_id` y mapeado al proyecto operativo por `fact_proyecto.proyecto_id`. |
| **Tabla de hechos** | `fact_proyecto(fact_id, proyecto_id, nombre, descripcion, horas_planificadas, horas_trabajadas, monto_planificado, monto_real, ganancia_proyecto, tareas_planificadas, tareas_completadas, tareas_retrasadas, empleados_asignados, roi, tuct, fecha_inicio_plan, fecha_fin_plan, fecha_inicio_real, fecha_fin_real, estado_id, tipo_proyecto_id, cliente_id)`. |
| **Dimensiones conectadas** | Tiempo (`dim_tiempo` → `dim_dia` → `dim_mes` → `dim_anio`) usando roles de `fecha_inicio_plan`, `fecha_fin_plan`, `fecha_inicio_real`, `fecha_fin_real`.<br>Estado del proyecto (`dim_estado`).<br>Tipo de proyecto (`dim_tipo_proyecto`).<br>Cliente (`dim_cliente`). |
| **Medidas básicas (almacenadas)** | `horas_planificadas`, `horas_trabajadas`, `monto_planificado`, `monto_real`, `ganancia_proyecto`, `tareas_planificadas`, `tareas_completadas`, `tareas_retrasadas`, `empleados_asignados`, `roi`, `tuct`. |
| **Medidas derivadas (cálculo en capa OLAP)** | `desviacion_horas` = `horas_trabajadas` - `horas_planificadas`.<br>`desviacion_monto` = `monto_real` - `monto_planificado`.<br>`%_cumplimiento_tareas` = `tareas_completadas` / `tareas_planificadas`.<br>`%_retrasos` = `tareas_retrasadas` / `tareas_planificadas`.<br>`costo_real_vs_plan_pct` = `monto_real` / `monto_planificado`.<br>`horas_reales_vs_plan_pct` = `horas_trabajadas` / `horas_planificadas`. |

El motor OLAP deberá soportar operaciones de slice, dice, drill-down y roll-up sobre las dimensiones declaradas, permitiendo análisis por año/mes/día, por tipo de proyecto, estado y cliente.

### 1.2 CuboDefecto

**Tabla de hechos base**: `fact_defecto`

| Elemento | Definición |
| :--- | :--- |
| **Grano (granularity)** | Una fila por defecto registrado en SSD. Identificado por `fact_defecto.defecto_id`. |
| **Tabla de hechos** | `fact_defecto(defecto_id, proyecto_id, tipo_defecto_id, fase_sdlc_id, severidad, tiempo_id, count_defecto)`. |
| **Dimensiones conectadas** | Tiempo del defecto (`dim_tiempo` → `dim_dia` → `dim_mes` → `dim_anio`) vía `tiempo_id`.<br>Tipo de defecto (`dim_tipo_defecto`).<br>Fase del SDLC (`dim_fase_sdlc`).<br>Proyecto (join a `fact_proyecto` por `proyecto_id`), y a través de él tipo de proyecto, estado y cliente. |
| **Medidas básicas** | `count_defecto` (siempre 1 por defecto, pero se suma para obtener agregados). |
| **Medidas derivadas** | `defectos_totales` = `SUM(count_defecto)`.<br>`defectos_criticos` = `SUM(CASE WHEN severidad = 'Alta' THEN 1 ELSE 0 END)`.<br>`defectos_por_proyecto` = `SUM(count_defecto) GROUP BY proyecto_id`.<br>`defectos_por_fase` = `SUM(count_defecto) GROUP BY fase_sdlc_id`.<br>`defectos_por_tipo` = `SUM(count_defecto) GROUP BY tipo_defecto_id`. |

Este cubo servirá como base para KPI de calidad y para alimentar el modelo predictivo de defectos.

## 2. KPIs para el Dashboard

A continuación se define un catálogo de KPIs que el dashboard deberá mostrar. Cada KPI incluye nombre, descripción funcional, fórmula a nivel consulta y origen de datos en términos de tablas/columnas del SSD.

| KPI | Descripción | Fórmula (nivel consulta) | Origen en SSD |
| :--- | :--- | :--- | :--- |
| **Porcentaje de proyectos entregados a tiempo** | Mide el porcentaje de proyectos cuya `fecha_fin_real` es menor o igual a `fecha_fin_plan`. | `KPI = (COUNT(proyectos WHERE fecha_fin_real <= fecha_fin_plan) / COUNT(*)) * 100` | `fact_proyecto(fecha_fin_plan, fecha_fin_real)` |
| **Horas reales vs planificadas (%)** | Mide en qué proporción las horas trabajadas se ajustan a las horas planificadas. | `KPI = (SUM(horas_trabajadas) / SUM(horas_planificadas)) * 100` | `fact_proyecto(horas_trabajadas, horas_planificadas)` |
| **Costo real vs planificado (%)** | Compara el costo real del proyecto contra el monto planificado. | `KPI = (SUM(monto_real) / SUM(monto_planificado)) * 100` | `fact_proyecto(monto_real, monto_planificado)` |
| **ROI promedio** | Retorno de inversión promedio de los proyectos en el periodo. | `KPI = AVG(roi)` | `fact_proyecto(roi)` |
| **Ganancia total** | Suma de la ganancia de todos los proyectos en el periodo. | `KPI = SUM(ganancia_proyecto)` | `fact_proyecto(ganancia_proyecto)` |
| **Porcentaje de tareas completadas** | Mide el porcentaje de tareas completadas respecto al total planificado. | `KPI = (SUM(tareas_completadas) / SUM(tareas_planificadas)) * 100` | `fact_proyecto(tareas_completadas, tareas_planificadas)` |
| **Porcentaje de tareas retrasadas** | Mide el porcentaje de tareas retrasadas respecto al total planificado. | `KPI = (SUM(tareas_retrasadas) / SUM(tareas_planificadas)) * 100` | `fact_proyecto(tareas_retrasadas, tareas_planificadas)` |
| **Empleados asignados promedio** | Cantidad promedio de empleados asignados por proyecto. | `KPI = AVG(empleados_asignados)` | `fact_proyecto(empleados_asignados)` |
| **Defectos totales por periodo** | Número total de defectos registrados en el periodo seleccionado. | `KPI = SUM(count_defecto)` | `fact_defecto(count_defecto), dim_tiempo` |
| **Defectos críticos por periodo** | Número total de defectos con severidad 'Alta'. | `KPI = SUM(CASE WHEN severidad = 'Alta' THEN 1 ELSE 0 END)` | `fact_defecto(severidad, count_defecto)` |
| **Defectos por fase SDLC** | Número de defectos agrupados por fase del ciclo de vida. | `KPI = SUM(count_defecto) GROUP BY fase_sdlc_id` | `fact_defecto(fase_sdlc_id, count_defecto), dim_fase_sdlc` |

El dashboard deberá implementar filtros estándar por rango de fechas (`dim_tiempo`), tipo de proyecto (`dim_tipo_proyecto`), estado (`dim_estado`) y cliente (`dim_cliente`). Los KPIs se recalcularán dinámicamente según los filtros activos.

## 3. Balanced Scorecard (BSC) y OKRs

El BSC se estructura en cuatro perspectivas: Financiera, Cliente, Procesos Internos, y Aprendizaje y Crecimiento. Cada objetivo tendrá uno o más Key Results (OKRs) asociados a métricas obtenibles desde el SSD.

### 3.1 Perspectiva Financiera

| Objetivo | Key Result | Métrica / Fórmula | Origen en SSD |
| :--- | :--- | :--- | :--- |
| **F1. Asegurar la rentabilidad de los proyectos.** | **F1.1** ROI promedio ≥ 12%. | `AVG(roi) >= 0.12` | `fact_proyecto(roi)` |
| **F1. Asegurar la rentabilidad de los proyectos.** | **F1.2** Desviación de costos ≤ 10%. | `AVG(ABS(monto_real - monto_planificado) / monto_planificado) <= 0.10` | `fact_proyecto(monto_real, monto_planificado)` |
| **F1. Asegurar la rentabilidad de los proyectos.** | **F1.3** ≥ 85% de proyectos con `ganancia_proyecto > 0`. | `COUNT(proyectos con ganancia_proyecto > 0) / COUNT(*) >= 0.85` | `fact_proyecto(ganancia_proyecto)` |

### 3.2 Perspectiva Cliente

| Objetivo | Key Result | Métrica / Fórmula | Origen en SSD |
| :--- | :--- | :--- | :--- |
| **C1. Entregar productos confiables y a tiempo.** | **C1.1** ≥ 90% de proyectos entregados a tiempo. | `COUNT(proyectos con fecha_fin_real <= fecha_fin_plan) / COUNT(*) >= 0.90` | `fact_proyecto(fecha_fin_plan, fecha_fin_real)` |
| **C1. Entregar productos confiables y a tiempo.** | **C1.2** ≥ 95% de proyectos sin defectos críticos. | `COUNT(proyectos con defectos_criticos = 0) / COUNT(*) >= 0.95` | `fact_proyecto(defectos_criticos)` o join con `fact_defecto` |
| **C1. Entregar productos confiables y a tiempo.** | **C1.3** ≥ 80% de proyectos con porcentaje de tareas retrasadas ≤ 20%. | `COUNT(proyectos con (tareas_retrasadas / tareas_planificadas) <= 0.20) / COUNT(*) >= 0.80` | `fact_proyecto(tareas_retrasadas, tareas_planificadas)` |

### 3.3 Perspectiva Procesos Internos

| Objetivo | Key Result | Métrica / Fórmula | Origen en SSD |
| :--- | :--- | :--- | :--- |
| **P1. Optimizar el proceso de desarrollo y pruebas.** | **P1.1** Defectos promedio por proyecto ≤ 25. | `SUM(count_defecto) / COUNT(DISTINCT proyecto_id) <= 25` | `fact_defecto(count_defecto, proyecto_id)` |
| **P1. Optimizar el proceso de desarrollo y pruebas.** | **P1.2** ≥ 90% de tareas completadas. | `SUM(tareas_completadas) / SUM(tareas_planificadas) >= 0.90` | `fact_proyecto(tareas_completadas, tareas_planificadas)` |
| **P1. Optimizar el proceso de desarrollo y pruebas.** | **P1.3** Pico de defectos dentro del primer 40% de la duración del proyecto. | Validar con distribución Rayleigh histórica: `t_peak / duracion_proyecto <= 0.40` | `fact_defecto(tiempo_id)` + `fact_proyecto(fechas, horas_totales)` |

### 3.4 Perspectiva Aprendizaje y Crecimiento

| Objetivo | Key Result | Métrica / Fórmula | Origen en SSD |
| :--- | :--- | :--- | :--- |
| **A1. Fortalecer la capacidad del equipo.** | **A1.1** Productividad de horas ≥ 85%. | `SUM(horas_trabajadas) / SUM(horas_planificadas) >= 0.85` | `fact_proyecto(horas_trabajadas, horas_planificadas)` |
| **A1. Fortalecer la capacidad del equipo.** | **A1.2** Uso del modelo predictivo en ≥ 70% de nuevos proyectos. | `COUNT(DISTINCT proyecto_id en fact_prediccion_proyecto) / COUNT(DISTINCT proyecto_id de proyectos nuevos) >= 0.70` | `fact_prediccion_proyecto(proyecto_id)`, `fact_proyecto(proyecto_id, estado_id)` |

## 4. Modelo Predictivo de Defectos (Distribución de Rayleigh)

El objetivo del modelo es estimar el número total de defectos esperados para un nuevo proyecto y la distribución temporal de dichos defectos, utilizando la distribución de Rayleigh. Los resultados se almacenan en la tabla `fact_prediccion_proyecto`.

### 4.1 Entradas del modelo

Entradas que deberá proporcionar la interfaz de usuario (formulario):
• `tipo_proyecto_id` (INT): se selecciona desde `dim_tipo_proyecto`.
• `horas_estimadas` (DECIMAL(10,2)): horas totales estimadas del proyecto.
• `duracion_semanas` (INT): duración estimada del proyecto en semanas.
• `complejidad` (VARCHAR): valor categórico como 'baja', 'media', 'alta'.
• `proyecto_id` (INT, opcional): si ya existe un registro en PMO/SSD para este proyecto.

### 4.2 Cálculo de parámetros

El modelo calculará los siguientes parámetros intermedios con base en las entradas:

1. **Cálculo de sigma (σ)**:
    `sigma = duracion_semanas / 2.5`
2. **Cálculo del tiempo pico de defectos (t_peak)**:
    `t_peak = sigma * sqrt(2)`

El valor de sigma controla la dispersión temporal de los defectos; t_peak indica la semana en la que se espera el máximo de defectos reportados.

Para el número total de defectos esperados (K), se recomienda calibrar el modelo a partir de historial:
    `defectos_por_hora = SUM(defectos_reales) / SUM(horas_trabajadas)`
    `total_defectos_estimado = defectos_por_hora * horas_estimadas`

donde:
  • `defectos_reales` se obtiene de `SUM(count_defecto)` en `fact_defecto` para proyectos terminados.
  • `horas_trabajadas` se obtiene de `fact_proyecto.horas_trabajadas`.

### 4.3 Distribución de Rayleigh

Sea `t` el tiempo en semanas desde el inicio del proyecto. La distribución de Rayleigh se define como:

**Función de densidad de probabilidad (defectos por unidad de tiempo)**:
    `f(t) = (t / sigma^2) * exp( -t^2 / (2 * sigma^2) )`

**Función de distribución acumulada (proporción de defectos acumulados hasta t)**:
    `F(t) = 1 - exp( -t^2 / (2 * sigma^2) )`

Entonces, el número de defectos acumulados hasta la semana `t` se aproxima como:
    `defectos_acumulados(t) = total_defectos_estimado * F(t)`

Para construir la curva de defectos por semana, se evalúa `f(t)` y/o `defectos_acumulados(t)` para `t = 1, 2, ..., duracion_semanas`.

### 4.4 Persistencia de la predicción en fact_prediccion_proyecto

Cada ejecución del modelo deberá generar un registro en la tabla `fact_prediccion_proyecto` con la siguiente correspondencia de columnas:

| Columna en `fact_prediccion_proyecto` | Contenido esperado |
| :--- | :--- |
| `proyecto_id` | Identificador del proyecto (si existe en SSD); NULL si es una simulación para un proyecto aún no creado. |
| `tiempo_id` | `tiempo_id` correspondiente a la fecha estimada de inicio del proyecto (`dim_tiempo`). |
| `tipo_proyecto_id` | Tipo de proyecto seleccionado en el formulario. |
| `horas_estimadas` | Valor ingresado en el formulario. |
| `duracion_semanas` | Valor ingresado en el formulario. |
| `complejidad` | Valor categórico ingresado en el formulario. |
| `sigma_parametro` | Valor de sigma calculado por el modelo. |
| `tiempo_pico` | Valor de `t_peak` calculado por el modelo. |
| `total_defectos_estimado` | Valor K calculado a partir de `defectos_por_hora * horas_estimadas`. |
| `tiempo_prediccion_id` | `tiempo_id` correspondiente al día en que se ejecuta la predicción (`dim_tiempo`). |

El modelo no necesita almacenar la curva completa de Rayleigh en la base de datos; esa curva puede calcularse en tiempo de ejecución en la aplicación usando los parámetros `sigma_parametro`, `total_defectos_estimado` y la duración del proyecto.
