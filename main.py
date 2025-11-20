import streamlit as st
from typing import Any, Dict, List, Optional, Tuple
import sqlite3
import re

# Interfaz CRUD muy simple, todo en español y con menos código.
# Usa tu módulo `funciones_crud.py` existente para las operaciones.

st.set_page_config(page_title="Interfaz transportes", layout="wide")

# -- Definición mínima de esquemas: solo los nombres de campos que usa la UI
SCHEMAS = {
    "Boleto": ["codigo", "servicio_id", "cliente_id", "asiento", "precio"],
    "Bus": ["patente", "modelo", "capacidad"],
    "Chofer": ["rut", "nombre", "telefono", "email"],
    "Cliente": ["rut", "nombre", "email", "telefono", "direccion"],
    "Pago": ["boleto_id", "monto", "fecha_pago", "metodo"],
    "Parada": ["nombre", "ciudad"],
    "Ruta": ["codigo", "nombre", "origen", "destino"],
    "RutaParadas": ["ruta_id", "parada_id", "orden"],
    "Servicio": ["codigo", "ruta_id", "bus_id", "chofer_id", "fecha_salida", "fecha_llegada"],
    "Tarifa": ["ruta_id", "nombre", "monto", "fecha_inicio", "fecha_fin"],
}
#
# Metadatos simples extraídos del esquema SQL (NOT NULL / UNIQUE / tipos especiales)
# Esto permite validar en la UI antes de enviar al DB.
SCHEMA_META = {
    "Ruta": {"required": ["codigo", "nombre", "origen", "destino"], "unique": ["codigo"]},
    "Parada": {"required": ["nombre", "ciudad"], "unique": []},
    "RutaParadas": {"required": ["ruta_id", "parada_id", "orden"], "unique": []},
    "Bus": {"required": ["patente", "capacidad"], "unique": ["patente"]},
    "Chofer": {"required": ["rut", "nombre"], "unique": ["rut"], "types": {"rut": "rut"}},
    "Cliente": {"required": ["rut", "nombre"], "unique": ["rut"], "types": {"rut": "rut"}},
    "Servicio": {"required": ["codigo", "ruta_id", "bus_id", "chofer_id", "fecha_salida"], "unique": ["codigo"], "types": {"fecha_salida": "datetime", "fecha_llegada": "datetime"}},
    "Tarifa": {"required": ["ruta_id", "monto"], "unique": [], "types": {"fecha_inicio": "datetime", "fecha_fin": "datetime"}},
    "Boleto": {"required": ["codigo", "servicio_id", "cliente_id", "asiento", "precio"], "unique": ["codigo"]},
    "Pago": {"required": ["boleto_id", "monto", "metodo"], "unique": ["boleto_id"], "types": {"fecha_pago": "datetime"}},
}

# --------- Conectar con tu módulo de base de datos --------------------
try:
    import funciones_crud
    HAS_DB = all(hasattr(funciones_crud, n) for n in ("insertar", "consultar", "actualizar", "eliminar"))
except Exception:
    funciones_crud = None  # type: ignore
    HAS_DB = False


def requiere_db():
    """Mostrar aviso si falta el módulo de base de datos."""
    if not HAS_DB:
        st.error("Falta el módulo `funciones_crud.py` con las funciones requeridas.")
        return False
    return True


def caster(campo: str, valor: str) -> Any:
    """Convertir a entero si el nombre del campo sugiere número."""
    if valor is None or valor == "":
        return None
    if any(k in campo.lower() for k in ("id", "monto", "asiento", "precio", "capacidad")):
        try:
            return int(valor)
        except Exception:
            return valor
    return valor


def is_integer_field(campo: str) -> bool:
    """Heurística simple para determinar si un campo debe ser integer.
    Basada en nombres comunes (id, monto, asiento, precio, capacidad, orden).
    Excluye campos de fecha/hora.
    """
    # Campos que NO deben ser tratados como enteros
    if any(k in campo.lower() for k in ("fecha", "date", "datetime", "hora", "time")):
        return False
    
    # Campos que SÍ deben ser enteros
    integer_fields = ("id", "monto", "asiento", "precio", "capacidad", "orden", "codigo")
    return any(k in campo.lower() for k in integer_fields)


