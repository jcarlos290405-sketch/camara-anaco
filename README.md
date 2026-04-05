# Sistema de Gestión - Cámara de Comercio, Industrias y Servicios de Anaco-Anzoátegui

Sistema web profesional para la gestión de solicitudes de afiliación y administración de afiliados.

## Características

- Formulario público de solicitud de afiliación (wizard de 5 pasos)
- Panel de administración con dashboard KPI
- Gestión de solicitudes, afiliados y links compartidos
- Notificaciones por correo electrónico (SMTP)
- Generación de códigos QR para links compartidos
- Interfaz moderna y responsive con Tailwind CSS

## Requisitos

- Python 3.8+

## Instalación

### Local

```bash
cd camara_comercio
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Variables de Entorno

Configure las siguientes variables de entorno antes de ejecutar la aplicación:

| Variable | Descripción | Ejemplo | Requerida |
|----------|-------------|---------|-----------|
| `SECRET_KEY` | Clave secreta para sesiones Flask | `tu-clave-segura` | Sí |
| `DATABASE_URL` | URL de conexión a base de datos | `sqlite:///camara_comercio.db` | Sí |
| `FLASK_DEBUG` | Modo debug (True/False) | `False` | No |
| `SMTP_SERVER` | Servidor SMTP | `smtp.gmail.com` | Sí |
| `SMTP_PORT` | Puerto SMTP | `587` | Sí |
| `EMAIL_USER` | Usuario de correo | `tu@email.com` | Sí |
| `EMAIL_PASSWORD` | Contraseña de aplicación | `tu-app-password` | Sí |
| `SMTP_FROM_EMAIL` | Correo remitente | `noreply@email.com` | Sí |
| `SMTP_TO_EMAIL` | Correo destinatario | `admin@email.com` | Sí |
| `MAIL_USE_TLS` | Usar TLS (True/False) | `True` | No |
| `ADMIN_PASSWORD` | Contraseña inicial del admin | `tu-password-seguro` | Sí (producción) |

### Ejecutar

```bash
python app.py
```

### Abrir en el navegador

```
http://localhost:5000
```

## Despliegue en Render

1. Conectar repositorio de GitHub a Render
2. Configurar todas las variables de entorno en el dashboard de Render
3. El despliegue es automático tras cada push a la rama `main`

## Rutas Principales

| Ruta | Descripción |
|------|-------------|
| `/` | Página pública |
| `/solicitud` | Formulario de afiliación (wizard) |
| `/login` | Panel de administración |
| `/admin` | Dashboard |
| `/admin/solicitudes` | Gestión de solicitudes |
| `/admin/afiliados` | Gestión de afiliados |
| `/admin/links` | Generación de links compartidos |

## Estructura del Proyecto

```
camara_comercio/
├── app.py              # Aplicación principal
├── models.py           # Modelos de base de datos
├── config.py           # Configuración
├── requirements.txt    # Dependencias
├── templates/          # Plantillas HTML
└── static/
    └── uploads/        # Archivos subidos
```

## Tecnologías Utilizadas

- **Backend:** Flask, SQLAlchemy, Flask-Login
- **Frontend:** Tailwind CSS, Chart.js, Font Awesome 6
- **Base de Datos:** SQLite (configurable para PostgreSQL en producción)
- **Email:** SMTP

## Licencia

© 2026 Cámara de Comercio, Industrias y Servicios de Anaco-Anzoátegui
