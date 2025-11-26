import os
import random
from datetime import datetime, timedelta, date
from typing import Dict, List
import numpy as np
import pandas as pd
from scipy.stats import truncnorm

# ==== Configuration ====
OUTPUT_DIR = "./synthetic_output"
NUM_PROYECTOS = 1000
random.seed(42)
np.random.seed(42)

# Try to import Faker, else use SimpleFake
try:
    from faker import Faker
    _FAKER_AVAILABLE = True
except ImportError:
    _FAKER_AVAILABLE = False

class SimpleFake:
    def __init__(self):
        self.first_names = ["Juan","María","Luis","Ana","Carlos","Lucía","Miguel","Sofía","José","Carmen","Pedro","Laura","Jorge","Paula","Ricardo","Isabel","Fernando","Patricia"]
        self.last_names  = ["García","Martínez","Rodríguez","López","Hernández","Pérez","Gómez","Sánchez","Díaz","Morales","Vargas","Jiménez","Castillo","Romero","Ruiz","Navarro","Torres","Flores"]
        self.words = ["sistema","plataforma","proyecto","aplicación","módulo","servicio","solución","proceso","interfaz","usuario","cliente","calidad","rendimiento","automatización","optimización","diseño"]
        self.company_adjectives = ["Soluciones","Tecnologías","Servicios","Desarrollos","Sistemas","Innovaciones","Consultoría","Proyectos"]
        self.company_nouns      = ["Global","Digital","Avanzados","Inteligentes","Integrales","Profesionales","Creativos","Expertos"]
    def first_name(self): return random.choice(self.first_names)
    def last_name(self):  return random.choice(self.last_names)
    def company(self):    return f"{random.choice(self.company_adjectives)} {random.choice(self.company_nouns)}"
    def sentence(self, nb_words=8): 
        s = " ".join(random.choices(self.words, k=nb_words))
        return s.capitalize()+"."
    def date_time_between_dates(self, datetime_start: datetime, datetime_end: datetime) -> datetime:
        delta = datetime_end - datetime_start
        return datetime_start + timedelta(seconds=random.randint(0, max(1,int(delta.total_seconds()))))
    def date_between_dates(self, date_start: date, date_end: date) -> date:
        delta = date_end - date_start
        return date_start + timedelta(days=random.randint(0, max(0, delta.days)))
    def lexify(self, text="??", letters="ABCDEFGHIJKLMNOPQRSTUVWXYZ"):
        return "".join(random.choice(letters) if ch=="?" else ch for ch in text)

def get_fake(locale="es_MX"):
    if _FAKER_AVAILABLE:
        fk = Faker(locale)
        fk.seed_instance(42)
        return fk
    return SimpleFake()

fake = get_fake()

# ==== Helper Functions ====
def retraso_random(media=5, sd=4, min_=0, max_=30):
    a, b = (min_ - media)/sd, (max_ - media)/sd
    return int(truncnorm.rvs(a, b, loc=media, scale=sd))

def seleccionar_estado_realista(horas_plan: int) -> str:
    if horas_plan <= 1000:
        pesos = {"Planificado":0.05,"En ejecución":0.15,"En revisión":0.10,"Completado":0.65,"Cancelado":0.05}
    elif horas_plan <= 3000:
        pesos = {"Planificado":0.05,"En ejecución":0.40,"En revisión":0.15,"Completado":0.35,"Cancelado":0.05}
    else:
        pesos = {"Planificado":0.05,"En ejecución":0.55,"En revisión":0.20,"Completado":0.15,"Cancelado":0.05}
    return np.random.choice(list(pesos.keys()), p=list(pesos.values()))

def defects_poisson(horas_plan: int) -> int:
    lam = max(1, horas_plan/300) * random.uniform(0.8, 1.2)
    return int(np.random.poisson(lam))

