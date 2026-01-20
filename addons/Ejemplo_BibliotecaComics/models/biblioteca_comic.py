# -*- coding: utf-8 -*-

# Importaciones necesarias
from datetime import timedelta
from odoo import models, fields, api
from odoo.exceptions import ValidationError


# ==========================================================
# MODELO ABSTRACTO - BaseArchive
# ==========================================================
class BaseArchive(models.AbstractModel):
    _name = 'base.archive'
    _description = 'Modelo abstracto de archivo (archivable)'

    activo = fields.Boolean(default=True)

    def archivar(self):
        for record in self:
            record.activo = not record.activo


# ==========================================================
# MODELO PRINCIPAL - BibliotecaComic
# ==========================================================
class BibliotecaComic(models.Model):
    _name = 'biblioteca.comic'
    _description = 'Cómic de la biblioteca'
    _inherit = ['base.archive']
    _order = 'fecha_publicacion desc, nombre'
    _rec_name = 'nombre'

    # --- CAMPOS EXISTENTES ---
    nombre = fields.Char(string='Título', required=True, index=True)
    estado = fields.Selection(
        selection=[('borrador', 'No disponible'), ('disponible', 'Disponible'), ('perdido', 'Perdido')],
        string='Estado', default='borrador'
    )
    descripcion = fields.Html(string='Descripción', sanitize=True, strip_style=False)
    portada = fields.Binary(string='Portada del cómic')
    fecha_publicacion = fields.Date(string='Fecha de publicación')
    precio = fields.Float(string='Precio')
    paginas = fields.Integer(string='Número de páginas', groups='base.group_user', company_dependent=False)
    valoracion_lector = fields.Float(string='Valoración media lectores', digits=(14, 4))

    # --- RELACIONES ---
    autor_ids = fields.Many2many('res.partner', string='Autores')
    editorial_id = fields.Many2one('res.partner', string='Editorial')
    categoria_id = fields.Many2one('biblioteca.comic.categoria', string='Categoría')

    # (NUEVO) Relación con los ejemplares físicos
    exemplar_ids = fields.One2many(
        'biblioteca.comic.exemplar',
        'comic_id',
        string='Ejemplares Físicos'
    )

    # --- CAMPO COMPUTADO ---
    dias_lanzamiento = fields.Integer(
        string='Días desde lanzamiento',
        compute='_compute_dias_lanzamiento',
        inverse='_inverse_dias_lanzamiento',
        search='_search_dias_lanzamiento',
        store=False,
        compute_sudo=True
    )

    # --- REFERENCIA ---
    ref_doc_id = fields.Reference(selection='_referencable_models', string='Referencia a documento')

    @api.model
    def _referencable_models(self):
        models = self.env['ir.model'].search([('field_id.name', '=', 'message_ids')])
        return [(x.model, x.name) for x in models]

    # --- MÉTODOS ---
    @api.depends('fecha_publicacion')
    def _compute_dias_lanzamiento(self):
        hoy = fields.Date.today()
        for comic in self:
            if comic.fecha_publicacion:
                delta = hoy - comic.fecha_publicacion
                comic.dias_lanzamiento = delta.days
            else:
                comic.dias_lanzamiento = 0

    def _inverse_dias_lanzamiento(self):
        hoy = fields.Date.today()
        for comic in self:
            if comic.dias_lanzamiento is not None:
                nueva_fecha = hoy - timedelta(days=comic.dias_lanzamiento)
                comic.fecha_publicacion = nueva_fecha

    def _search_dias_lanzamiento(self, operator, value):
        hoy = fields.Date.today()
        fecha_limite = hoy - timedelta(days=value)
        operator_map = {'>': '<', '>=': '<=', '<': '>', '<=': '>='}
        new_op = operator_map.get(operator, operator)
        return [('fecha_publicacion', new_op, fecha_limite)]

    def name_get(self):
        result = []
        for record in self:
            nombre = "%s (%s)" % (record.nombre, record.fecha_publicacion or 'Sin fecha')
            result.append((record.id, nombre))
        return result

    # --- CONSTRAINTS ---
    _sql_constraints = [
        ('name_uniq', 'UNIQUE (nombre)', 'El título del cómic debe ser único.'),
        ('positive_page', 'CHECK(paginas>0)', 'El cómic debe tener al menos una página.')
    ]

    @api.constrains('fecha_publicacion')
    def _check_release_date(self):
        for record in self:
            if record.fecha_publicacion and record.fecha_publicacion > fields.Date.today():
                raise ValidationError('La fecha de publicación no puede ser en el futuro.')


