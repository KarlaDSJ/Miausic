from music21 import note, chord, stream, instrument, meter, tempo
import mingus.core.notes as notes
from tensorflow.keras.models import load_model
import numpy as np

def get_note(note_c, instr):
    """Regresa una nota"""
    new_note = note.Note(note_c)
    new_note.storedInstrument = instr
    return new_note

def get_chord(pattern, offset):
    """Regresa un arcorde"""
    notes_in_chord = pattern.split(' ')
    new_chord = chord.Chord(notes_in_chord)
    new_chord.offset = offset

def get_music(model, dataset, escala, length=100):
    """Generamos una pista"""
    latent_dim=100
    n_vocab = len(set(dataset))
    int_to_note = dict((number, note) for number, note in enumerate(set(dataset)))
    note_to_int = dict((note, number) for number, note in enumerate(set(dataset)))
    generator_model = load_model(model)
    
    #Generamos una pista empezando por una escala dada
    escala = [notes.note_to_int(x) for x in escala]
    j = []
    for _ in range(latent_dim//8+1):
        j += escala 
    predictions = generator_model.predict(np.array(j[:latent_dim]).reshape((1, latent_dim)))
    #Creamos el diccionario para saber el nombre de los acordes
    pred_notes = [x * (n_vocab / 2) + (n_vocab / 2) for x in predictions[0]]
    pred_notes_mapped = [int_to_note[int(x[0])] for x in pred_notes]
    
    return pred_notes_mapped[:length]  

def create_midi(pred_notes_mapped, compas, bpm, instr=instrument.Violin()):
    """Convertimos una pista a midi"""
    output_notes = stream.Stream()
    output_notes.append(meter.TimeSignature(compas))
    output_notes.append(tempo.MetronomeMark(number=bpm))
    output_notes.append(instr)

    #Convertimos las notas y los acordes correspondientes en música
    for item in pred_notes_mapped:
        pattern = item
        # pattern is a chord
        if ' ' in pattern:
            output_notes.append(chord.Chord(item.split()))
        # pattern is a note
        else:
            output_notes.append(get_note(pattern, instr))

    return output_notes
   