# ==== Data Generation Functions ====
def generar_tablas_base():
    departamentos = ["Desarrollo","QA","Finanzas","Soporte Técnico","Gestión de Proyectos"]
    roles = ["Project Manager","Desarrollador Backend","Desarrollador Frontend","Diseñador UI/UX","QA Tester","Arquitecto de Software","Analista de Negocio","DevOps Engineer"]
    rol_to_depto = {
        "Project Manager":"Gestión de Proyectos","Desarrollador Backend":"Desarrollo","Desarrollador Frontend":"Desarrollo",
        "Diseñador UI/UX":"Desarrollo","QA Tester":"QA","Arquitecto de Software":"Desarrollo","Analista de Negocio":"Finanzas","DevOps Engineer":"Soporte Técnico"
    }
    sectores = ["Automotriz","Tecnología","Construcción","Ingeniería","Salud","Manufactura","Servicios"]
    paises   = ["México","Chile","Colombia","Argentina","España","Estados Unidos"]
    tipos_proyecto = ["Desarrollo Web","Aplicación Móvil","Software Empresarial","Infraestructura Cloud","Consultoría Técnica"]
    estados = ["Planificado","En ejecución","En revisión","Completado","Cancelado"]

    df_departamento = pd.DataFrame({"departamento_id": range(1,len(departamentos)+1), "nombre_departamento": departamentos})
    df_rol = pd.DataFrame({"rol_id": range(1,len(roles)+1), "nombre_rol": roles})

    # Empleados
    n_emp = random.randint(80,100)
    empleados = []
    for eid in range(1, n_emp+1):
        rol = random.choice(roles)
        depto = rol_to_depto[rol]
        empleados.append({
            "empleado_id": eid,
            "nombre": f"{fake.first_name()} {fake.last_name()}",
            "rol_id": int(df_rol.loc[df_rol.nombre_rol==rol,"rol_id"].iat[0]),
            "departamento_id": int(df_departamento.loc[df_departamento.nombre_departamento==depto,"departamento_id"].iat[0]),
        })
    df_empleado = pd.DataFrame(empleados)

    # Clientes
    factor = 15
    num_clientes_target = int(max(200, min(np.sqrt(NUM_PROYECTOS)*factor*random.uniform(0.9,1.1), 3000)))
    base_paises  = np.array([0.35,0.10,0.15,0.10,0.15,0.15]); base_paises = base_paises/np.sum(base_paises)
    base_sect    = np.array([0.10,0.25,0.15,0.15,0.10,0.15,0.10]); base_sect = base_sect/np.sum(base_sect)

    clientes = []; cid=1
    for pais, wp in zip(paises, base_paises):
        n_pais = int(num_clientes_target*wp)
        for sect, ws in zip(sectores, base_sect):
            n = int(n_pais*ws)
            for _ in range(n):
                clientes.append({"cliente_id": cid, "nombre": fake.company(), "sector": sect, "pais": pais})
                cid += 1
    df_cliente = pd.DataFrame(clientes)
    if len(df_cliente) < num_clientes_target:
        extra = df_cliente.sample(num_clientes_target-len(df_cliente), replace=True)
        df_cliente = pd.concat([df_cliente, extra], ignore_index=True)
    elif len(df_cliente) > num_clientes_target:
        df_cliente = df_cliente.sample(num_clientes_target).reset_index(drop=True)
    df_cliente["cliente_id"] = df_cliente.index+1

    df_tipo_proyecto = pd.DataFrame({"tipo_proyecto_id": range(1,len(tipos_proyecto)+1), "nombre": tipos_proyecto})
    df_estado = pd.DataFrame({"estado_id": range(1,len(estados)+1), "nombre_estado": estados})

    return df_departamento, df_rol, df_empleado, df_cliente, df_tipo_proyecto, df_estado