def leer_campos(prefijo: str, campos: List[str], tabla: str) -> Dict[str, Any]:
    """Leer valores desde st.session_state (inputs) y castear.
    Maneja campos de fecha y hora combinándolos en el formato correcto.
    """
    out: Dict[str, Any] = {}
    for c in campos:
        key = f"{prefijo}_{tabla}_{c}"
        val = st.session_state.get(key, "") if hasattr(st, "session_state") else ""
        
        # Si es un campo de fecha, buscar también el campo de hora correspondiente
        if c in ["fecha_salida", "fecha_llegada"]:
            # Determinar el campo de hora correspondiente
            hora_field = "hora_salida" if c == "fecha_salida" else "hora_llegada"
            hora_key = f"{prefijo}_{tabla}_{hora_field}"
            hora_val = st.session_state.get(hora_key, "00:00") if hasattr(st, "session_state") else "00:00"
            
            # Combinar fecha y hora si la fecha está presente
            if val:
                val = f"{val} {hora_val}"
        
        v = caster(c, val)
        if v is not None and v != "":
            out[c] = v
    return out


def _pretty_result(res: Any) -> str:
    """Formatea una respuesta de las funciones CRUD en una línea legible para mostrar en la UI.
    Evita imprimir la representación JSON/dict cruda.
    """
    if isinstance(res, dict):
        # Casos comunes
        if res.get("deleted"):
            return f"Eliminado: id={res.get('id')}"
        if res.get("error"):
            return f"Error ({res.get('error')}): {res.get('message') or ''}"
        if "id" in res:
            return f"OK — id={res.get('id')}"
        # Fallback: pares clave=valor concisos
        try:
            return ", ".join(f"{k}={v}" for k, v in res.items())
        except Exception:
            return str(res)
    # Listas/tuplas: indicar cantidad
    if isinstance(res, (list, tuple)):
        return f"Resultado: {len(res)} filas"
    return str(res)


# Wrappers muy simples que llaman a funciones_crud con los parámetros que espera
def insertar_registro(tabla: str, datos: Dict[str, Any]):
    if not funciones_crud:
        return {"error": "no_db", "message": "Módulo funciones_crud no disponible."}
    # Validar según metadatos
    valid, msg = validar_datos(tabla, datos, is_update=False)
    if not valid:
        return {"error": "validation", "message": msg}
    cols = list(datos.keys())
    vals = [datos[c] for c in cols]
    try:
        return funciones_crud.insertar(tabla, cols, vals)
    except sqlite3.IntegrityError as e:
        # Capturar violaciones de UNIQUE u otras restricciones de integridad
        return {"error": "unique", "message": str(e)}
    except Exception as e:
        return {"error": "db_error", "message": str(e)}


def leer_registros(tabla: str, filtros: Optional[Dict[str, Any]], limite: int) -> List[Dict[str, Any]]:
    cols = ["id"] + SCHEMAS[tabla]
    condicion = None
    valores: tuple = ()
    if filtros:
        partes = [f"{k} = ?" for k in filtros.keys()]
        condicion = " AND ".join(partes)
        valores = tuple(filtros.values())
    if not funciones_crud:
        return []
    try:
        if condicion:
            filas = funciones_crud.consultar(tabla, columnas=cols, condicion=condicion, valores_condicion=valores)
        else:
            filas = funciones_crud.consultar(tabla, columnas=cols, condicion=None, valores_condicion=())
    except Exception:
        return []
    resultado: List[Dict[str, Any]] = []
    for row in (filas or [])[:limite]:
        d = {cols[i]: row[i] for i in range(min(len(cols), len(row)))}
        resultado.append(d)
    return resultado


def actualizar_registro(tabla: str, id_registro, datos: Dict[str, Any]):
    condicion = "id = ?"
    if not funciones_crud:
        return {"error": "no_db", "message": "Módulo funciones_crud no disponible."}
    # Validar según metadatos (indicar que es update para permitir same-row unique)
    valid, msg = validar_datos(tabla, datos, is_update=True, current_id=id_registro)
    if not valid:
        return {"error": "validation", "message": msg}
    try:
        return funciones_crud.actualizar(tabla, datos, condicion, (id_registro,))
    except Exception as e:
        return {"error": "db_error", "message": str(e)}


