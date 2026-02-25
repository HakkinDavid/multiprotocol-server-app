# README

## Requisitos previos

* Python 3.11
* Node.js 24
* npm 11.6

---

## Backend

1. Abrir una terminal.
2. Navegar al subdirectorio `backend`.

```bash
cd backend
```

3. Crear un entorno virtual utilizando Python 3.11.

```bash
python3.11 -m venv venv
```

4. Activar el entorno virtual.

En macOS o Linux:

```bash
source venv/bin/activate
```

En Windows:

```bash
venv\Scripts\activate
```

5. Instalar las dependencias utilizando Python 3.11 y el archivo `requirements.txt`.

```bash
pip install -r requirements.txt
```

6. Crear el archivo `.env` dentro de la subcarpeta `app`, siguiendo el formato indicado en el archivo de ejemplo correspondiente.

7. Colocar el modelo serializado en la siguiente ruta:

```
[raíz]/training/models/best_model_MultiOutputRegressor.joblib
```

8. Iniciar el servidor con Uvicorn.

```bash
uvicorn app.main:app --reload
```

El backend quedará disponible en el puerto configurado por defecto.

---

## Frontend

1. Abrir una nueva terminal.
2. Navegar al subdirectorio `frontend`.

```bash
cd frontend
```

3. Instalar las dependencias con npm 11.6.

```bash
npm i
```

4. Iniciar el servidor de desarrollo.

```bash
npm run devHost
```

El frontend quedará disponible en el puerto indicado por la configuración del proyecto.

## Uso del sistema
	1.	Abrir la aplicación web en el navegador una vez que el servidor de desarrollo esté en ejecución y navegar al menú de Machine Learning.
	2.	En el formulario principal, seleccionar el equipo local en el primer menú desplegable.
	3.	Seleccionar un equipo distinto como visitante en el segundo menú desplegable.
	4.	Ingresar los goles del equipo local al medio tiempo en el campo correspondiente.
	5.	Ingresar los goles del equipo visitante al medio tiempo en el campo correspondiente.
	6.	Presionar el botón Predecir.

La aplicación enviará los datos al backend y mostrará en pantalla los goles finales estimados para ambos equipos, junto con el resultado derivado del encuentro.