def generar_proyectos_finanzas_catalogos(df_cliente, df_tipo_proyecto, df_estado):
    RANGO_HORAS = {
        "Desarrollo Web": (600, 2000), "Aplicación Móvil": (800, 3000), "Software Empresarial": (2000, 4000),
        "Infraestructura Cloud": (1000, 3500), "Consultoría Técnica": (400, 1500)
    }
    RANGO_MONTOS = {
        "Desarrollo Web": (25_000, 90_000), "Aplicación Móvil": (40_000, 180_000), "Software Empresarial": (100_000, 250_000),
        "Infraestructura Cloud": (50_000, 150_000), "Consultoría Técnica": (20_000, 70_000)
    }
    
    proyectos, catalogos, finanzas = [], [], []
    HOY = datetime.today().date()
    PLAN_START_MIN = datetime(2020,1,1)
    PLAN_END_CAP   = datetime(2025,12,31)

    for pid in range(1, NUM_PROYECTOS+1):
        cliente_id = random.choice(df_cliente["cliente_id"].tolist())
        tipo_id    = random.choice(df_tipo_proyecto["tipo_proyecto_id"].tolist())
        tipo_nom   = df_tipo_proyecto.loc[df_tipo_proyecto.tipo_proyecto_id==tipo_id,"nombre"].iat[0]

        horas_plan = random.randint(*RANGO_HORAS[tipo_nom])
        estado_nom = seleccionar_estado_realista(horas_plan)
        estado_id  = int(df_estado.loc[df_estado.nombre_estado==estado_nom,"estado_id"].iat[0])

        nombre_proyecto = random.choice([
            "Sistema ERP Alpha","Plataforma Reservas","App Inventarios","Portal Clientes",
            "Gestión Documental","Aplicación CRM","Sistema RRHH","Plataforma E-Commerce",
            "App de Tareas","Sistema Flotas"
        ]) + f" {fake.lexify('??').upper()}"
        descripcion = fake.sentence(8)

        fecha_inicio_plan = fake.date_time_between_dates(PLAN_START_MIN, PLAN_END_CAP)
        duracion_dias     = int(np.random.triangular(90, 400, 1080))
        fecha_fin_plan    = min(fecha_inicio_plan + timedelta(days=duracion_dias), PLAN_END_CAP)

        fecha_inicio_real, fecha_fin_real = None, None
        if estado_nom in ("En ejecución","En revisión","Completado","Cancelado"):
            fecha_inicio_real = min((fecha_inicio_plan + timedelta(days=random.randint(-10,15))).date(), HOY)
        if estado_nom == "Completado":
            fecha_fin_real = min((fecha_fin_plan + timedelta(days=retraso_random())).date(), HOY)
        elif estado_nom == "Cancelado":
            fecha_fin_real = min((fecha_inicio_plan.date() + timedelta(days=random.randint(10, duracion_dias))), HOY)

        progreso = np.random.beta(2,2)
        if estado_nom == "Completado": progreso = np.random.beta(4,1.2)
        elif estado_nom == "En ejecución": progreso = np.random.beta(2.5,1.5)
        elif estado_nom == "En revisión":   progreso = np.random.beta(3,2)
        elif estado_nom == "Planificado":   progreso = np.random.beta(0.8,5)
        elif estado_nom == "Cancelado":     progreso *= 0.6

        monto_pres = random.randint(*RANGO_MONTOS[tipo_nom])
        monto_real = int(monto_pres * min(1.2, max(0.2, progreso + np.random.normal(0,0.05))))
        ingreso    = int(monto_real * (random.uniform(1.1,1.5) if estado_nom=="Completado" else random.uniform(0.8,1.3)))

        defectos_detectados = defects_poisson(horas_plan) if estado_nom in ("Completado","Cancelado") else 0
        
        proyectos.append({
            "proyecto_id": pid,
            "nombre": nombre_proyecto,
            "descripcion": descripcion,
            "fecha_inicio_plan": fecha_inicio_plan.date(),
            "fecha_fin_plan":   fecha_fin_plan.date(),
            "fecha_inicio_real": fecha_inicio_real,
            "fecha_fin_real":    fecha_fin_real,
            "horas_totales":     horas_plan,
            "horas_trabajadas":  int(horas_plan * progreso),
            "estado_id":         estado_id,
            "tipo_proyecto_id":  tipo_id,
            "cliente_id":        cliente_id,
            "defectos_detectados": defectos_detectados,
            "metadata_extraccion": 0
        })
        catalogos.append({"catalogo_id": pid, "nombre_catalogo": f"Catálogo Proyecto {pid}"})
        finanzas.append({
            "id": pid, "proyecto_id": pid,
            "monto_presupuestado": monto_pres,
            "monto_real_acumulado": monto_real,
            "ingreso_proyecto": ingreso,
            "metadata_extraccion": 0
        })

    df_proyecto = pd.DataFrame(proyectos)
    df_proyecto["catalogo_id"] = df_proyecto["proyecto_id"]
    df_catalogo_tareas = pd.DataFrame(catalogos)
    df_finanzas_proyecto = pd.DataFrame(finanzas)
    return df_proyecto, df_catalogo_tareas, df_finanzas_proyecto

