from odoo import http
from odoo.http import request

class DeliveryController(http.Controller):

    @http.route('/delivery/status/<string:code>', auth='public', type='json')
    def get_delivery_status(self, code):
        delivery = request.env['sg.delivery'].sudo().search([('code', '=', code)], limit=1)

        if delivery:
            return {
                "code": delivery.code,
                "status": delivery.state
            }

        return {"error": "Repartiment no trobat"}