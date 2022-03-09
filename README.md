# Data Project 2 - Master Data Analytics EDEM 2022

| ![](https://github.com/aloa04/dataproject-2/blob/main/media/safe-place-logo.png?raw=true) | **IoT for a safer life**<br /><br />Cloud based IoT software |
| ------------------------------------------------------------ | :----------------------------------------------------------: |

## Meet our team

- [Julen Aguirreurreta](https://github.com/juagvi)
- [Enrique Badenas](https://github.com/Enriquebadenas)
- [Pablo Bottero](https://github.com/aloa04)
- [Sergi García](https://github.com/S3gam)
- [Ismail Kinani](https://github.com/kinaflux)



## Proyecto

El objetivo del proyecto es diseñar una solución basada en cloud que emplee dispositivos IoT y sistemas de software para gestionar la presencialidad de alumnos y profesores en centros escolares. De este modo, se evita que alumnos y alumnas falten a clase o detectar si hay algún percance a durante la jornada escolar.

## Requisitos de software

En Google Cloud empleamos los siguientes servicios

- PubSub
- Cloud Storage
- Data Flow
- BigQuery
- Cloud Functions
- IOT Core





Además, empleamos Python 3.7 en DataFlow para crear la lógica para concocer si los alumnos entran o salen de clase. También se utiliza en CLoud Functions para detectar si alguna persona permanece demasiado tiempo en las zonas "de paso".



Por último, toda la infromación se visualiza en Data Studio, desde donde se puede controlar, gracias a la sincronización con BigQuery, las personas que hay en cada aula, así como visualizar las tablas de alertas para que el personal pueda actuar sobre ellas.






## Configuración del sistema

**PubSub**
En primer lugar, creamos un Topic y la suscripción por defecto.

Desde la página PubSub de Cloud Console, creamos el Topic con un nombre único y añadimos una suscripción por defecto. Tanto los Topics como las suscripciones son necesarios en los siguientes pasos para crear la canalización de datos.



**IoT Core**

Para esta demostración, utilizaremos Cloud Shell como simulador de datos IoT. Hemos creado un script en Python para simular los sensores (uno por sala) y el movimiento de persdonas entre ellos. 

Desde Cloud Console IoT Core hemos creado registro IoT eligiendo uno de los Temas PubSub creados anteriormente y desde Cloud Shell generamos una clave RSA con un certificado X509 autofirmado. Una vez hecho esto, registramos los dispositivos y subimos los archivos rsa_cert.pem en la sección de autenticación.

Ahora, hemos vinculado nuestro dispositivo (Cloud Shell) con IoT Core.



**Cloud Storage**

Creamos un Bucket especificando un nombre único para poder almacenar la plantilla de Dtaflow.



**BigQuery**

En BigQuery se almacenarán las diferentes tablas que empleamos en el proyecto:

1. Una automática completada por DataFlow
2. Alertas. Aquí se almacenan las personas que están demasiado tiempo fuera de las clases o en zonas supervisadas.
3. Pulseras. Donde se vincula el ID de las pulseras con toda la información del alumno.
4. Sensores. Aquí se guarda la información de donde está ubicado cada sensor.



**DataFlow**

Desde Dataflow leemos los datos producidos por IoT Core y se procesan para comprobar si la persona entra o sale del aula. Tras ello se almacena en BigQuery. Además También se procesa con Cloud Funtions las alertas para controlar la presencialidad de los alumnos.



**Data Studio**

Finalmente, desde Data Studio se leen directamente los datos de BigQuery y se muestran en un dashboard interactivo.



**Video del funcionamiento**

(https://youtu.be/qCENhMNpZdA)



## Aplicaciónes para el cliente

El personal de administración controla que los alumnos y los profesores estén en las aulas o zonas comunes y avisa de posibles incidencias. Data Saturio