def generar_tareas(df_proyecto, df_tipo_proyecto, df_estado):
    nombres_tarea = [
        "Diseño de interfaz","Desarrollo backend","Desarrollo frontend","Integración BD","Pruebas unitarias",
        "Pruebas funcionales","Revisión de código","Despliegue QA","Documentación técnica","Config. infraestructura",
        "Soporte post-implementación","Análisis de requisitos","Optimización de consultas","Seguridad","CI/CD",
        "Revisión de sprint","Implementación API","Validación QA","Mantenimiento","Control de calidad",
        "Pruebas de rendimiento","Automatización de pruebas","Migración de datos","Ajustes post-despliegue"
    ]
    tipos_tarea = ["Desarrollo","Testing","Documentación","Soporte","Diseño","Implementación","Mantenimiento"]
    prioridades = ["Alta","Media","Baja"]
    distrib_tareas = {
        "Consultoría Técnica": (12, 0.6), "Desarrollo Web": (22, 0.8), "Aplicación Móvil": (35, 1.0),
        "Software Empresarial": (60, 1.1), "Infraestructura Cloud": (45, 0.9)
    }

    tareas=[]; tid=1
    for _, p in df_proyecto.iterrows():
        tipo_nom = df_tipo_proyecto.loc[df_tipo_proyecto.tipo_proyecto_id==p.tipo_proyecto_id,"nombre"].iat[0]
        estado_nom = df_estado.loc[df_estado.estado_id==p.estado_id,"nombre_estado"].iat[0]
        media, sigma = distrib_tareas[tipo_nom]
        n_tareas = int(max(5, min(np.random.lognormal(mean=np.log(media), sigma=sigma), 200)))
        fi, ff = p["fecha_inicio_plan"], p["fecha_fin_plan"]; dur = max(1, (ff - fi).days)

        for _ in range(n_tareas):
            completada = np.random.choice([1,0], p=[0.95,0.05]) if estado_nom=="Completado" else \
                         np.random.choice([1,0], p=[0.65,0.35]) if estado_nom=="En ejecución" else \
                         np.random.choice([1,0], p=[0.40,0.60]) if estado_nom=="En revisión" else \
                         np.random.choice([1,0], p=[0.15,0.85]) if estado_nom=="Planificado" else \
                         np.random.choice([1,0], p=[0.05,0.95])
            avance_rel = np.random.beta(2,2)
            fecha_entrega = fi + timedelta(days=int(avance_rel*dur))
            fecha_completado = None
            if completada:
                retraso = max(0, int(np.random.normal(5,4)))
                fecha_completado = fecha_entrega + timedelta(days=retraso)
                if isinstance(p["fecha_fin_real"], (datetime,date)) and fecha_completado > p["fecha_fin_real"]:
                    fecha_completado = p["fecha_fin_real"]
            ref_fecha = fecha_completado if completada else fecha_entrega
            tareas.append({
                "tarea_id": tid,
                "nombre_tarea": random.choice(nombres_tarea),
                "tipo_tarea": random.choice(tipos_tarea),
                "prioridad": np.random.choice(prioridades, p=[0.25,0.5,0.25]),
                "completada": int(completada),
                "fecha_entrega": fecha_entrega,
                "fecha_completado": fecha_completado,
                "catalogo_tareas_id": p["proyecto_id"],
                "metadata_extraccion": 0
            })
            tid+=1
    return pd.DataFrame(tareas)