# ==========================================================
# NUEVO MODELO (a.1) - Socios
# Gestiona la información de las personas que piden préstamos
# ==========================================================
class BibliotecaSocio(models.Model):
    _name = 'biblioteca.socio'
    _description = 'Socio de la Biblioteca'
    _rec_name = 'identificador'  # Se mostrará el ID en las búsquedas

    nombre = fields.Char(string='Nombre', required=True)
    apellido = fields.Char(string='Apellido', required=True)
    identificador = fields.Char(string='Identificador', required=True, copy=False)

    _sql_constraints = [
        ('identificador_uniq', 'UNIQUE (identificador)', 'El ID del socio debe ser único.')
    ]

    def name_get(self):
        """Muestra: [ID] Nombre Apellido"""
        result = []
        for record in self:
            name = "[%s] %s %s" % (record.identificador, record.nombre, record.apellido)
            result.append((record.id, name))
        return result


# ==========================================================
# NUEVO MODELO (a.2) - Ejemplares (Préstamos)
# Gestiona las copias físicas y sus préstamos actuales
# ==========================================================
class BibliotecaComicExemplar(models.Model):
    _name = 'biblioteca.comic.exemplar'
    _description = 'Ejemplar de Cómic para Préstamo'

    # a.2.1 Referencia al cómic (información general)
    comic_id = fields.Many2one(
        'biblioteca.comic',
        string='Cómic',
        required=True,
        ondelete='cascade'
    )

    # a.2.2 Control de préstamo (quién lo tiene)
    socio_id = fields.Many2one(
        'biblioteca.socio',
        string='Prestado a (Socio)',
        help='Socio que tiene actualmente el ejemplar.'
    )

    fecha_prestamo = fields.Date(
        string='Fecha de Préstamo',
        default=fields.Date.today
    )

    fecha_devolucion = fields.Date(
        string='Fecha Prevista Devolución'
    )

    # Estado calculado simple para la vista lista
    estado_prestamo = fields.Selection(
        [('disponible', 'Disponible'), ('prestado', 'Prestado')],
        string='Estado',
        compute='_compute_estado',
        store=True
    )

    @api.depends('socio_id')
    def _compute_estado(self):
        for rec in self:
            rec.estado_prestamo = 'prestado' if rec.socio_id else 'disponible'

    # a.2.2.1 y a.2.2.2 Validaciones de fechas
    @api.constrains('fecha_prestamo', 'fecha_devolucion')
    def _check_fechas_prestamo(self):
        hoy = fields.Date.today()
        for rec in self:
            # Solo validamos si hay un préstamo activo (si hay socio)
            if rec.socio_id:
                # a.2.2.1 La fecha de préstamo no puede ser posterior a hoy
                if rec.fecha_prestamo and rec.fecha_prestamo > hoy:
                    raise ValidationError('La fecha de inicio del préstamo no puede ser futura.')

                # a.2.2.2 La fecha prevista de vuelta no puede ser anterior a hoy
                # (Entendemos que al registrar el préstamo, la devolución es futura)
                if rec.fecha_devolucion and rec.fecha_devolucion < hoy:
                    raise ValidationError('La fecha prevista de devolución no puede ser anterior a hoy.')