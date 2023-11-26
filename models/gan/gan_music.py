from music21 import note, chord, stream
from tensorflow.keras.models import load_model
import numpy as np


def get_note(note_c, instr):
    """Regresa una nota"""
    new_note = note.Note(note_c)
    new_note.storedInstrument = instr
    return new_note

def get_chord(pattern, offset, instr):
    """REgresa un arcorde"""
    notes_in_chord = pattern.split(' ')
    notes = []
    for current_note in notes_in_chord:
        notes.append(get_note(current_note, instr))
    new_chord = chord.Chord(notes)
    new_chord.offset = offset

def get_music(model, dataset, length=500):
    """Generamos una pista"""
    latent_dim=100
    n_vocab = len(set(dataset))
    generator_model = load_model(model)
    
    #Generamos una pista empezando por una alearoria
    predictions = generator_model.predict(np.random.normal(0, 1, (1, latent_dim)))
    #Creamos el diccionario para saber el nombre de los acordes
    pred_notes = [x * (n_vocab / 2) + (n_vocab / 2) for x in predictions[0]]
    int_to_note = dict((number, note) for number, note in enumerate(set(dataset)))
    pred_notes_mapped = [int_to_note[int(x[0])] for x in pred_notes]
    
    return pred_notes_mapped[:length]  

def create_midi(pred_notes_mapped, instr):
    """Convertimos una pista a midi"""
    offset = 0
    output_notes = []
    output_notes.append(instr)

    #Convertimos las notas y los acordes correspondientes en música
    for item in pred_notes_mapped:
        pattern = item[0]
        # pattern is a chord
        if ' ' in pattern:
            output_notes.append(get_chord(pattern,offset,instr))
        # pattern is a note
        else:
            output_notes.append(get_note(pattern, instr))

        #Para que no se empalmen
        offset += 0.5

    return stream.Stream(output_notes)
   