def generar_tipo_fase_defectos():
    tipos = [
        ("Funcionalidad", ["Lógica/algoritmo","Requisitos mal interpretados","Reglas de negocio","Validación de entradas","Cálculo numérico"]),
        ("Rendimiento",   ["Consultas ineficientes","Uso excesivo de CPU","Bloqueos/contención","N+1 queries","Caching incorrecto"]),
        ("Seguridad",     ["XSS","Inyección SQL","Autorización rota","Exposición de datos","Deserialización peligrosa","XXE"]),
        ("Usabilidad",    ["Accesibilidad","Flujo confuso","Etiquetas/ayuda","Diseño inconsistente","Feedback insuficiente"]),
        ("Compatibilidad",["Navegador/OS","Resolución/dispositivo","Dependencias/bibliotecas","Versionado API","Localización"]),
        ("Mantenibilidad",["Duplicación/código espagueti","Complejidad ciclomática","Nombres pobres","Falta de pruebas","Acoplamiento alto"]),
        ("Portabilidad",  ["Rutas/FS","Endianness/arqu.","Dependencias SO","Diferencias de runtime","Script deploy"]),
        ("Fiabilidad",    ["Condiciones de carrera","Fugas de recursos","Time-outs","Reintentos/retornos","Estados inconsistentes"]),
        ("Documentación", ["Especificación desactualizada","Guías incompletas","Comentarios engañosos","Falta de ejemplo","Formato incorrecto"]),
        ("Otros",         ["Config. errónea","Datos de prueba","Infraestructura","Terceros","Desconocido"])
    ]
    tipo_priors = {
        "Funcionalidad":0.22,"Rendimiento":0.08,"Seguridad":0.10,"Usabilidad":0.10,"Compatibilidad":0.08,
        "Mantenibilidad":0.12,"Portabilidad":0.05,"Fiabilidad":0.12,"Documentación":0.08,"Otros":0.05
    }
    fases = [
        "Análisis de Requisitos","Diseño Funcional","Diseño Técnico","Configuración del Entorno",
        "Desarrollo Backend","Desarrollo Frontend","Integración de Componentes",
        "Pruebas Unitarias","Pruebas Funcionales","Pruebas de Rendimiento",
        "Revisión de Calidad (QA)","Documentación Técnica","Implementación en Producción",
        "Ajustes Post-Producción","Soporte/Mantenimiento"
    ]
    fase_pesos = {
        "Funcionalidad": [0.10,0.10,0.10,0.02,0.18,0.18,0.08,0.12,0.10,0.01,0.01,0.00,0.00,0.00,0.00],
        "Rendimiento":   [0.02,0.03,0.06,0.06,0.10,0.08,0.10,0.05,0.10,0.28,0.06,0.00,0.03,0.02,0.01],
        "Seguridad":     [0.06,0.08,0.14,0.05,0.08,0.08,0.06,0.05,0.10,0.02,0.08,0.02,0.10,0.05,0.03],
        "Usabilidad":    [0.08,0.14,0.06,0.01,0.04,0.24,0.04,0.06,0.14,0.00,0.10,0.04,0.03,0.01,0.01],
        "Compatibilidad":[0.02,0.04,0.06,0.12,0.10,0.12,0.10,0.06,0.12,0.05,0.06,0.02,0.06,0.04,0.03],
        "Mantenibilidad":[0.02,0.06,0.14,0.04,0.20,0.12,0.06,0.08,0.08,0.02,0.10,0.06,0.01,0.00,0.01],
        "Portabilidad":  [0.01,0.02,0.06,0.16,0.08,0.06,0.08,0.04,0.08,0.04,0.06,0.02,0.10,0.10,0.09],
        "Fiabilidad":    [0.02,0.04,0.08,0.06,0.16,0.12,0.10,0.10,0.08,0.04,0.08,0.02,0.04,0.04,0.02],
        "Documentación": [0.08,0.08,0.06,0.02,0.04,0.04,0.02,0.04,0.04,0.00,0.08,0.36,0.06,0.04,0.04],
        "Otros":         [0.03,0.04,0.04,0.10,0.10,0.08,0.10,0.06,0.06,0.04,0.06,0.02,0.10,0.05,0.02]
    }
    severidad_pr = {
        "Funcionalidad":[0.55,0.35,0.10], "Rendimiento":  [0.45,0.40,0.15], "Seguridad":    [0.35,0.40,0.25],
        "Usabilidad":   [0.70,0.25,0.05], "Compatibilidad":[0.55,0.35,0.10], "Mantenibilidad":[0.60,0.30,0.10],
        "Portabilidad": [0.55,0.35,0.10], "Fiabilidad":   [0.45,0.35,0.20], "Documentación":[0.70,0.25,0.05],
        "Otros":        [0.55,0.35,0.10]
    }

    filas_tipos=[]; tid=1
    for categoria, subtipos in tipos:
        for st in subtipos:
            filas_tipos.append({"tipo_defecto_id": tid, "categoria": categoria, "subtipo": st})
            tid+=1
    df_tipo_defecto = pd.DataFrame(filas_tipos)
    df_fase = pd.DataFrame({"fase_id": range(1,16), "nombre_fase": fases})

    return df_tipo_defecto, df_fase, tipo_priors, fase_pesos, severidad_pr

