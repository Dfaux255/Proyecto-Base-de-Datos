import sqlite3 
# =========================================
# FUNCIÓN: CONECTAR A LA BASE DE DATOS
# =========================================
def conectar():
    """
    Abre la conexión con la base de datos 'HHH.db'.
    La línea PRAGMA foreign_keys = ON activa el uso de claves foráneas,
    lo que asegura que las relaciones entre tablas sean respetadas.
    """
    conexion = sqlite3.connect("base_de_datos_transportes.db")  # Abre el archivo de base de datos
    conexion.execute("PRAGMA foreign_keys = ON")  # activa la comprobación de claves foráneas en SQLite, Esto evita insertar o eliminar filas que rompan relaciones.
    return conexion  # Devuelve el objeto conexión

# =========================================
# FUNCIÓN: INSERTAR REGISTROS
# =========================================
def insertar(nombre_tabla, lista_columnas, lista_valores):
    """
    Inserta un registro nuevo en la tabla indicada.
    Parámetros:
        nombre_tabla: nombre de la tabla (texto)
        lista_columnas: lista con los nombres de las columnas
        lista_valores: lista con los valores que se insertarán
    """
    conexion = conectar() #para obtener una conexión limpia.
    cursor = conexion.cursor()  # Crea un cursor para ejecutar comandos SQL
    # Se generan los signos "?" para los valores (uno por cada dato)
    signos_interrogacion = ", ".join(["?"] * len(lista_valores))
    # Une los nombres de las columnas separadas por comas
    columnas_texto = ", ".join(lista_columnas)
    # Crea la instrucción SQL completa
    consulta_sql = "INSERT INTO " + nombre_tabla + " (" + columnas_texto + ") VALUES (" + signos_interrogacion + ")"
    try:
        cursor.execute(consulta_sql, lista_valores)  # Envía la instrucción SQL con los valores
        conexion.commit()  # Guarda los cambios permanentemente
        print("Registro insertado correctamente en la tabla", nombre_tabla)
    except sqlite3.Error as error:
        print("Error al insertar datos:", error)
    finally:
        conexion.close()  # Cierra la conexión con la base

# =========================================
# FUNCIÓN: CONSULTAR REGISTROS
# =========================================
def consultar(nombre_tabla, columnas="*", condicion=None, valores_condicion=()):
    """
    Consulta registros desde una tabla.
    Parámetros:
        nombre_tabla: nombre de la tabla
        columnas: lista con los nombres de las columnas o "*" para todas
        condicion: texto opcional (por ejemplo "id = ?")
        valores_condicion: valores usados en la condición (tupla)
    Retorna una lista con los resultados encontrados.
    """
    conexion = conectar()
    cursor = conexion.cursor()
    # Si el parámetro columnas viene en lista, se convierte a texto
    if isinstance(columnas, list):
        columnas = ", ".join(columnas)
    # Comienza a formar la consulta SQL
    consulta_sql = "SELECT " + columnas + " FROM " + nombre_tabla
    # Si hay condición, se agrega la parte del WHERE
    if condicion:
        consulta_sql += " WHERE " + condicion
    try:
        cursor.execute(consulta_sql, valores_condicion)
        filas = cursor.fetchall()  # fetchall() obtiene todas las filas de la consulta
        return filas
    except sqlite3.Error as error:
        print("Error al consultar datos:", error)
        return []
    finally:
        conexion.close()

# =========================================
# FUNCIÓN: ACTUALIZAR REGISTROS
# =========================================
def actualizar(nombre_tabla, nuevos_datos, condicion, valores_condicion=()):
    """
    Actualiza uno o más campos de un registro.
    Parámetros:
        nombre_tabla: nombre de la tabla
        nuevos_datos: diccionario con los campos a cambiar (ej: {"email": "nuevo@correo.com"})
        condicion: condición para elegir el registro (ej: "id = ?")
        valores_condicion: valores para reemplazar el "?" de la condición
    """
    conexion = conectar()
    cursor = conexion.cursor()
    # Construye la parte SET de forma simple: "columna1 = ?, columna2 = ?"
    texto_actualizacion = ""
    for campo in nuevos_datos.keys():
        texto_actualizacion += campo + " = ?, "
    texto_actualizacion = texto_actualizacion[:-2]  # Quita la última coma y espacio
    # Crea la instrucción SQL completa
    consulta_sql = "UPDATE " + nombre_tabla + " SET " + texto_actualizacion + " WHERE " + condicion
    # Combina los valores nuevos con los de la condición
    valores_finales = tuple(nuevos_datos.values()) + tuple(valores_condicion)
    try:
        cursor.execute(consulta_sql, valores_finales)
        conexion.commit()
        print("Registro actualizado correctamente en la tabla", nombre_tabla)
    except sqlite3.Error as error:
        print("Error al actualizar datos:", error)
    finally:
        conexion.close()

# =========================================
# FUNCIÓN: ELIMINAR REGISTROS
# =========================================
def eliminar(nombre_tabla, condicion, valores_condicion=()):
    """
    Elimina registros de una tabla.
    Parámetros:
        nombre_tabla: nombre de la tabla
        condicion: texto de la condición (por ejemplo "id = ?")
        valores_condicion: valores usados para reemplazar el "?"
    """
    conexion = conectar()
    cursor = conexion.cursor()
    consulta_sql = "DELETE FROM " + nombre_tabla + " WHERE " + condicion
    try:
        cursor.execute(consulta_sql, valores_condicion)
        conexion.commit()
        print("Registro eliminado correctamente de la tabla", nombre_tabla)
    except sqlite3.Error as error:
        print("Error al eliminar datos:", error)
    finally:
        conexion.close()
