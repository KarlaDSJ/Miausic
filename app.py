from flask import Flask
from flask import render_template
from flask import request
import os
import numpy as np
import pickle
from music21 import converter, instrument
from models.gan.gan_music import *
from models.genetic import *

app = Flask(__name__)

instru = {'piano':instrument.Piano(), 'violin': instrument.Violin(), 'guitarra':instrument.AcousticGuitar()}
scala = {"Ionian": scales.Ionian,
          "Dorian": scales.Dorian,
          "Phrygian": scales.Phrygian,
          "Lydian": scales.Lydian,
          "Mixolydian":scales.Mixolydian,
          "Aeolian": scales.Aeolian,
          "Locrian": scales.Locrian,
          "Mayor": scales.Major,
          "Armonica mayor": scales.HarmonicMajor,
          "Menor": scales.NaturalMinor,
          "Cromática": scales.Chromatic,
          "Octatónico": scales.Octatonic}

def change_instrument(instrumento):
    """Guardamos la partitura y cambiamos el instrumento"""
    s=converter.parse("static/results/res.mid")
    for p in s.parts:
        p.insert(0, instrumento)
    s.write('musicxml.pdf', fp='static/results/res.pdf')
    os.system(f'fluidsynth -ni static/Touhou.sf2 static/results/res.mid -F static/results/res.wav -r 44100')

def save_music(escala, beat, instrumento, compas, duracion):
    """Crea y guarda la partitura, un archivo midi y otro mp3"""
    with open('models/gan/objects/notes.pickle', 'rb') as f:
        notes = pickle.load(f)
        generated_music = get_music('models/gan/objects/generator_model.h5', np.array(notes['pitch']), escala.ascending(), duracion*5)
        midi_gan = create_midi(generated_music, compas, beat, instrumento)
        #Guardamos los archivos para mostrarlos 
        midi_gan.write('midi', fp='static/results/res.mid')
        change_instrument(instrumento)

def create_music(escala, nota, beat, instrumento, compas, duracion):
    # Crear la composición usando acordes generados por el algoritmo genético modificado
    composicion = Composition()
    acordes_generados = algoritmo_genetico(10, 10, escala, nota)
    compas = compas.split('/')
    compas = [int(compas[0]),int(compas[1])]
    track = crear_track_con_acordes(acordes_generados, duracion*2, (compas[0],compas[1]))  # 5 barras por track
    composicion.add_track(track)
    composicion.set_author("Miausic")
    # Salida a un archivo MIDI
    midi_file_out.write_Composition("static/results/res.mid", composicion, beat)
    # Guardamos los archivos y decidimos el intrumento a utilizar
    


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/crear')
def crear():
    return render_template('crear.html')

@app.route('/submit', methods=['POST'])
def submit():
    #Aquí obtenemos las restricciones
    print(request.form)
    instrumento = instru[request.form['instrumento']]
    compas = request.form['compas']
    bpm = int(request.form['beats'])
    nota = request.form['nota']
    duracion = int(request.form['duracion'])
    escala = scala[request.form['escalas']](nota)
    #Creamos la pista
    if request.form.get('gan') != None:
        save_music(escala, bpm, instrumento, compas, duracion)
    else:
        create_music(escala, nota, bpm, instrumento, compas, duracion)
    return render_template('pista.html')

if __name__ == "__main__":
    app.run(debug=True)