from odoo import models, fields

class Client(models.Model):
    _name = "repartiments.client"
    _description = "Client"

    name = fields.Char(required=True)
    surname = fields.Char()
    dni = fields.Char()
    phone = fields.Char()