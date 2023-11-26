# Miausic
Página web para crear música generativa con restricciones teóricas

## Linux 

### Instalación 
```
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```
### Ejecución
```
source venv/bin/activate
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

## Windows
### Instalación
```
python3 -m venv venv
venv/bin/activate
pip3 install -r requirements.txt
```

### Ejecución
```
venv/bin/activate
set FLASK_APP=app.py
set FLASK_ENV=development
flask run
```


## Requerimientos 

Ess necesario tener instalado:
- MuseScore (para generar la partitura) https://musescore.org/es 

Configurar music21
```
music21.configure
```
Indicamos dónde se encuentra la app MuseScore (ejemplo en Mac)
```
environment.set("musescoreDirectPNGPath", "/Applications/MuseScore 4.app/Contents/MacOS/mscore")
```

- fluidsynth (para convertir de midi a mp3)
```
brew install fluid-synth
```