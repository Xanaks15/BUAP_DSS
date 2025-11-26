# BUAP DSS - Sistema de Soporte a la Decisión

Este proyecto implementa un Sistema de Soporte a la Decisión (DSS) para una empresa de desarrollo de software. Incluye la generación de datos sintéticos, un proceso ETL (Extract, Transform, Load) incremental y un esquema de base de datos dimensional (SSD).

## Estructura del Proyecto

- **`generate_pmo_data.py`**: Script para generar datos sintéticos y poblar la base de datos transaccional (PMO).
- **`create_pmo_db.sql`**: Esquema SQL de la base de datos PMO.
- **`create_ssd_db.sql`**: Esquema SQL de la base de datos dimensional (SSD).
- **`setup_ssd.py`**: Script para inicializar la base de datos SSD.
- **`ETL-Proyecto/`**: Directorio que contiene el código del proceso ETL.
    - **`etl.py`**: Script principal del proceso ETL.
    - **`sql_queries/`**: Consultas SQL para extracción y carga.
- **`reset_flags.py`**: Utilidad para resetear las banderas de carga incremental en la PMO.
- **`verify_*.py`**: Scripts de verificación de datos y esquema.

## Requisitos

- Python 3.8+
- Librerías: `pandas`, `numpy`, `faker`, `scipy`

## Instrucciones de Uso

1.  **Generar Datos PMO**:
    ```bash
    python generate_pmo_data.py
    ```
2.  **Inicializar SSD**:
    ```bash
    python setup_ssd.py
    ```
3.  **Ejecutar ETL**:
    ```bash
    python ETL-Proyecto/ETL-Proyecto/etl.py
    ```

## Notas

- Las bases de datos SQLite (`pmo_db.sqlite` y `ssd_db.sqlite`) se generan localmente y están excluidas del control de versiones.
- El proceso ETL soporta carga incremental mediante la bandera `metadata_extraccion`.
