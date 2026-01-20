# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.fields import Date


# Nuevo modelo para clasificar las tareas
class CategoriaTarea(models.Model):
    _name = 'lista_tareas.categoria'
    _description = 'Categoría de Tarea'

    name = fields.Char(string="Nombre de Categoría", required=True)


class ListaTareas(models.Model):
    _name = 'lista_tareas.lista'
    _description = 'Modelo de la lista de tareas'
    _rec_name = "tarea"

    tarea = fields.Char(string="Tarea")
    prioridad = fields.Integer(string="Prioridad")
    urgente = fields.Boolean(string="Urgente", compute="_value_urgente", store=True)
    realizada = fields.Boolean(string="Realizada")
    fecha_asignada = fields.Date(string="Fecha Asignada", default=fields.Date.today)

    # 1. ATRIBUTOS DE FECHA LÍMITE
    fecha_limite = fields.Date(string="Fecha Límite")
    # Campo computado para tareas fuera de plazo
    vencida = fields.Boolean(string="Vencida", compute="_compute_vencida")

    # 2. USUARIO ASIGNADO (Relación Many2one con res.users)
    usuario_asignado = fields.Many2one('res.users', string="Usuario Asignado", default=lambda self: self.env.user)

    # 3. RELACIÓN CON CATEGORÍAS
    categoria_id = fields.Many2one('lista_tareas.categoria', string="Categoría")

    @api.depends('prioridad')
    def _value_urgente(self):
        for record in self:
            record.urgente = record.prioridad > 10

    # Lógica para determinar si la tarea está vencida
    @api.depends('fecha_limite', 'realizada')
    def _compute_vencida(self):
        hoy = Date.today()
        for record in self:
            # Se considera vencida si la fecha límite pasó y no se ha marcado como realizada
            if record.fecha_limite and record.fecha_limite < hoy and not record.realizada:
                record.vencida = True
            else:
                record.vencida = False