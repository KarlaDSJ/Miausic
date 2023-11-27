from music21 import note, chord, stream, instrument, meter, tempo, duration
import mingus.core.chords as chords
from tensorflow.keras.models import load_model
import numpy as np
import random

def get_note(note_c, instr):
    """Regresa una nota"""
    new_note = note.Note(note_c)
    new_note.storedInstrument = instr
    return new_note

def change_scale(chord, escala):
    notes = chord.split(' ')
    aux = []
    for i in notes[:len(notes)//2]:
        if i not in escala:
           aux += escala[random.randint(0,len(escala)-1)]
        else:
            aux += i
    return ' '.join(aux + notes[len(notes)//2:])

def get_music(model, dataset, escala, length=100):
    """Generamos una pista"""
    latent_dim=100
    n_vocab = len(set(dataset))
    int_to_note = dict((number, change_scale(note,escala)) for number, note in enumerate(set(dataset)))
    generator_model = load_model(model)
    
    #Generamos una pista empezando por una alearoria
    predictions = generator_model.predict(np.random.normal(0, 1, (1, latent_dim)))
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
            #new_chord = chords.major_triad(random.choice(item.split()))
            #print(new_chord)
            p = pattern.split()
            m = chord.Chord(p[:len(p)//2])
            m.simplifyEnharmonics(inPlace=True)
            output_notes.append(m)
        # pattern is a note
        else:
            output_notes.append(get_note(pattern, instr))

    return output_notes
   