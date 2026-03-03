from odoo import models, fields

class DeliveryWizard(models.TransientModel):
    _name = "sg.delivery.wizard"
    _description = "Wizard Crear Repartiment"

    employee_id = fields.Many2one("sg.employee", string="Repartidor", required=True)
    vehicle_id = fields.Many2one("sg.vehicle", string="Vehicle", required=True)
    km = fields.Float(string="Kilòmetres")

    def action_create_delivery(self):
        self.env["sg.delivery"].create({
            "employee_id": self.employee_id.id,
            "vehicle_id": self.vehicle_id.id,
            "km": self.km,
        })