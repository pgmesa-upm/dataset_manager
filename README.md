
# DATASET MANAGER (V-2.0) (solo compatible con Windows)

### Autor
Pablo García Mesa
- pgmesa.sm@gmail.com
- https://github.com/pgmesa-upm/dataset_manager

### 0. Descripción
Esta herramienta se ha creado para facilitar el manejo actual y futuro del dataset del estudio de esclerosis múltiple,
llevado a cabo por la UPM en colaboración con el oftalmológico del Gregorio Marañón 

Viene con un fichero .bat para inicializar el programa. Es necesario que en la carpeta del disco duro donde se encuentre, haya, en el mismo directorio padre, un interprete de python instalado con el nombre (.python) (>= 3.9) (revisar codigo de .bat para más información). Si no está presente se podrá utilizar un interprete del propio ordenador ejecutando el archivo main.py (si todas las dependencias están instaladas -> mirar requirements.txt)

EL programa cuenta con unos cuantos comandos para interactuar con los dos datasets (raw y clean): muestra información 
sobre el contenido de ambos datasets, los compara y permite identificar cundo hay datos nuevos disponibles para procesar y permite procesarlos de forma automática

Entre los módulos que utiliza este programa, destaca un paquete creado (por el autor de este programa) para usar como libreria en este script y en el del algoritmo, el cual permite interactuar con el dataset del estudio y acceder a los datos (PyPI - upm_oct_dataset_utils - https://github.com/pgmesa-upm/upm_oct_dataset_utils) 

Al iniciar el programa se desplegará una consola de comandos con una propia terminal, la cual solo reconocerá comandos propios del programa. 
```
>
> echo
[!] 'echo' command doesn't exist in the program
>
```
Al abrir esta consola, también se desplegará parcialemente la ayuda del programa.
```
+ DATASET MANAGER (ctrl-c to exit):

[?] Commands:
     => 'raw': Shows raw dataset info. 2 extra modes: 1. only missing info (add -m) 2. only summary (add -s)
     => 'clean': Shows clean dataset info. 2 extra modes: 1. only missing info (add -m) 2. only summary (add -s)
     => 'check': Shows the difference between the 2 datasets. Is usefull to see if there is available data to process (add -a to show all info)
     => 'process': Processes the entire raw dataset (add -o to override existing clean files)
     => 'exit': Exits from the program
[?] Global Flags:
     => '-h': shows command help
     => '-hq': shows information about how to use specific queries in a command
[%] *INFO: commands 'raw', 'clean', 'check' and 'process' admits specific queries (-hq to know more)

 -  Enter command:
>
```
Como se observa en la ayuda, los comandos del programa admiten parámetros extra para personalizar los comandos a ejecutar. Para desplegar la ayuda sobre como añadir estos parámetros a los comandos hay que introducir '-hq':
```
> -hq

    [?] How to make queries (always use ',' for enums without ' ' after it):
    - 3 options (only in those commands which support it):
    1. '-g=' - Choose one or more groups. Ex: -g=control,MS,NMO
    2. '-p=' - Choose one or more patients (ranges are supported: 1-5,4,12-16). Ex: -p=1-5,8,9 -> [1,2,3,4,5,8,9]
    4. '-s=' - Choose one or more studies. Ex: -s=1,2 or -s=12-10-2021,13-4-2022
    3. '-d=' - Choose one or more data types. Ex: -d=OCT,retinography,XML

    *INFO: For acronyms use upper case, otherwise the query will fail.
        - If nothing is specified, all options are processed

>
```
### 1. Ejemplos de Uso
#### Mostrar la información del raw dataset para ver que estudios o adquisiciones quedan todavía por exportar de los pacientes o no existen, de los grupos de control y esclerosis
```
raw -g=control,MS
```
Output:
```
> raw -g=control,MS
+ RAW DATASET INFO (Path -> 'D:\study_datasets\raw_dataset')

    - Adquisitions per patient study:
        -> 4 OCT (macular_OD, macular_OS, optic-nerve_OD, optic-nerve_OS)
        -> 4 OCTA (macular_OD, macular_OS, optic-nerve_OD, optic-nerve_OS)
        -> 2 retinographies (OD, OS)
        -> 8 scans XML analysis report

----------------------------------------------------
+ CONTROL GROUP (size=21)
- 'patient-1' (studies=1) has all adquisitions
- 'patient-2' (studies=1) has all adquisitions
- 'patient-3' (studies=1) has all adquisitions
...
+ SUMMARY (queried-studies=21):
    -> OCT Cubes => 84/84 (100.0%) -> (0 missing)
    -> OCTA Cubes => 84/84 (100.0%) -> (0 missing)
    -> Retina Images => 42/42 (100.0%) -> (0 missing)
    -> XML scans => 168/168 (100.0%) -> (0 missing)
-> Global data = 378/378 (100.0%) -> (0 missing)
----------------------------------------------------
----------------------------------------------------
+ MS GROUP (size=26)
- 'patient-1' (studies=1) has all adquisitions
- 'patient-2' (studies=1) has all adquisitions
- 'patient-3' (studies=1) has all adquisitions
- 'patient-4' (studies=1) has all adquisitions
- 'patient-5' (studies=1) has missing info:
    {
        "study_06-10-2021": {
            "retinography": "OD and OS missing"
        }
    }
- 'patient-6' (studies=1) has all adquisitions
- 'patient-7' (studies=1) has missing info:
    {
        "study_13-10-2021": {
            "OCTA": "macula left missing",
            "XML": {
                "OCTA_macula_OS": "missing"
            }
        }
    }
- 'patient-8' (studies=1) has missing info:
    {
        "study_14-10-2021": {
            "retinography": "OD and OS missing"
        }
    }
...
```
#### Mostrar un resumen de los estudios procesados en el clean dataset de los grupos de control y esclerosis
```
clean -g=control,MS -s
```
Output:
```
> clean -g=control,MS -s
+ CLEAN DATASET INFO (Path -> 'D:\study_datasets\clean_dataset')

    - Adquisitions per patient:
        -> 4 OCT (macular_OD, macular_OS, optic-nerve_OD, optic-nerve_OS)
        -> 4 OCTA (macular_OD, macular_OS, optic-nerve_OD, optic-nerve_OS)
        -> 2 retinographies (OD, OS)
        -> 8 scans in JSON analysis report

----------------------------------------------------
+ CONTROL GROUP (size=21)
+ SUMMARY:
    -> OCT Cubes => 44/84 (52.38%) -> (40 missing)
    -> OCTA Cubes => 84/84 (100.0%) -> (0 missing)
    -> Retina Images => 42/42 (100.0%) -> (0 missing)
    -> JSON scans => 88/168 (52.38%) -> (80 missing)
-> Global data = 258/378 (68.25%) -> (120 missing)
----------------------------------------------------
----------------------------------------------------
+ MS GROUP (size=26)
+ SUMMARY:
    -> OCT Cubes => 44/104 (42.31%) -> (60 missing)
    -> OCTA Cubes => 51/104 (49.04%) -> (53 missing)
    -> Retina Images => 24/52 (46.15%) -> (28 missing)
    -> JSON scans => 79/208 (37.98%) -> (129 missing)
-> Global data = 198/468 (42.31%) -> (270 missing)
----------------------------------------------------
```
#### Procesar las imagenes de OCTA de los pacientes 1 al 16, el 18 y el 20 de los grupos 'control' y 'esclerosis múltiple', sobreescribiendo los ficheros en caso de que ya existieran (imaginemos que los queremos procesar de otra manera a los anteriores, para ver que efecto puede tener sobre el algoritmo que procese luego los datos)
```
process -g=control,MS -p=1-16,8,20 -d=OCTA -o
```
Output:
```
> process -g=control,MS -p=1,2 -d=OCTA -o
INFO:dataset_manager: ----------- Procesing raw_dataset into clean_dataset -----------
INFO:dataset_manager: -> Raw Dataset Path => 'D:/study_datasets/raw_dataset'
INFO:dataset_manager: -> Clean Dataset Path => 'D:/study_datasets/clean_dataset'
INFO:dataset_manager: => CONTROL GROUP
INFO:dataset_manager:  + Processing 'patient-1' data
INFO:dataset_manager:   -'study_03-11-2021'
INFO:dataset_manager:      -> saving raw (.img) 'OCTA_macula_right' as tiff (.tif) (overriding)
INFO:dataset_manager:      -> saving raw (.img) 'OCTA_macula_left' as tiff (.tif) (overriding)
INFO:dataset_manager:      -> saving raw (.img) 'OCTA_optic-nerve_right' as tiff (.tif) (overriding)
INFO:dataset_manager:      -> saving raw (.img) 'OCTA_optic-nerve_left' as tiff (.tif) (overriding)
INFO:dataset_manager:  + Processing 'patient-2' data
INFO:dataset_manager:   -'study_25-10-2021'
INFO:dataset_manager:      -> saving raw (.img) 'OCTA_macula_right' as tiff (.tif) (overriding)
...
INFO:dataset_manager: => MS GROUP
INFO:dataset_manager:  + Processing 'patient-1' data
INFO:dataset_manager:   -'study_21-09-2021'
INFO:dataset_manager:      -> saving raw (.img) 'OCTA_macula_right' as tiff (.tif) (overriding)
INFO:dataset_manager:      -> saving raw (.img) 'OCTA_macula_left' as tiff (.tif) (overriding)
INFO:dataset_manager:      -> saving raw (.img) 'OCTA_optic-nerve_right' as tiff (.tif) (overriding)
INFO:dataset_manager:      -> saving raw (.img) 'OCTA_optic-nerve_left' as tiff (.tif) (overriding)
INFO:dataset_manager:  + Processing 'patient-2' data
INFO:dataset_manager:   -'study_21-09-2021'
INFO:dataset_manager:      -> saving raw (.img) 'OCTA_macula_right' as tiff (.tif) (overriding)
...
INFO:dataset_manager: ------------------ End, Raw Dataset processed ------------------
```
#### Comparar los dataset raw y clean para ver que OCTs todavía no se han procesado de los grupos de control y esclerosis, mostrando toda la información
```
check -g=control,MS -d=OCT -a
```
Output:
```
> check -g=control,MS -d=OCT -a
=> AVAILABLE DATA TO PROCESS:
+ 'CONTROL' GROUP
- 'patient-12' has data to process
    {
        "study_05-11-2021": {
            "OCT": {
                "macula": [
                    "right",
                    "left"
                ],
                "optic-nerve": [
                    "right",
                    "left"
                ]
            }
        }
    }
- 'patient-13' has data to process
    {
        "study_16-11-2021": {
            "OCT": {
                "macula": [
                    "right",
                    "left"
                ],
                "optic-nerve": [
                    "right",
                    "left"
                ]
            }
        }
    }
+ 'MS' GROUP
...
```
### 2. Limitaciones
Los scripts en sí que usa el programa tienen gran cantidad de funcionalidades y posibilidades para buscar información, cambiar la forma del procesado etc, pero este programa de consola quelos utiliza es limitado por ahora y no permite acceder a muchas de las opciones que ofrecen los script. La búsqueda de información si se ha implementado casi al completo, pero la personalización del procesado todavía no. En un futuro convendría implementarlo con un fichero de configuración, pero de momento para el estudio no parece necesario, ya que una vez definida la forma de procesar, lo normal es dejarlo todo igual a no ser que se quiera reprocesar todo el dataset con otra configuración. Para hacer esto último requeriría cambiar los parámetro direcamente desde los scripts. También hay muchas otras funcionalidades que se podrían añadir y formas de reescribir el código de manera más eficiente, pero que por falta de tiempo no se han podido implementar.