def validar_datos(tabla: str, datos: Dict[str, Any], is_update: bool = False, current_id: Optional[int] = None) -> Tuple[bool, Optional[str]]:
    """Valida datos contra SCHEMA_META: campos requeridos, formato de RUT, fechas, y unicidad simple.
    Retorna (True, None) si pasa, o (False, mensaje) si falla.
    """
    meta = SCHEMA_META.get(tabla, {})
    # Required
    for req in meta.get("required", []):
        # Si es update y campo no está presente, no lo exigimos
        if is_update and req not in datos:
            continue
        val = datos.get(req)
        if val is None or (isinstance(val, str) and val.strip() == ""):
            return False, f"El campo '{req}' es obligatorio para la tabla {tabla}."

    # Tipos especiales
    types = meta.get("types", {})
    for field, kind in types.items():
        if field not in datos:
            continue
        val = datos.get(field)
        if val is None:
            continue
        if kind == "rut":
            # formato 12.345.678-9 o 1.234.567-8; permitir K/k
            if not re.match(r"^\d{1,2}\.\d{3}\.\d{3}-[\dkK]$", str(val)):
                return False, f"El campo '{field}' debe tener formato RUT: xx.xxx.xxx-x"
        if kind == "datetime":
            s = str(val).strip()
            # Aceptar YYYY/MM/DD o YYYY/MM/DD HH:MM (ahora con validación de hora)
            if not (re.match(r"^\d{4}/\d{2}/\d{2}$", s) or re.match(r"^\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}$", s)):
                return False, f"El campo '{field}' debe tener formato fecha 'YYYY/MM/DD' o 'YYYY/MM/DD HH:MM'"
            # Validar formato de hora si está presente
            if " " in s:
                fecha_part, hora_part = s.split(" ", 1)
                if not re.match(r"^\d{2}:\d{2}$", hora_part):
                    return False, f"El campo '{field}' tiene formato de hora inválido. Use 'HH:MM'"

    # Unicidad: comprobación simple consultando la DB
    uniques = meta.get("unique", [])
    if uniques and funciones_crud:
        for col in uniques:
            if col not in datos:
                continue
            val = datos.get(col)
            if val is None or (isinstance(val, str) and val == ""):
                continue
            try:
                rows = funciones_crud.consultar(tabla, columnas=["id", col], condicion=f"{col} = ?", valores_condicion=(val,)) or []
            except Exception:
                rows = []
            if not rows:
                continue
            # Si es update y la única fila encontrada es la misma id, ok
            if is_update and current_id is not None:
                other = [r for r in rows if r[0] != current_id]
                if other:
                    return False, f"El valor '{val}' para '{col}' ya existe en {tabla}."
            else:
                # insert: cualquier fila existente es conflicto
                if rows:
                    return False, f"El valor '{val}' para '{col}' ya existe en {tabla}."

    return True, None


def eliminar_registro(tabla: str, id_registro):
    """
    Intentamos borrar directamente usando la conexión SQLite para poder
    capturar errores de integridad (foreign key) y devolver una estructura
    informativa que la UI puede interpretar.
    """
    conn = None
    try:
        # Preferir usar la función conectar si está disponible en funciones_crud
        if funciones_crud and hasattr(funciones_crud, "conectar"):
            conn = funciones_crud.conectar()
        else:
            conn = sqlite3.connect("base_de_datos_transportes.db")
            conn.execute("PRAGMA foreign_keys = ON")

        cur = conn.cursor()
        cur.execute(f"DELETE FROM \"{tabla}\" WHERE id = ?", (id_registro,))
        # Si no se eliminó ninguna fila, el registro no existe
        if cur.rowcount == 0:
            conn.commit()
            return {"deleted": False, "error": "not_found", "message": f"Registro id={id_registro} no encontrado en {tabla}."}
        conn.commit()
        return {"deleted": True, "id": id_registro}
    except sqlite3.IntegrityError as e:
        # Falló por restricción de clave foránea
        # Buscar qué tablas contienen referencias a este registro
        # Si no hay conexión válida, intentar abrir una temporal para buscar dependientes
        dependientes = None
        try:
            if not conn:
                conn = sqlite3.connect("base_de_datos_transportes.db")
                conn.execute("PRAGMA foreign_keys = ON")
            dependientes = _buscar_referencias(conn, tabla, id_registro)
        except Exception:
            dependientes = None
        return {"deleted": False, "error": "foreign_key", "message": str(e), "dependents": dependientes}
    except sqlite3.Error as e:
        return {"deleted": False, "error": "db_error", "message": str(e)}
    finally:
        if conn:
            conn.close()


