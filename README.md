# Sistema de Gestión - Cámara de Comercio, Industrias y Servicios de Anaco-Anzoátegui

Sistema web profesional para la gestión de solicitudes de afiliación y administración de afiliados.

## Características

- Formulario público de solicitud de afiliación (wizard de 5 pasos)
- Panel de administración con dashboard KPI
- Gestión de solicitudes, afiliados y links compartidos
- Notificaciones por correo electrónico (SMTP Gmail)
- Generación de códigos QR para links compartidos
- Interfaz moderna y responsive con Tailwind CSS

## Requisitos

- Python 3.8+
- Gmail con contraseña de aplicación para SMTP

## Instalación

1. **Clonar o entrar al directorio del proyecto:**
```bash
cd camara_comercio
```

2. **Crear entorno virtual e instalar dependencias:**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Ejecutar la aplicación:**
```bash
python app.py
```

4. **Abrir en el navegador:**
```
http://localhost:5000
```

## Credenciales de Acceso

- **Usuario:** CamDCDA26
- **Contraseña:** CAM26COMAN$*

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

## Configuración SMTP

El sistema está pre-configurado con:
- Servidor: smtp.gmail.com
- Puerto: 587
- Remitente: secretariacamaraanaco@gmail.com

Los correos se envían automáticamente cuando se recibe una nueva solicitud.

## Estructura del Proyecto

```
camara_comercio/
├── app.py              # Aplicación principal
├── models.py           # Modelos de base de datos
├── config.py           # Configuración
├── requirements.txt    # Dependencias
├── templates/          # Plantillas HTML
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── solicitudes/
│   ├── afiliados/
│   ├── links/
│   └── publico/
└── static/
    └── uploads/        # Archivos subidos
```

## Capturas de Pantalla

### Dashboard
- Tarjetas KPI con contadores animados
- Gráficos de solicitudes por mes (Chart.js)
- Gráfico doughnut de distribución por sector
- Lista de últimas solicitudes

### Formulario de Solicitud
- Wizard de 5 pasos con barra de progreso
- Drag & drop para documentos
- Validación en tiempo real
- Diseño responsive

### Panel de Administración
- Vista de tarjetas y tabla
- Filtros avanzados
- Tabs para detalle de solicitudes

## Tecnologías Utilizadas

- **Backend:** Flask, SQLAlchemy, Flask-Login
- **Frontend:** Tailwind CSS, Chart.js, Font Awesome 6
- **Base de Datos:** SQLite
- **Email:** SMTP (Gmail)

## Licencia

© 2026 Cámara de Comercio, Industrias y Servicios de Anaco-Anzoátegui
