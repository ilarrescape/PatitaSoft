# PatitaSOFT 🐾

Sistema integral para el refugio Patitas (Pinamar), construido con **Python + Streamlit + MySQL** y preparado para **Railway**.

## Qué incluye

- Login y registro (el primer usuario queda como administrador).
- Gestión de perritos y estados.
- Historia clínica y salud.
- Ingresos, donaciones y gastos.
- Inventario de medicamentos, alimento e insumos, con stock mínimo y movimientos.
- Veterinarias, empresas, organizaciones y proveedores.
- Adopciones y datos de adoptantes.
- Castraciones de perros y gatos.
- Dashboard con KPIs y gráficos Plotly.
- Categorías con colores HEX configurables.
- CRUD mediante selección en `st.dataframe` + ventanas `st.dialog`.
- Exportación a Excel y PDF en cada módulo.
- Diseño alineado al logo de PatitaSOFT.
- Roles: `admin`, `operator`, `viewer`.

> Nota sobre chips: Streamlit puede mostrar opciones tipo etiqueta en determinados componentes, pero no permite definir un color HEX diferente por opción dentro de cada celda editable de `st.data_editor`. Por eso PatitaSOFT guarda el HEX en MySQL, permite editarlo en el módulo Categorías y muestra una vista previa en chips. El esquema queda listo para usar esos colores en visualizaciones y estilos.

## Ejecutarlo en local

### 1. Crear la base de datos

En MySQL:

```sql
create database patitasoft character set utf8mb4 collate utf8mb4_unicode_ci;
```

No hace falta ejecutar `sql/schema.sql` manualmente: la aplicación crea tablas y categorías iniciales al arrancar.

### 2. Crear entorno

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Variables de entorno

Copiá `.env.example` a `.env` y completá los datos de MySQL. Streamlit también puede leer `.streamlit/secrets.toml` con este formato:

```toml
[mysql]
host = "localhost"
port = 3306
database = "patitasoft"
user = "root"
password = "tu_password"
```

Para una prueba rápida en Linux:

```bash
export MYSQLHOST=localhost
export MYSQLPORT=3306
export MYSQLDATABASE=patitasoft
export MYSQLUSER=root
export MYSQLPASSWORD=tu_password
streamlit run app.py
```

Abrí `http://localhost:8501`.

## Desplegar en Railway paso a paso

### 1. Subir a GitHub

Descomprimí el ZIP, entrá a la carpeta `PatitaSOFT` y ejecutá:

```bash
git init
git add .
git commit -m "PatitaSOFT inicial"
git branch -M main
git remote add origin TU_URL_DE_GITHUB
git push -u origin main
```

### 2. Crear proyecto en Railway

1. Railway → **New Project**.
2. **Deploy from GitHub repo** y elegí el repositorio.
3. Dentro del mismo proyecto: **Add Service → Database → MySQL**.
4. Railway generará las variables de MySQL.

### 3. Variables del servicio Streamlit

En el servicio de PatitaSOFT → **Variables**, vinculá/copiá las variables del MySQL:

- `MYSQLHOST`
- `MYSQLPORT`
- `MYSQLDATABASE`
- `MYSQLUSER`
- `MYSQLPASSWORD`
- `APP_SECRET` con una cadena larga aleatoria (reservada para futuras funciones).

Si Railway usa nombres equivalentes en el servicio MySQL, creá estas variables en el servicio web referenciando los valores del servicio de base de datos.

### 4. Comando de inicio

El proyecto ya incluye `Procfile`:

```text
web: streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT --server.headless=true
```

Si Railway no lo toma automáticamente, configurá ese mismo texto como **Start Command**.

### 5. Generar dominio

En **Settings → Networking → Generate Domain**. La primera carga creará todas las tablas y categorías.

### 6. Primer usuario

Entrá al dominio, elegí **Registrarse** y creá la primera cuenta. Esa cuenta recibe rol `admin`. Después, desde **Usuarios**, podés cambiar roles o desactivar accesos.

## Recomendaciones de producción

- Activar backups del MySQL de Railway.
- Usar un dominio propio con HTTPS.
- Crear al menos dos administradores.
- Restringir el registro público después de crear el equipo si el refugio no lo necesita (podés eliminar/ocultar la pestaña Registro).
- Para comprobantes, fotos y documentos, agregar Cloudflare R2/S3 en una segunda etapa en vez de guardar blobs dentro de MySQL.
- Agregar auditoría detallada (quién editó/eliminó cada registro) si el equipo tiene muchos operadores.

## Estructura

```text
PatitaSOFT/
├── app.py
├── assets/logo.png
├── core/
│   ├── auth.py
│   ├── db.py
│   ├── exporters.py
│   ├── helpers.py
│   └── ui.py
├── views/
│   ├── dashboard.py
│   ├── dogs.py
│   ├── health.py
│   ├── finance.py
│   ├── inventory.py
│   ├── partners.py
│   ├── adoptions.py
│   ├── castrations.py
│   ├── categories.py
│   └── users.py
├── sql/schema.sql
├── requirements.txt
└── Procfile
```
