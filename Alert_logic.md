# Lógica para las alertas + crear tabla solo para las alertas
## Edificio
Si se produce una salida del edificio dentro del horario establecido  
Mensaje alerta: "El user_id XXXXX ha salido del edificio a la hora timestamp"

## Baño
Si un usuario está dentro de Baño > 10 minutos  
Mensaje alerta: "El user_id XXXXX lleva más de 10 minutos en el baño, por favor comprobar estado"

## Clases
Si se supera nº máximo dispositivos por clase, por ejemplo > 10  
Mensaje alerta: "En la clase X se ha superado el aforo máximo de personas"

## Teacher
Si no hay id_Teacher dentro de clase X > 10 minutos & id alumnos dentro de clase X != 0  
Mensaje alerta: "La clase X no dispone de profesor, por favor atender"
