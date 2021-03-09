# Copyright 2021 Sergio Zanchetta (Associazione PNLUG - Gruppo Odoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import _, models

_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    def render_receipt_button(self, receipt, submit_txt=None, render_values=None):
        values = {
            "partner_id": receipt.partner_id.id,
        }
        if render_values:
            values.update(render_values)
        return (
            self.acquirer_id.with_context(
                submit_class="btn btn-primary", submit_txt=submit_txt or _("Pay Now")
            )
            .sudo()
            .render(
                self.reference,
                receipt.amount_residual,
                receipt.currency_id.id,
                values=values,
            )
        )
