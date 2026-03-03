from odoo import models, fields

class Vehicle(models.Model):
    _name = "repartiments.vehicle"
    _description = "Vehicle"

    name = fields.Char(string="Nom", required=True)

    type = fields.Selection([
        ("bicicleta", "Bicicleta"),
        ("moto", "Moto"),
        ("furgoneta", "Furgoneta")
    ], required=True)

    plate = fields.Char(string="Matrícula")
    photo = fields.Binary(string="Foto")
    description = fields.Text(string="Descripció")

    delivery_ids = fields.One2many(
        "repartiments.delivery",
        "vehicle_id",
        string="Repartiments"
    )