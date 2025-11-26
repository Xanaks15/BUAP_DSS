from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from .database import Base

class FactProyecto(Base):
    __tablename__ = "fact_proyecto"

    fact_id = Column(Integer, primary_key=True, index=True)
    proyecto_id = Column(Integer)
    nombre = Column(String(150))
    descripcion = Column(String)
    horas_planificadas = Column(Integer)
    horas_trabajadas = Column(Integer)
    monto_planificado = Column(DECIMAL(15, 2))
    monto_real = Column(DECIMAL(15, 2))
    ganancia_proyecto = Column(DECIMAL(15, 2))
    tareas_planificadas = Column(Integer)
    tareas_completadas = Column(Integer)
    tareas_retrasadas = Column(Integer)
    empleados_asignados = Column(Integer)
    roi = Column(Float)
    tuct = Column(Float)
    
    fecha_inicio_plan = Column(Integer, ForeignKey("dim_tiempo.tiempo_id"))
    fecha_fin_plan = Column(Integer, ForeignKey("dim_tiempo.tiempo_id"))
    fecha_inicio_real = Column(Integer, ForeignKey("dim_tiempo.tiempo_id"))
    fecha_fin_real = Column(Integer, ForeignKey("dim_tiempo.tiempo_id"))
    
    estado_id = Column(Integer, ForeignKey("dim_estado.estado_id"))
    tipo_proyecto_id = Column(Integer, ForeignKey("dim_tipo_proyecto.tipo_proyecto_id"))
    cliente_id = Column(Integer, ForeignKey("dim_cliente.cliente_id"))

    # Relationships
    estado = relationship("DimEstado")
    tipo_proyecto = relationship("DimTipoProyecto")
    cliente = relationship("DimCliente")


class DimEstado(Base):
    __tablename__ = "dim_estado"
    estado_id = Column(Integer, primary_key=True)
    nombre_estado = Column(String(50))

class DimTipoProyecto(Base):
    __tablename__ = "dim_tipo_proyecto"
    tipo_proyecto_id = Column(Integer, primary_key=True)
    nombre = Column(String(100))

class DimCliente(Base):
    __tablename__ = "dim_cliente"
    cliente_id = Column(Integer, primary_key=True)
    nombre_cliente = Column(String(150))
    sector = Column(String(100))
    pais = Column(String(100))

class DimTiempo(Base):
    __tablename__ = "dim_tiempo"
    tiempo_id = Column(Integer, primary_key=True)
    fecha = Column(Date)
    dia_id = Column(Integer)

class FactDefecto(Base):
    __tablename__ = "fact_defecto"
    fact_defecto_id = Column(Integer, primary_key=True) # Assuming auto-generated or composite
    # In schema it's composite (proyecto_id, tipo_defecto_id, fase_id, tiempo_id)
    # But SQLAlchemy needs a PK. Let's assume we can use composite PK or just map it.
    # For simplicity, let's map the columns.
    
    proyecto_id = Column(Integer, ForeignKey("fact_proyecto.proyecto_id"), primary_key=True)
    tipo_defecto_id = Column(Integer, ForeignKey("dim_tipo_defecto.tipo_defecto_id"), primary_key=True)
    fase_id = Column(Integer, ForeignKey("dim_fase_sdlc.fase_sdlc_id"), primary_key=True)
    tiempo_id = Column(Integer, ForeignKey("dim_tiempo.tiempo_id"), primary_key=True)
    severidad = Column(String(50))

class DimTipoDefecto(Base):
    __tablename__ = "dim_tipo_defecto"
    tipo_defecto_id = Column(Integer, primary_key=True)
    nombre_tipo_defecto = Column(String(100))

class DimFaseSDLC(Base):
    __tablename__ = "dim_fase_sdlc"
    fase_sdlc_id = Column(Integer, primary_key=True)
    nombre_fase = Column(String(100))
