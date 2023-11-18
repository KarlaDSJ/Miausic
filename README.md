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