def _buscar_referencias(conn: sqlite3.Connection, tabla: str, id_val) -> Dict[str, List[Dict[str, Any]]]:
    """Busca en la base de datos las filas que referencian a (tabla,id_val).
    Retorna un dict {tabla_referente: [ {pk: val, col: val, ...}, ... ] }
    Limitamos a 10 filas por tabla para no sobrecargar la UI.
    """
    res: Dict[str, List[Dict[str, Any]]] = {}
    cur = conn.cursor()
    # Obtener todas las tablas de usuario
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tablas = [r[0] for r in cur.fetchall()]
    for t in tablas:
        try:
            # PRAGMA foreign_key_list devuelve las FK definidas en la tabla 't'
            fk_rows = cur.execute(f'PRAGMA foreign_key_list("{t}")').fetchall()
            # fk_rows columns: (id, seq, table, from, to, on_update, on_delete, match)
            for fk in fk_rows:
                ref_table = fk[2]
                from_col = fk[3]
                to_col = fk[4]
                if ref_table == tabla:
                    # determinar pk de la tabla 't'
                    info = cur.execute(f'PRAGMA table_info("{t}")').fetchall()
                    pk_cols = [row[1] for row in info if row[5] > 0]
                    pk = pk_cols[0] if pk_cols else None
                    # construir consulta segura: usar nombres ya validados por sqlite_master/pragma
                    q = f'SELECT * FROM "{t}" WHERE "{from_col}" = ? LIMIT 10'
                    rows = cur.execute(q, (id_val,)).fetchall()
                    if rows:
                        cols = [c[0] for c in cur.description]
                        lista = []
                        for row in rows:
                            d = {cols[i]: row[i] for i in range(len(cols))}
                            lista.append(d)
                        res[t] = lista
        except Exception:
            # ignorar errores en tablas individuales y continuar
            continue
    return res


# ----------------------- Interfaz (muy simple) -------------------------
st.title("Interfaz transportes")
st.write("Interfaz mínima. Selecciona operación y tabla en la barra lateral.")

with st.sidebar:
    operacion = st.selectbox("Operación", ["Crear", "Leer", "Actualizar", "Eliminar"])
    tabla = st.selectbox("Tabla", options=list(SCHEMAS.keys()))

col1, col2 = st.columns(2)

