# Copyright 2021 Sergio Zanchetta (Associazione PNLUG - Gruppo Odoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# from odoo.exceptions import AccessError, MissingError, UserError
from odoo.http import request

from odoo.addons.account_portal_receipt.controllers.portal import PortalAccount


class PortalAccount(PortalAccount):
    def _receipt_get_page_view_values(self, receipt, access_token, **kwargs):
        values = super(PortalAccount, self)._receipt_get_page_view_values(
            receipt, access_token, **kwargs
        )
        payment_inputs = request.env["payment.acquirer"]._get_available_payment_input(
            partner=receipt.partner_id, company=receipt.company_id
        )
        # if not connected (using public user), the method _get_available_payment_input
        # will return public user tokens
        is_public_user = request.env.user._is_public()
        if is_public_user:
            # we should not display payment tokens owned by the public user
            payment_inputs.pop("pms", None)
            token_count = (
                request.env["payment.token"]
                .sudo()
                .search_count(
                    [
                        ("acquirer_id.company_id", "=", receipt.company_id.id),
                        ("partner_id", "=", receipt.partner_id.id),
                    ]
                )
            )
            values["existing_token"] = token_count > 0
        values.update(payment_inputs)
        # if the current user is connected we set partner_id to his partner otherwise
        # we set it as the receipt partner
        # we do this to force the creation of payment tokens to the correct partner and
        # avoid token linked to the public user
        values["partner_id"] = (
            receipt.partner_id if is_public_user else request.env.user.partner_id,
        )
        return values
