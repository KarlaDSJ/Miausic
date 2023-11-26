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

def save_music(nota, escala, beat, instrumento, compas):
    """Crea y guarda la partitura, un archivo midi y otro mp3"""
    
    with open('models/gan/objects/notes.pickle', 'rb') as f:
        notes = pickle.load(f)
        generated_music = get_music('models/gan/objects/generator_model.h5', np.array(notes['pitch']))
        midi_gan = create_midi(generated_music, instrumento)
        #Guardamos los archivos para mostrarlos 
        midi_gan.write('midi', fp='static/results/res.mid')
        midi_gan.write('musicxml.pdf', fp='static/results/res.pdf')
        os.system(f'fluidsynth -ni static/Touhou.sf2 static/results/res.mid -F static/results/res.wav -r 44100')

def create_music(nota, escala, beat, instrumento, compas):
    # Crear la composición usando acordes generados por el algoritmo genético modificado
    composicion = Composition()
    acordes_generados = algoritmo_genetico(10, 10, nota)
    compas = [int(compas[0]),int(compas[1])]
    track = crear_track_con_acordes(acordes_generados, 5, (compas[0],compas[1]))  # 5 barras por track
    composicion.add_track(track)
    composicion.set_author("Miausic")
    # Salida a un archivo MIDI
    midi_file_out.write_Composition("static/results/res.mid", composicion, beat)
    # Guardamos los archivos y decidimos el intrumento a utilizar
    s=converter.parse("static/results/res.mid")
    for p in s.parts:
        p.insert(0, instrumento)
    s.write('musicxml.pdf', fp='static/results/res.pdf')
    os.system(f'fluidsynth -ni static/Touhou.sf2 static/results/res.mid -F static/results/res.wav -r 44100')


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/crear')
def crear():
    return render_template('crear.html')

@app.route('/submit', methods=['POST'])
def submit():
    instru = {'piano':instrument.Piano(), 'violin': instrument.Violin(), 'guitarra':instrument.AcousticGuitar()}
    #Aquí obtenemos las restricciones
    print(request.form)
    instrumento = instru[request.form['instrumento']]
    compas = request.form['compas'].split('.')
    bpm = int(request.form['beats'])
    nota = request.form['nota']
    escala = request.form['escalas']
    #Creamos la pista
    if request.form.get('gan') != None:
        save_music(nota, escala, bpm, instrumento, compas)
    else:
        create_music(nota, escala, bpm, instrumento, compas)
    return render_template('pista.html')

if __name__ == "__main__":
    app.run(debug=True)