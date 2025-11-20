REQUERIMIENTOS TÉCNICOS - SISTEMA DE TRANSPORTES
================================================

REQUISITOS DEL SISTEMA
----------------------

• Python 3.8 o superior
• Sistema operativo: Windows, macOS o Linux
• Navegador web moderno (Chrome, Firefox, Edge, Safari)
• Mínimo 2GB de RAM

DEPENDENCIAS DE PYTHON
----------------------

Las siguientes librerías deben estar instaladas:

streamlit==1.28.0
sqlite3 (incluido en Python por defecto)

ARCHIVOS NECESARIOS
-------------------

El proyecto debe contener estos archivos en la misma carpeta:

main.py                 (aplicación principal)
funciones_crud.py       (módulo de base de datos)
base_de_datos_transportes.db  (se crea automáticamente)

INSTALACIÓN
-----------

1. Instalar Python desde python.org
2. Instalar Streamlit ejecutando:
   pip install streamlit==1.28.0

3. Verificar instalación:
   streamlit version

EJECUCIÓN
---------

1. Abrir terminal/consola
2. Navegar a la carpeta del proyecto
3. Ejecutar: streamlit run main.py

VERIFICACIÓN
------------

Si la aplicación no funciona, verificar:

1. Python está instalado: python --version
2. Streamlit está instalado: streamlit version
3. Los archivos .py están en la misma carpeta

SOLUCIÓN DE PROBLEMAS
---------------------

Error: "ModuleNotFoundError"
• Ejecutar: pip install streamlit

Error: "No module named funciones_crud"
• Verificar que funciones_crud.py está en la misma carpeta

NOTAS TÉCNICAS
---------------

• La base de datos se crea automáticamente
• Los datos se guardan en SQLite local
• No se requiere conexión a internet después de la instalación
• Compatible con Python 3.8-3.11
