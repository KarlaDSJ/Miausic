import mingus.core.scales as scales
import mingus.core.chords as chords
import mingus.core.progressions as progressions
from mingus.containers import Note, Bar, Track, Composition
from mingus.midi import midi_file_out
import random

# Función para evaluar si un acorde se ajusta a una escala
def se_ajusta_a_escala(escala, acorde):
    return all(nota in escala for nota in acorde)

# Función para generar un acorde mayor aleatorio
def generar_acorde_aleatorio(notas_posibles):
    return chords.major_triad(random.choice(notas_posibles))

# Función para evaluar si un acorde se ajusta a una escala
def se_ajusta_a_escala(escala, acorde):
    return all(nota in escala for nota in acorde)

# Función para generar un acorde mayor aleatorio 
def generar_acorde_aleatorio(notas_posibles):
    return chords.major_triad(random.choice(notas_posibles))

# Función para seleccionar los mejores acordes basados en su ajuste a la escala
def seleccionar_mejores(poblacion, escala, num_seleccionados):
    ajustados = [(acorde, se_ajusta_a_escala(escala, acorde)) for acorde in poblacion]
    ajustados.sort(key=lambda x: x[1], reverse=True)
    return [acorde for acorde, ajuste in ajustados[:num_seleccionados]]

# Función para cruzar dos acordes y generar un nuevo acorde
def cruzar(acorde1, acorde2):
    nuevo_acorde = acorde1[:2] + acorde2[2:]
    return nuevo_acorde

# Función para mutar un acorde cambiando una nota al azar
def mutar(acorde, notas_posibles):
    acorde_mutado = acorde.copy()
    indice = random.randint(0, len(acorde_mutado) - 1)
    acorde_mutado[indice] = random.choice(notas_posibles)
    return acorde_mutado

# Función para evaluar la armonía de una secuencia de acordes en una clave
def evaluar_armonia(secuencia, clave):
    funciones = [progressions.determine(chords.from_shorthand(acorde), clave) for acorde in secuencia]
    return all(funcion != [] for funcion in funciones)

# Algoritmo Genético
def algoritmo_genetico(num_generaciones, tam_poblacion, escala):
    notas_posibles = scales.Major(escala).ascending()
    poblacion = [generar_acorde_aleatorio(notas_posibles) for _ in range(tam_poblacion)]

    for _ in range(num_generaciones):
        # Selección
        seleccionados = seleccionar_mejores(poblacion, notas_posibles, tam_poblacion // 2)

        # Evaluación de la armonía
        seleccionados = [acorde for acorde in seleccionados if evaluar_armonia(acorde, escala)]

        # Cruce
        descendencia = []
        while len(descendencia) < tam_poblacion // 2:
            padres = random.sample(seleccionados, 2)
            hijo = cruzar(padres[0], padres[1])
            descendencia.append(hijo)

        # Mutación
        for _ in range(tam_poblacion // 4):
            mutante = mutar(random.choice(poblacion), notas_posibles)
            poblacion.append(mutante)

        poblacion = seleccionados + descendencia

    return poblacion

# Función para crear una barra con un acorde
def crear_barra_con_acorde(acorde, duracion=4):
    bar = Bar()
    bar.meter = duracion
    for nota in acorde:
        bar.place_notes(Note(nota), duracion[0])
    return bar

# Función para crear un track con varias barras de acordes
def crear_track_con_acordes(acordes, num_barras, duracion=4):
    track = Track()
    for acorde in acordes[:num_barras]:
        barra = crear_barra_con_acorde(acorde, duracion)
        track + barra
    return track