def _normaliza(pesos: List[float]) -> np.ndarray:
    arr = np.array(pesos, dtype=float); s = arr.sum()
    return arr/ s if s>0 else np.ones_like(arr)/len(arr)

def generar_defectos(df_proyecto, df_tipo_defecto, df_fase, tipo_priors, fase_pesos, severidad_pr):
    severidades = ["Baja","Media","Alta"]
    defectos=[]; did=1
    categorias = sorted(set(df_tipo_defecto["categoria"]))
    cat_prior = np.array([tipo_priors[c] for c in categorias], dtype=float); cat_prior /= cat_prior.sum()
    cat_to_sub = {c: df_tipo_defecto[df_tipo_defecto["categoria"]==c] for c in categorias}

    for _, p in df_proyecto.iterrows():
        total = int(p.get("defectos_detectados", 0))
        if total <= 0: continue

        mix = np.random.multinomial(total, cat_prior)
        inicio = p["fecha_inicio_real"] or p["fecha_inicio_plan"]
        fin    = p["fecha_fin_real"]    or p["fecha_fin_plan"]
        if isinstance(inicio, datetime): inicio = inicio.date()
        if isinstance(fin, datetime):    fin = fin.date()

        for c_idx, cat in enumerate(categorias):
            n_cat = mix[c_idx]
            if n_cat == 0: continue
            f_pesos = _normaliza(fase_pesos[cat])
            sever_p = severidad_pr[cat]
            sub_df = cat_to_sub[cat]
            sub_ids = sub_df["tipo_defecto_id"].tolist()

            for _ in range(n_cat):
                tipo_defecto_id = random.choice(sub_ids)
                fase_id = int(np.random.choice(df_fase["fase_id"], p=f_pesos))
                severidad = str(np.random.choice(severidades, p=sever_p))
                base_alvo = random.choice(["usuario","datos","autenticación","API","UI","reportes","catálogo","pago"])
                cat_sub = sub_df.loc[sub_df.tipo_defecto_id==tipo_defecto_id, "subtipo"].iat[0]
                descripcion = f"{cat}: {cat_sub} en módulo de {base_alvo}."
                fecha_registro = fake.date_between_dates(inicio, fin) if inicio!=fin else inicio
                
                defectos.append({
                    "defecto_id": did,
                    "proyecto_id": int(p["proyecto_id"]),
                    "tipo_defecto_id": int(tipo_defecto_id),
                    "fase_id": int(fase_id),
                    "severidad": severidad,
                    "descripcion": descripcion,
                    "fecha_registro": fecha_registro,
                    "metadata_extraccion": 0
                })
                did+=1
    return pd.DataFrame(defectos)