with col1:
    st.header(operacion)

    if operacion == "Crear":
        with st.form("form_crear"):
            for f in SCHEMAS[tabla]:
                # CORREGIDO: Agregar tabla a la key
                key = f"crear_{tabla}_{f}"
                if is_integer_field(f):
                    st.number_input(f, min_value=0, step=1, key=key)
                else:
                    if f == "fecha_salida":
                        st.write("**Fecha y Hora de Salida**")
                        col_fecha, col_hora = st.columns(2)
                        with col_fecha:
                            st.text_input("Fecha (YYYY/MM/DD)", key=key, placeholder="YYYY/MM/DD")
                        with col_hora:
                            st.text_input("Hora (HH:MM)", key=f"crear_{tabla}_hora_salida", placeholder="HH:MM", value="00:00")
                    elif f == "fecha_llegada":
                        st.write("**Fecha y Hora de Llegada**")
                        col_fecha, col_hora = st.columns(2)
                        with col_fecha:
                            st.text_input("Fecha (YYYY/MM/DD)", key=key, placeholder="YYYY/MM/DD")
                        with col_hora:
                            st.text_input("Hora (HH:MM)", key=f"crear_{tabla}_hora_llegada", placeholder="HH:MM", value="00:00")
                    else:
                        # Para otros campos de fecha genéricos
                        if any(k in f.lower() for k in ("fecha", "date", "datetime")) and f not in ["fecha_salida", "fecha_llegada"]:
                            st.write(f"**{f}**")
                            col_fecha, col_hora = st.columns(2)
                            with col_fecha:
                                st.text_input("Fecha (YYYY/MM/DD)", key=key, placeholder="YYYY/MM/DD")
                            with col_hora:
                                hora_field = f.replace("fecha", "hora")
                                st.text_input("Hora (HH:MM)", key=f"crear_{tabla}_{hora_field}", placeholder="HH:MM", value="00:00")
                        else:
                            st.text_input(f, key=key)
            enviar = st.form_submit_button("Crear")
        if enviar:
            datos = leer_campos("crear", SCHEMAS[tabla], tabla)
            if not datos:
                st.info("No se ingresaron datos.")
            elif requiere_db():
                res = insertar_registro(tabla, datos)
                # manejar errores retornados por el wrapper
                if isinstance(res, dict) and res.get("error"):
                    # Mensajes específicos según tipo de error
                    err = res.get("error")
                    msg = res.get("message")
                    if err == "validation":
                        st.error(f"Validación: {msg}")
                    elif err == "unique":
                        st.error("Error: valor duplicado para un campo único. " + str(msg))
                    elif err == "no_db":
                        st.error("Error: módulo de base de datos no disponible.")
                        st.write(res)
                    else:
                        st.error(f"Error al crear (BD): {msg}")
                        st.write(res)
                else:
                    st.success("Creado")
                    st.info(_pretty_result(res))

    elif operacion == "Leer":
        with st.form("form_leer"):
            filtros: Dict[str, Any] = {}
            for f in SCHEMAS[tabla]:
                # CORREGIDO: Agregar tabla a la key
                key = f"leer_{tabla}_{f}"
                if is_integer_field(f):
                    # Usamos 0 como sentinel "sin filtro" (IDs/autoincrement empiezan en 1)
                    filtros[f] = st.number_input(f, min_value=0, value=0, step=1, key=key)
                else:
                    filtros[f] = st.text_input(f, key=key)
            limite = st.number_input("Límite", min_value=1, value=20, key=f"leer_{tabla}_limite")
            enviar = st.form_submit_button("Buscar")
        if enviar:
            filt = {k: caster(k, v) for k, v in filtros.items() if v}
            if requiere_db():
                rows = leer_registros(tabla, filt or None, int(limite))
                st.write(f"Resultados: {len(rows)}")
                st.table(rows)

    elif operacion == "Actualizar":
        with st.form("form_actualizar"):
            # CORREGIDO: Agregar tabla a la key del ID
            id_reg = st.number_input("ID del registro", min_value=0, value=0, step=1, key=f"upd_{tabla}_id")
            for f in SCHEMAS[tabla]:
                # CORREGIDO: Agregar tabla a la key
                key = f"upd_{tabla}_{f}"
                if is_integer_field(f):
                    st.number_input(f, min_value=0, step=1, key=key)
                else:
                    if f == "fecha_salida":
                        st.write("**Fecha y Hora de Salida**")
                        col_fecha, col_hora = st.columns(2)
                        with col_fecha:
                            st.text_input("Fecha (YYYY/MM/DD)", key=key, placeholder="YYYY/MM/DD")
                        with col_hora:
                            st.text_input("Hora (HH:MM)", key=f"upd_{tabla}_hora_salida", placeholder="HH:MM", value="00:00")
                    elif f == "fecha_llegada":
                        st.write("**Fecha y Hora de Llegada**")
                        col_fecha, col_hora = st.columns(2)
                        with col_fecha:
                            st.text_input("Fecha (YYYY/MM/DD)", key=key, placeholder="YYYY/MM/DD")
                        with col_hora:
                            st.text_input("Hora (HH:MM)", key=f"upd_{tabla}_hora_llegada", placeholder="HH:MM", value="00:00")
                    else:
                        # Para otros campos de fecha genéricos
                        if any(k in f.lower() for k in ("fecha", "date", "datetime")) and f not in ["fecha_salida", "fecha_llegada"]:
                            st.write(f"**{f}**")
                            col_fecha, col_hora = st.columns(2)
                            with col_fecha:
                                st.text_input("Fecha (YYYY/MM/DD)", key=key, placeholder="YYYY/MM/DD")
                            with col_hora:
                                hora_field = f.replace("fecha", "hora")
                                st.text_input("Hora (HH:MM)", key=f"upd_{tabla}_{hora_field}", placeholder="HH:MM", value="00:00")
                        else:
                            st.text_input(f, key=key)
            enviar = st.form_submit_button("Actualizar")
        if enviar:
            if not id_reg:
                st.error("Provee el ID del registro.")
            else:
                # validar conversión de ID
                try:
                    id_int = int(id_reg)
                except Exception:
                    st.error("El ID debe ser un número entero.")
                    id_int = None

                if id_int is None:
                    pass
                else:
                    datos = leer_campos("upd", SCHEMAS[tabla], tabla)
                    if not datos:
                        st.info("No hay campos para actualizar.")
                    elif requiere_db():
                        res = actualizar_registro(tabla, id_int, datos)
                        if isinstance(res, dict) and res.get("error"):
                            st.error(f"Error al actualizar: {res.get('message')}")
                            # mostrar mensaje legible en vez de JSON
                            st.info(_pretty_result(res))
                        else:
                            st.success("Actualizado")
                            st.info(_pretty_result(res))

    elif operacion == "Eliminar":
        with st.form("form_eliminar"):
            # CORREGIDO: Agregar tabla a la key
            id_reg = st.number_input("ID del registro", min_value=0, value=0, step=1, key=f"del_{tabla}_id")
            confirmar = st.checkbox("Confirmar eliminación", key=f"del_{tabla}_confirm")
            enviar = st.form_submit_button("Eliminar")
        if enviar:
            if not confirmar:
                st.error("Marca confirmar para eliminar.")
            elif not id_reg:
                st.error("Provee el ID del registro.")
            elif requiere_db():
                try:
                    id_int = int(id_reg)
                except Exception:
                    st.error("El ID debe ser un número entero.")
                    id_int = None

                if id_int is None:
                    res = {"deleted": False, "error": "invalid_id", "message": "ID inválido"}
                else:
                    res = eliminar_registro(tabla, id_int)
                # res es un dict con {deleted: True} o {deleted: False, error: ...}
                if isinstance(res, dict) and not res.get("deleted", False):
                    err = res.get("error")
                    if err == "foreign_key":
                        st.error("No se puede eliminar: existen registros que dependen de este (restricción de clave foránea). Elimina antes los registros dependientes o actualiza las referencias.")
                        st.write(res.get("message"))
                        dependents = res.get("dependents")
                        if dependents:
                            st.subheader("Registros dependientes encontrados")
                            for tname, rows in dependents.items():
                                st.markdown(f"**Tabla:** {tname}")
                                st.table(rows)
                    elif err == "not_found":
                        st.warning("No existe el registro que intentas eliminar.")
                        st.write(res.get("message"))
                    else:
                        st.error(f"Error al eliminar: {res.get('message')}")
                else:
                    st.success("Eliminado")
                    st.info(_pretty_result(res))

with col2:
    st.header("Datos desde la base de datos")
    # Selector independiente para ver tablas en el panel derecho
    try:
        default_idx = list(SCHEMAS.keys()).index(tabla)
    except Exception:
        default_idx = 0
    view_table = st.selectbox("Tabla a ver", options=list(SCHEMAS.keys()), index=default_idx, key="view_table")
    st.subheader(f"Tabla: {view_table}")

    if not HAS_DB:
        st.info("Módulo `funciones_crud.py` no disponible: no se pueden mostrar datos en vivo.")
    else:
        # Límite visible configurable
        limite = st.number_input("Filas a mostrar", min_value=1, max_value=100, value=10, key="view_limit")
        try:
            cols = ["id"] + SCHEMAS.get(view_table, [])
            filas_db = funciones_crud.consultar(view_table, columnas=cols, condicion=None, valores_condicion=()) or []
            muestra = [{cols[i]: row[i] for i in range(min(len(cols), len(row)))} for row in filas_db[:int(limite)]]
            if muestra:
                st.table(muestra)
            else:
                st.info("La tabla está vacía o no hay filas que mostrar.")
        except Exception as e:
            st.error(f"Error al leer la base de datos: {e}")