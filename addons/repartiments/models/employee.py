from odoo import models, fields

class Employee(models.Model):
    _name = "repartiments.employee"
    _description = "Empleat"

    name = fields.Char(string="Nom", required=True)
    surname = fields.Char(string="Cognoms")
    dni = fields.Char(string="DNI", required=True)
    phone = fields.Char(string="Telèfon")
    photo = fields.Binary(string="Foto")

    carnet_moto = fields.Boolean(string="Carnet Moto")
    carnet_furgo = fields.Boolean(string="Carnet Furgoneta")

    delivery_ids = fields.One2many(
        "repartiments.delivery",
        "employee_id",
        string="Repartiments"
    )