def generar_asignaciones(df_proyecto, df_empleado):
    from numpy.random import poisson
    asignaciones=[]
    for _, p in df_proyecto.iterrows():
        base_media = p["horas_totales"]/400
        media = max(3, base_media * random.uniform(0.9,1.3))
        n = int(max(3, min(poisson(media), 30)))
        seleccionados = random.sample(df_empleado["empleado_id"].tolist(), k=min(n, len(df_empleado)))
        for e in seleccionados:
            asignaciones.append({
                "proyecto_id": int(p["proyecto_id"]), 
                "empleado_id": int(e),
                "metadata_extraccion": 0
            })
    return pd.DataFrame(asignaciones)

def exportar_csvs(dfs: Dict[str, pd.DataFrame], out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    for fname, df in dfs.items():
        path = os.path.join(out_dir, fname)
        df.to_csv(path, index=False, encoding="utf-8")
        print(f"✅ {fname} → {len(df):,} registros")

# ==== Main Pipeline ====
if __name__ == "__main__":
    print("🔧 Generando Tablas base...")
    df_departamento, df_rol, df_empleado, df_cliente, df_tipo_proyecto, df_estado = generar_tablas_base()

    print("🔧 Generando Proyectos, catálogos y finanzas...")
    df_proyecto, df_catalogo_tareas, df_finanzas_proyecto = generar_proyectos_finanzas_catalogos(
        df_cliente, df_tipo_proyecto, df_estado
    )

    print("🔧 Generando Tareas...")
    df_tarea = generar_tareas(df_proyecto, df_tipo_proyecto, df_estado)

    print("🔧 Generando Defectos...")
    df_tipo_defecto, df_fase_sdlc, tipo_priors, fase_pesos, severidad_pr = generar_tipo_fase_defectos()
    df_defecto = generar_defectos(df_proyecto, df_tipo_defecto, df_fase_sdlc, tipo_priors, fase_pesos, severidad_pr)

    print("🔧 Generando Asignaciones...")
    df_proyecto_empleado = generar_asignaciones(df_proyecto, df_empleado)

    print("💾 Exportando CSVs...")
    exportar_csvs({
        "departamento.csv": df_departamento,
        "rol.csv": df_rol,
        "empleado.csv": df_empleado,
        "cliente.csv": df_cliente,
        "tipo_proyecto.csv": df_tipo_proyecto,
        "estado.csv": df_estado,
        "proyecto.csv": df_proyecto,
        "catalogo_tareas.csv": df_catalogo_tareas,
        "tarea.csv": df_tarea,
        "proyecto_empleado.csv": df_proyecto_empleado,
        "finanzas_proyecto.csv": df_finanzas_proyecto,
        "tipo_defecto.csv": df_tipo_defecto,
        "fase_sdlc.csv": df_fase_sdlc,
        "defecto.csv": df_defecto
    }, OUTPUT_DIR)
    print("🏁 Listo.")
