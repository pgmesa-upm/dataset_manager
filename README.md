
# DATASET MANAGER (V-1.0) (solo compatible con Windows)

### Autor
Pablo García Mesa
- pgmesa.sm@gmail.com
- https://github.com/pgmesa-upm/dataset_manager

### 0. Descripción
Esta herramienta se ha creado para facilitar el manejo actual y futuro del dataset del estudio de esclerosis múltiple,
llevado a cabo por la UPM en colaboración con el oftalmológico del Gregorio Marañón 

Viene con un fichero .bat para inicializar el programa. Es necesario que en la carpeta del disco duro donde se encuentre, haya, en el mismo directorio padre, un interprete de python instalado con el nombre (.python) (>3.9) (revisar codigo de .bat para más información). Si no está presente se podrá utilizar un interprete del propio ordenador ejecutando el archivo main.py (si todas las dependencias están instaladas -> mirar requirements.txt)

EL programa cuenta con unos cuantos comandos para interactuar con los dos datasets (raw y clean): muestra información 
sobre el contenido de ambos datasets, los compara y permite identificar cundo hay datos nuevos disponibles para procesar y permite procesarlos de forma automática

Entre los módulos que utiliza este programa, destaca un paquete creado para usar como libreria en este script y en el del algoritmo, el cual permite interactuar con el dataset del estudio y acceder a los datos (PyPI - upm_oct_dataset_utils - https://github.com/pgmesa-upm/upm_oct_dataset_utils) 

### 1. Limitaciones
Los scripts en sí que usa el programa tienen gran cantidad de funcionalidades y posibilidades para buscar información, cambiar la forma del procesado, etc, pero el programa de consola que controla el estos es limitado por ahora y no permite acceder a muchas de las opciones que ofrecen los script. La busqueda de información si se ha implementado casi al completo, pero la personalización del procesado todavía no. En un futuro convendría implementarlo con un fichero de configuración, pero de momento para el estudio no parece necesario, ya que una vez definida la forma de procesar, lo normal es dejarlo todo igual a no ser que se quiera reprocesar todo el dataset con otra configuración. Para hacer esto último requeriría cambiar los parámetro direcamente desde los scripts. También hay muchas otras funcionalidades que se podrían añadir y formas de reescribir el código de manera más eficiente, pero que por falta de tiempo no se han podido implementar.