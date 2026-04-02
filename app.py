import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
from functools import wraps
import qrcode
from io import BytesIO
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

from config import Config
from models import db, Usuario, Solicitud, MiembroJunta, Documento, HistorialEstado, Afiliado, LinkCompartido, ClickLink

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, inicie sesión para acceder al sistema.'

@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# ===================== UTILITY FUNCTIONS =====================

def enviar_correo_solicitud(solicitud, documentos=None):
    """Envía notificación por correo cuando se recibe una nueva solicitud"""
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = f'Nueva Solicitud de Afiliación: {solicitud.nombre_empresa}'
        msg['From'] = app.config['SMTP_FROM_EMAIL']
        msg['To'] = app.config['SMTP_TO_EMAIL']

        # HTML body
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background-color: #f9fafb; margin: 0; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
                .header {{ background: linear-gradient(135deg, #1E3A5F 0%, #0A4B6E 100%); color: white; padding: 30px; text-align: center; }}
                .header h1 {{ margin: 0; font-size: 24px; }}
                .header h2 {{ margin: 10px 0 0; font-size: 16px; font-weight: normal; opacity: 0.9; }}
                .content {{ padding: 30px; }}
                .info-section {{ margin-bottom: 25px; }}
                .info-section h3 {{ color: #1E3A5F; border-bottom: 2px solid #D4AF37; padding-bottom: 8px; margin-bottom: 15px; font-size: 16px; }}
                .info-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }}
                .info-item {{ background: #f3f4f6; padding: 12px; border-radius: 8px; }}
                .info-item label {{ display: block; color: #6b7280; font-size: 12px; margin-bottom: 4px; }}
                .info-item value {{ color: #1f2937; font-weight: 600; }}
                .estado {{ display: inline-block; padding: 6px 16px; border-radius: 20px; font-weight: 600; font-size: 14px; }}
                .estado-pendiente {{ background: #fef3c7; color: #d97706; }}
                .miembros {{ margin-top: 15px; }}
                .miembro {{ background: #f9fafb; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-left: 4px solid #D4AF37; }}
                .footer {{ background: #f3f4f6; padding: 20px; text-align: center; font-size: 12px; color: #6b7280; }}
                .btn {{ display: inline-block; background: #1E3A5F; color: white; padding: 12px 30px; border-radius: 8px; text-decoration: none; font-weight: 600; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Cámara de Comercio, Industrias y Servicios</h1>
                    <h2>de Anaco-Anzoátegui</h2>
                </div>
                <div class="content">
                    <div style="text-align: center; margin-bottom: 30px;">
                        <span class="estado estado-pendiente">Nueva Solicitud Recibida</span>
                        <h2 style="color: #1f2937; margin: 15px 0 5px;">{solicitud.nombre_empresa}</h2>
                        <p style="color: #6b7280; margin: 0;">Código: <strong>{solicitud.codigo_formateado}</strong></p>
                    </div>

                    <div class="info-section">
                        <h3>Datos de la Empresa</h3>
                        <div class="info-grid">
                            <div class="info-item">
                                <label>RIF</label>
                                <value>{solicitud.rif}</value>
                            </div>
                            <div class="info-item">
                                <label>NIT</label>
                                <value>{solicitud.nit or 'No especificado'}</value>
                            </div>
                            <div class="info-item">
                                <label>Sector</label>
                                <value>{solicitud.sector or 'No especificado'}</value>
                            </div>
                            <div class="info-item">
                                <label>Ciudad</label>
                                <value>{solicitud.ciudad or 'No especificada'}</value>
                            </div>
                            <div class="info-item">
                                <label>Año de Fundación</label>
                                <value>{solicitud.ano_fundacion or 'No especificado'}</value>
                            </div>
                            <div class="info-item">
                                <label>N° de Empleados</label>
                                <value>{solicitud.numero_empleados or 'No especificado'}</value>
                            </div>
                        </div>
                        <div style="margin-top: 12px;">
                            <div class="info-item">
                                <label>Dirección</label>
                                <value>{solicitud.direccion or 'No especificada'}</value>
                            </div>
                        </div>
                    </div>

                    <div class="info-section">
                        <h3>Datos de Contacto</h3>
                        <div class="info-grid">
                            <div class="info-item">
                                <label>Nombre</label>
                                <value>{solicitud.nombre_contacto}</value>
                            </div>
                            <div class="info-item">
                                <label>Cargo</label>
                                <value>{solicitud.cargo or 'No especificado'}</value>
                            </div>
                            <div class="info-item">
                                <label>Correo Electrónico</label>
                                <value>{solicitud.correo}</value>
                            </div>
                            <div class="info-item">
                                <label>Teléfono</label>
                                <value>{solicitud.telefono or solicitud.telefono_movil or 'No especificado'}</value>
                            </div>
                        </div>
                    </div>
        """

        # Add board members if any
        if solicitud.junta_directiva:
            html_content += """
                    <div class="info-section">
                        <h3>Junta Directiva</h3>
                        <div class="miembros">
            """
            for miembro in solicitud.junta_directiva:
                html_content += f"""
                            <div class="miembro">
                                <strong>{miembro.nombre}</strong><br>
                                <small>{miembro.cargo or 'Miembro'}</small>
                            </div>
                """
            html_content += "</div></div>"

        # Add documents if any
        if solicitud.documentos:
            html_content += """
                    <div class="info-section">
                        <h3>Documentos Adjuntos</h3>
                        <p>Se han adjuntado los siguientes documentos a la solicitud:</p>
            """
            for doc in solicitud.documentos:
                html_content += f"<li>{doc.nombre_original}</li>"
            html_content += "</div>"

        # Additional info and footer
        html_content += f"""
                    <div class="info-section">
                        <h3>Información Adicional</h3>
                        <div class="info-item">
                            <label>Razones de Afiliación</label>
                            <value>{solicitud.razones_afiliacion or 'No especificadas'}</value>
                        </div>
                    </div>

                    <div style="text-align: center; margin-top: 30px;">
                        <p style="color: #6b7280; font-size: 13px;">
                            Fecha de recepción: {solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M')}
                        </p>
                        <a href="{url_for('detalle_solicitud', solicitud_id=solicitud.id, _external=True)}" class="btn">
                            Ver Solicitud en el Sistema
                        </a>
                    </div>
                </div>
                <div class="footer">
                    <p>Este correo fue generado automáticamente por el Sistema de Gestión de la<br>
                    Cámara de Comercio, Industrias y Servicios de Anaco-Anzoátegui</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_content = f"""
        Nueva Solicitud de Afiliación

        Empresa: {solicitud.nombre_empresa}
        RIF: {solicitud.rif}
        Contacto: {solicitud.nombre_contacto}
        Correo: {solicitud.correo}

        Fecha: {solicitud.fecha_creacion.strftime('%d/%m/%Y %H:%M')}
        """

        msg.attach(MIMEText(text_content, 'plain'))
        msg.attach(MIMEText(html_content, 'html'))

        # Attach documents if any
        if documentos:
            for doc in documentos:
                doc_path = os.path.join(app.config['UPLOAD_FOLDER'], doc.nombre_archivo)
                if os.path.exists(doc_path):
                    with open(doc_path, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename= {doc.nombre_original}')
                    msg.attach(part)

        # Send email
        try:
            with smtplib.SMTP(app.config['SMTP_SERVER'], app.config['SMTP_PORT']) as server:
                server.starttls()
                server.login(app.config['SMTP_USER'], app.config['SMTP_PASSWORD'])
                server.send_message(msg)
            return True
        except Exception as e:
            print(f"Error enviando correo: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    except Exception as e:
        print(f"Error general en enviar_correo_solicitud: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def generate_qr_code(data, filename):
    """Genera código QR y lo guarda"""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    qr_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'qrcodes')
    os.makedirs(qr_folder, exist_ok=True)

    img_path = os.path.join(qr_folder, filename)
    img.save(img_path)
    return img_path


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


# ===================== PUBLIC ROUTES =====================

@app.route('/')
def index():
    return render_template('publico/index.html')


@app.route('/solicitud', methods=['GET', 'POST'])
def solicitud_form():
    if request.method == 'POST':
        # Process form data
        solicitud = Solicitud(
            nombre_empresa=request.form.get('nombre_empresa'),
            rif=request.form.get('rif'),
            nit=request.form.get('nit'),
            sector=request.form.get('sector'),
            sub_sector=request.form.get('sub_sector'),
            direccion=request.form.get('direccion'),
            ciudad=request.form.get('ciudad'),
            estado_geo=request.form.get('estado_geo'),
            codigo_postal=request.form.get('codigo_postal'),
            pagina_web=request.form.get('pagina_web'),
            ano_fundacion=request.form.get('ano_fundacion') if request.form.get('ano_fundacion') else None,
            numero_empleados=request.form.get('numero_empleados') if request.form.get('numero_empleados') else None,
            descripcion=request.form.get('descripcion'),
            nombre_contacto=request.form.get('nombre_contacto'),
            cargo=request.form.get('cargo'),
            telefono=request.form.get('telefono'),
            telefono_movil=request.form.get('telefono_movil'),
            correo=request.form.get('correo'),
            razones_afiliacion=request.form.get('razones_afiliacion'),
            expectativas=request.form.get('expectativas'),
            comentarios=request.form.get('comentarios'),
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(solicitud)
        db.session.flush()  # Get the ID

        # Process board members
        miembros_nombres = request.form.getlist('miembro_nombre')
        miembros_cargos = request.form.getlist('miembro_cargo')
        miembros_telefonos = request.form.getlist('miembro_telefono')
        miembros_correos = request.form.getlist('miembro_correo')

        for i, nombre in enumerate(miembros_nombres):
            if nombre:
                miembro = MiembroJunta(
                    solicitud_id=solicitud.id,
                    nombre=nombre,
                    cargo=miembros_cargos[i] if i < len(miembros_cargos) else None,
                    telefono=miembros_telefonos[i] if i < len(miembros_telefonos) else None,
                    correo=miembros_correos[i] if i < len(miembros_correos) else None,
                    orden=i
                )
                db.session.add(miembro)

        # Process uploaded documents
        files = request.files.getlist('documentos')
        for file in files:
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{solicitud.id}_{file.filename}")
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                file.save(file_path)

                doc = Documento(
                    solicitud_id=solicitud.id,
                    nombre_original=file.filename,
                    nombre_archivo=filename,
                    tipo='documento',
                    tamano=os.path.getsize(file_path),
                    extension=filename.rsplit('.', 1)[1].lower()
                )
                db.session.add(doc)

        db.session.commit()

        # Send email notification
        enviar_correo_solicitud(solicitud, solicitud.documentos)

        return redirect(url_for('confirmacion', solicitud_id=solicitud.id))

    return render_template('publico/solicitud_form.html')


@app.route('/confirmacion/<solicitud_id>')
def confirmacion(solicitud_id):
    solicitud = Solicitud.query.get(solicitud_id)
    if not solicitud:
        return redirect(url_for('index'))
    return render_template('publico/confirmacion.html', solicitud=solicitud)


@app.route('/links/<codigo>')
def acceder_link(codigo):
    link = LinkCompartido.query.filter_by(codigo=codigo, activo=True).first()
    if not link:
        return render_template('publico/link_invalido.html'), 404

    # Register click
    click = ClickLink(
        link_id=link.id,
        ip_address=request.remote_addr,
        user_agent=request.headers.get('User-Agent')
    )
    db.session.add(click)
    link.clicks += 1
    db.session.commit()

    if link.es_formulario:
        return redirect(url_for('solicitud_form', ref=link.codigo))
    else:
        return redirect(link.url_destino)


# ===================== AUTH ROUTES =====================

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = Usuario.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            user.ultimo_acceso = datetime.utcnow()
            db.session.commit()

            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard'))

        flash('Credenciales inválidas. Por favor, intente nuevamente.', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


# ===================== DASHBOARD ROUTES =====================

@app.route('/admin')
@login_required
def dashboard():
    # KPIs
    total_solicitudes = Solicitud.query.count()
    solicitudes_pendientes = Solicitud.query.filter_by(estado='pendiente').count()
    solicitudes_aprobadas = Solicitud.query.filter_by(estado='aprobada').count()
    total_afiliados = Afiliado.query.count()

    # Solicitudes por mes (últimos 6 meses)
    from sqlalchemy import func
    from datetime import datetime, timedelta

    meses_labels = []
    meses_data = []

    for i in range(5, -1, -1):
        fecha = datetime.now() - timedelta(days=i*30)
        label = fecha.strftime('%b %Y')
        meses_labels.append(label)

        count = Solicitud.query.filter(
            func.strftime('%Y-%m', Solicitud.fecha_creacion) == fecha.strftime('%Y-%m')
        ).count()
        meses_data.append(count)

    # Últimas solicitudes
    ultimas_solicitudes = Solicitud.query.order_by(Solicitud.fecha_creacion.desc()).limit(5).all()

    # Distribución por sector
    sectores = db.session.query(
        Solicitud.sector,
        func.count(Solicitud.id)
    ).group_by(Solicitud.sector).limit(5).all()

    sectores_labels = [s[0] or 'Sin especificar' for s in sectores]
    sectores_data = [s[1] for s in sectores]

    return render_template('dashboard.html',
        total_solicitudes=total_solicitudes,
        solicitudes_pendientes=solicitudes_pendientes,
        solicitudes_aprobadas=solicitudes_aprobadas,
        total_afiliados=total_afiliados,
        meses_labels=meses_labels,
        meses_data=meses_data,
        ultimas_solicitudes=ultimas_solicitudes,
        sectores_labels=sectores_labels,
        sectores_data=sectores_data
    )


# ===================== SOLICITUDES ROUTES =====================

@app.route('/admin/solicitudes')
@login_required
def listar_solicitudes():
    page = request.args.get('page', 1, type=int)
    per_page = 12

    query = Solicitud.query

    # Filters
    estado_filter = request.args.get('estado')
    if estado_filter:
        query = query.filter_by(estado=estado_filter)

    sector_filter = request.args.get('sector')
    if sector_filter:
        query = query.filter_by(sector=sector_filter)

    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    if fecha_inicio:
        query = query.filter(Solicitud.fecha_creacion >= datetime.strptime(fecha_inicio, '%Y-%m-%d'))
    if fecha_fin:
        query = query.filter(Solicitud.fecha_creacion <= datetime.strptime(fecha_fin, '%Y-%m-%d'))

    search = request.args.get('buscar')
    if search:
        query = query.filter(
            (Solicitud.nombre_empresa.ilike(f'%{search}%')) |
            (Solicitud.rif.ilike(f'%{search}%')) |
            (Solicitud.nombre_contacto.ilike(f'%{search}%'))
        )

    query = query.order_by(Solicitud.fecha_creacion.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('solicitudes/listar.html',
        pagination=pagination,
        filters={
            'estado': estado_filter,
            'sector': sector_filter,
            'fecha_inicio': fecha_inicio,
            'fecha_fin': fecha_fin,
            'buscar': search
        }
    )


@app.route('/admin/solicitudes/<solicitud_id>')
@login_required
def detalle_solicitud(solicitud_id):
    solicitud = Solicitud.query.get_or_404(solicitud_id)
    return render_template('solicitudes/detalle.html', solicitud=solicitud)


@app.route('/admin/solicitudes/<solicitud_id>/actualizar-estado', methods=['POST'])
@login_required
def actualizar_estado_solicitud(solicitud_id):
    solicitud = Solicitud.query.get_or_404(solicitud_id)
    nuevo_estado = request.form.get('estado')
    comentario = request.form.get('comentario', '')

    if nuevo_estado:
        # Record history
        historial = HistorialEstado(
            solicitud_id=solicitud.id,
            estado_anterior=solicitud.estado,
            estado_nuevo=nuevo_estado,
            comentario=comentario,
            usuario_id=current_user.id
        )
        db.session.add(historial)

        solicitud.estado = nuevo_estado
        db.session.commit()

        flash(f'Estado actualizado a "{nuevo_estado}" exitosamente.', 'success')

    return redirect(url_for('detalle_solicitud', solicitud_id=solicitud_id))


@app.route('/admin/solicitudes/<solicitud_id>/eliminar', methods=['POST'])
@login_required
def eliminar_solicitud(solicitud_id):
    solicitud = Solicitud.query.get_or_404(solicitud_id)

    # Delete associated files
    for doc in solicitud.documentos:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], doc.nombre_archivo)
        if os.path.exists(file_path):
            os.remove(file_path)

    db.session.delete(solicitud)
    db.session.commit()

    flash('Solicitud eliminada exitosamente.', 'success')
    return redirect(url_for('listar_solicitudes'))


@app.route('/admin/solicitudes/exportar')
@login_required
def exportar_solicitudes():
    from flask import Response
    import csv
    from io import StringIO

    solicitudes = Solicitud.query.order_by(Solicitud.fecha_creacion.desc()).all()

    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        'Código', 'Empresa', 'RIF', 'Contacto', 'Correo', 'Sector',
        'Estado', 'Fecha Creación'
    ])

    # Data
    for s in solicitudes:
        writer.writerow([
            s.codigo_formateado,
            s.nombre_empresa,
            s.rif,
            s.nombre_contacto,
            s.correo,
            s.sector or '',
            s.estado,
            s.fecha_creacion.strftime('%d/%m/%Y')
        ])

    output.seek(0)
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=solicitudes.csv'}
    )


# ===================== AFILIADOS ROUTES =====================

@app.route('/admin/afiliados')
@login_required
def listar_afiliados():
    page = request.args.get('page', 1, type=int)
    per_page = 12

    query = Afiliado.query

    search = request.args.get('buscar')
    if search:
        query = query.filter(
            (Afiliado.empresa.ilike(f'%{search}%')) |
            (Afiliado.rif.ilike(f'%{search}%'))
        )

    sector_filter = request.args.get('sector')
    if sector_filter:
        query = query.filter_by(sector=sector_filter)

    query = query.order_by(Afiliado.fecha_afiliacion.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('afiliados/listar.html', pagination=pagination)


@app.route('/admin/afiliados/nuevo', methods=['GET', 'POST'])
@login_required
def crear_afiliado():
    if request.method == 'POST':
        afiliado = Afiliado(
            empresa=request.form.get('empresa'),
            rif=request.form.get('rif'),
            sector=request.form.get('sector'),
            contacto_principal=request.form.get('contacto_principal'),
            telefono=request.form.get('telefono'),
            correo=request.form.get('correo'),
            direccion=request.form.get('direccion'),
            observaciones=request.form.get('observaciones')
        )
        db.session.add(afiliado)
        db.session.commit()

        flash('Afiliado creado exitosamente.', 'success')
        return redirect(url_for('listar_afiliados'))

    return render_template('afiliados/formulario.html', afiliado=None)


@app.route('/admin/afiliados/<int:afiliado_id>/editar', methods=['GET', 'POST'])
@login_required
def editar_afiliado(afiliado_id):
    afiliado = Afiliado.query.get_or_404(afiliado_id)

    if request.method == 'POST':
        afiliado.empresa = request.form.get('empresa')
        afiliado.rif = request.form.get('rif')
        afiliado.sector = request.form.get('sector')
        afiliado.contacto_principal = request.form.get('contacto_principal')
        afiliado.telefono = request.form.get('telefono')
        afiliado.correo = request.form.get('correo')
        afiliado.direccion = request.form.get('direccion')
        afiliado.observaciones = request.form.get('observaciones')

        db.session.commit()
        flash('Afiliado actualizado exitosamente.', 'success')
        return redirect(url_for('listar_afiliados'))

    return render_template('afiliados/formulario.html', afiliado=afiliado)


# ===================== LINKS ROUTES =====================

@app.route('/admin/links')
@login_required
def listar_links():
    links = LinkCompartido.query.order_by(LinkCompartido.fecha_creacion.desc()).all()
    return render_template('links/listar.html', links=links)


@app.route('/admin/links/nuevo', methods=['GET', 'POST'])
@login_required
def crear_link():
    if request.method == 'POST':
        codigo = str(uuid.uuid4())[:8]
        link = LinkCompartido(
            codigo=codigo,
            nombre=request.form.get('nombre'),
            descripcion=request.form.get('descripcion'),
            url_destino=request.form.get('url_destino'),
            es_formulario=request.form.get('es_formulario') == 'on'
        )
        db.session.add(link)
        db.session.commit()

        # Generate QR
        url_completa = url_for('acceder_link', codigo=codigo, _external=True)
        generate_qr_code(url_completa, f"{codigo}.png")

        flash('Link creado exitosamente.', 'success')
        return redirect(url_for('listar_links'))

    return render_template('links/formulario.html', link=None)


@app.route('/admin/links/<int:link_id>/toggle')
@login_required
def toggle_link(link_id):
    link = LinkCompartido.query.get_or_404(link_id)
    link.activo = not link.activo
    db.session.commit()

    estado = 'activado' if link.activo else 'desactivado'
    flash(f'Link {estado} exitosamente.', 'success')
    return redirect(url_for('listar_links'))


# ===================== API ROUTES =====================

@app.route('/api/documentos/<solicitud_id>')
@login_required
def get_documentos(solicitud_id):
    solicitud = Solicitud.query.get_or_404(solicitud_id)
    documentos = [{
        'id': d.id,
        'nombre': d.nombre_original,
        'tipo': d.tipo,
        'extension': d.extension,
        'es_imagen': d.es_imagen,
        'es_pdf': d.es_pdf
    } for d in solicitud.documentos]
    return jsonify(documentos)


@app.route('/api/stats')
@login_required
def get_stats():
    from sqlalchemy import func

    stats = {
        'total_solicitudes': Solicitud.query.count(),
        'pendientes': Solicitud.query.filter_by(estado='pendiente').count(),
        'aprobadas': Solicitud.query.filter_by(estado='aprobada').count(),
        'rechazadas': Solicitud.query.filter_by(estado='rechazada').count(),
        'afiliados': Afiliado.query.count()
    }
    return jsonify(stats)


# ===================== STATIC FILES =====================

@app.route('/uploads/<path:filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ===================== INITIALIZATION =====================

def init_db():
    """Initialize database and create default admin user"""
    with app.app_context():
        db.create_all()

        # Create default admin if not exists
        admin = Usuario.query.filter_by(username='CamDCDA26').first()
        if not admin:
            admin = Usuario(
                username='CamDCDA26',
                password_hash=generate_password_hash('CAM26COMAN$*'),
                nombre='Administrador',
                rol='admin'
            )
            db.session.add(admin)
            db.session.commit()
            print("Usuario admin creado: CamDCDA26")

        # Ensure upload directories exist
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'qrcodes'), exist_ok=True)


if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
else:
    # For gunicorn/Production: ensure tables exist on startup
    with app.app_context():
        db.create_all()
