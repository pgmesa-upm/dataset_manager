
# DATASET MANAGER (V-1.0) (solo compatible con Windows)

### Autor
Pablo García Mesa
- pgmesa.sm@gmail.com
- https://github.com/pgmesa-upm/excel_manager

### 0. Descripción
Esta herramienta se ha creado para facilitar el actual y el futuro manejo del dataset del estudio de esclerosis múltiple,
llevado a cabo por la UPM en colaboración con el oftalmológico del Gregorio Marañón 

Viene con un fichero .bat para inicializar el programa. Es necesario que en la carpeta del disco donde se encuentre haya, en 
el mismo directorio padre, un interprete de python instalado (revisar codigo de .bat para más información). Si no está presente se podrá utilizar un interprete del propio ordenador ejecutando el archivo main.py (si todas las dependencias están instaladas -> mirar requirements.txt)

EL programa cuenta con unos cuantos comandos para interactuar con los dos datasets (raw y clean): muestra información 
sobre el contenido de ambos datasets, los compara y permite identificar cundo hay datos nuevos disponibles para procesar
y permite procesarlos de forma automática

### 1. Limitaciones
Los scripts en sí que usa el programa tienen gran cantidad de funcionalidades y posibilidades para buscar información, cambiar la forma del procesado, etc, pero el programa de consola que controla el programa es muy limitado (solo se han incluido unas funciones básicas predefinidas, sin mucha oportunidad de introducir argumentos extra o flags para personalizar la ejecución). A pesar de esto, tiene gran utilidad para el estudio y además esta limitación es facil de mejorar