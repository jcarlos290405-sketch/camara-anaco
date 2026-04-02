from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import uuid

db = SQLAlchemy()


class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    nombre = db.Column(db.String(100))
    rol = db.Column(db.String(20), default='admin')
    activo = db.Column(db.Boolean, default=True)
    ultimo_acceso = db.Column(db.DateTime)

    def __repr__(self):
        return f'<Usuario {self.username}>'


class Solicitud(db.Model):
    __tablename__ = 'solicitudes'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    numero = db.Column(db.Integer, autoincrement=True)

    # Datos de la empresa
    nombre_empresa = db.Column(db.String(200), nullable=False)
    rif = db.Column(db.String(20), nullable=False)
    nit = db.Column(db.String(20))
    sector = db.Column(db.String(100))
    sub_sector = db.Column(db.String(100))
    direccion = db.Column(db.Text)
    ciudad = db.Column(db.String(100))
    estado_geo = db.Column(db.String(100))
    codigo_postal = db.Column(db.String(20))
    pagina_web = db.Column(db.String(200))
    ano_fundacion = db.Column(db.Integer)
    numero_empleados = db.Column(db.Integer)
    descripcion = db.Column(db.Text)

    # Datos de contacto
    nombre_contacto = db.Column(db.String(200), nullable=False)
    cargo = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    telefono_movil = db.Column(db.String(20))
    correo = db.Column(db.String(200), nullable=False)

    # Información adicional
    razones_afiliacion = db.Column(db.Text)
    expectativas = db.Column(db.Text)
    comentarios = db.Column(db.Text)

    # Metadatos
    estado = db.Column(db.String(50), default='pendiente')  # pendiente, aprobada, rechazada, en_revision
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))

    # Relación con junta directiva y documentos
    junta_directiva = db.relationship('MiembroJunta', backref='solicitud', cascade='all, delete-orphan', lazy=True)
    documentos = db.relationship('Documento', backref='solicitud', cascade='all, delete-orphan', lazy=True)
    historial = db.relationship('HistorialEstado', backref='solicitud', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<Solicitud {self.numero} - {self.nombre_empresa}>'

    @property
    def codigo_formateado(self):
        if self.numero is None:
            return f"CC-{self.id[:8].upper()}"
        return f"CC-{self.numero:04d}"


class MiembroJunta(db.Model):
    __tablename__ = 'miembros_junta'
    id = db.Column(db.Integer, primary_key=True)
    solicitud_id = db.Column(db.String(36), db.ForeignKey('solicitudes.id'), nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    cargo = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    correo = db.Column(db.String(200))
    orden = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<MiembroJunta {self.nombre}>'


class Documento(db.Model):
    __tablename__ = 'documentos'
    id = db.Column(db.Integer, primary_key=True)
    solicitud_id = db.Column(db.String(36), db.ForeignKey('solicitudes.id'), nullable=False)
    nombre_original = db.Column(db.String(255), nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(50))  # rif, licencia, certificado, otro
    tamano = db.Column(db.Integer)
    extension = db.Column(db.String(10))
    fecha_subida = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Documento {self.nombre_original}>'

    @property
    def es_imagen(self):
        return self.extension in ['jpg', 'jpeg', 'png', 'gif']

    @property
    def es_pdf(self):
        return self.extension == 'pdf'


class HistorialEstado(db.Model):
    __tablename__ = 'historial_estado'
    id = db.Column(db.Integer, primary_key=True)
    solicitud_id = db.Column(db.String(36), db.ForeignKey('solicitudes.id'), nullable=False)
    estado_anterior = db.Column(db.String(50))
    estado_nuevo = db.Column(db.String(50), nullable=False)
    comentario = db.Column(db.Text)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    fecha_cambio = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<HistorialEstado {self.solicitud_id}: {self.estado_anterior} -> {self.estado_nuevo}>'


class Afiliado(db.Model):
    __tablename__ = 'afiliados'
    id = db.Column(db.Integer, primary_key=True)
    empresa = db.Column(db.String(200), nullable=False)
    rif = db.Column(db.String(20), nullable=False)
    sector = db.Column(db.String(100))
    contacto_principal = db.Column(db.String(200))
    telefono = db.Column(db.String(20))
    correo = db.Column(db.String(200))
    direccion = db.Column(db.Text)
    fecha_afiliacion = db.Column(db.DateTime, default=datetime.utcnow)
    estado = db.Column(db.String(20), default='activo')
    observaciones = db.Column(db.Text)
    logo_filename = db.Column(db.String(255))

    def __repr__(self):
        return f'<Afiliado {self.empresa}>'


class LinkCompartido(db.Model):
    __tablename__ = 'links_compartidos'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True, nullable=False)
    nombre = db.Column(db.String(200))
    descripcion = db.Column(db.Text)
    url_destino = db.Column(db.String(500))
    es_formulario = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_expiracion = db.Column(db.DateTime)
    clicks = db.Column(db.Integer, default=0)
    activo = db.Column(db.Boolean, default=True)
    clicks_detalalle = db.relationship('ClickLink', backref='link', cascade='all, delete-orphan', lazy=True)

    def __repr__(self):
        return f'<LinkCompartido {self.codigo}>'

    @property
    def qr_code_path(self):
        return f"qrcodes/{self.codigo}.png"


class ClickLink(db.Model):
    __tablename__ = 'clicks_link'
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, db.ForeignKey('links_compartidos.id'), nullable=False)
    fecha_click = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(500))

    def __repr__(self):
        return f'<ClickLink {self.link_id} at {self.fecha_click}>'
