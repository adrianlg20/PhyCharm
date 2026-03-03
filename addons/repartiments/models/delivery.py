from odoo import models, fields, api
from odoo.exceptions import ValidationError

class Delivery(models.Model):
    _name = "repartiments.delivery"
    _description = "Repartiment"
    _order = "reception_date desc, urgency desc"

    code = fields.Char(string="Codi", readonly=True, default="New")

    reception_date = fields.Datetime(default=fields.Datetime.now)
    start_date = fields.Datetime()
    end_date = fields.Datetime()

    employee_id = fields.Many2one("repartiments.employee", required=True)
    vehicle_id = fields.Many2one("repartiments.vehicle", required=True)

    client_sender_id = fields.Many2one("repartiments.client")
    client_receiver_id = fields.Many2one("repartiments.client")

    km = fields.Float()
    weight = fields.Float()
    volume = fields.Float()

    urgency = fields.Selection([
        ("organos", "Òrgans Humans"),
        ("refrigerat", "Aliments Refrigerats"),
        ("aliments", "Aliments"),
        ("alta", "Alta Prioritat"),
        ("baixa", "Baixa Prioritat"),
    ])

    state = fields.Selection([
        ("no_eixit", "No ha eixit"),
        ("cami", "De camí"),
        ("entregada", "Entregada"),
    ], default="no_eixit")

    total_weight_volume = fields.Float(
        compute="_compute_total"
    )

    @api.depends("weight", "volume")
    def _compute_total(self):
        for rec in self:
            rec.total_weight_volume = rec.weight + rec.volume

    @api.constrains("km", "vehicle_id")
    def _check_km_vehicle(self):
        for rec in self:
            if rec.vehicle_id.type == "bicicleta" and rec.km > 10:
                raise ValidationError("Más de 10km no se puede hacer en bicicleta")
            if rec.vehicle_id.type == "furgoneta" and rec.km < 1:
                raise ValidationError("Menos de 1km no se puede hacer en furgoneta")

    @api.constrains("employee_id", "vehicle_id", "state")
    def _check_busy(self):
        for rec in self:
            busy = self.search([
                ("id", "!=", rec.id),
                ("state", "=", "cami"),
                "|",
                ("employee_id", "=", rec.employee_id.id),
                ("vehicle_id", "=", rec.vehicle_id.id),
            ])
            if busy:
                raise ValidationError("Empleado o vehículo ya están en viaje")

    @api.constrains("employee_id", "vehicle_id")
    def _check_license(self):
        for rec in self:
            if rec.vehicle_id.type == "moto" and not rec.employee_id.carnet_moto:
                raise ValidationError("El empleado no tiene carnet de moto")
            if rec.vehicle_id.type == "furgoneta" and not rec.employee_id.carnet_furgo:
                raise ValidationError("El empleado no tiene carnet de furgoneta")

    @api.model
    def create(self, vals):
        if vals.get("code", "New") == "New":
            vals["code"] = self.env["ir.sequence"].next_by_code("repartiments.delivery") or "New"
        return super().create(vals)