# Copyright 2021 Sergio Zanchetta (Associazione PNLUG - Gruppo Odoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from werkzeug.urls import url_encode

from odoo import _, http
from odoo.http import request, route

from odoo.addons.payment.controllers.portal import PaymentProcessing
from odoo.addons.portal.controllers.portal import _build_url_w_params


class PaymentPortal(http.Controller):
    @route(
        "/receipt/pay/<int:receipt_id>/form_tx",
        type="json",
        auth="public",
        website=True,
    )
    def receipt_pay_form(
        self, acquirer_id, receipt_id, save_token=False, access_token=None, **kwargs
    ):
        """Json method that creates a payment.transaction, used to create a
        transaction when the user clicks on 'pay now' button on the payment
        form.

        :return html: form containing all values related to the acquirer to
                      redirect customers to the acquirer website"""
        receipt_sudo = request.env["account.move"].sudo().browse(receipt_id)
        if not receipt_sudo:
            return False

        try:
            acquirer_id = int(acquirer_id)
        except Exception:
            return False

        if request.env.user._is_public():
            save_token = False  # we avoid to create a token for the public user

        success_url = kwargs.get(
            "success_url",
            "%s?%s"
            % (
                receipt_sudo.access_url,
                url_encode({"access_token": access_token}) if access_token else "",
            ),
        )
        vals = {
            "acquirer_id": acquirer_id,
            "return_url": success_url,
        }

        if save_token:
            vals["type"] = "form_save"

        transaction = receipt_sudo._create_payment_transaction(vals)
        PaymentProcessing.add_payment_transaction(transaction)

        return transaction.render_receipt_button(
            receipt_sudo,
            submit_txt=_("Pay & Confirm"),
            render_values={
                "type": "form_save" if save_token else "form",
                "alias_usage": _(
                    "If we store your payment information on our server, "
                    "subscription payments will be made automatically."
                ),
            },
        )

    @http.route(
        "/receipt/pay/<int:receipt_id>/s2s_token_tx",
        type="http",
        auth="public",
        website=True,
    )
    def receipt_pay_token(self, receipt_id, pm_id=None, **kwargs):
        """ Use a token to perform a s2s transaction """
        error_url = kwargs.get("error_url", "/my")
        access_token = kwargs.get("access_token")
        params = {}
        if access_token:
            params["access_token"] = access_token

        receipt_sudo = request.env["account.move"].sudo().browse(receipt_id).exists()
        if not receipt_sudo:
            params["error"] = "pay_receipt_invalid_doc"
            return request.redirect(_build_url_w_params(error_url, params))

        success_url = kwargs.get(
            "success_url",
            "%s?%s"
            % (
                receipt_sudo.access_url,
                url_encode({"access_token": access_token}) if access_token else "",
            ),
        )
        try:
            token = request.env["payment.token"].sudo().browse(int(pm_id))
        except (ValueError, TypeError):
            token = False
        token_owner = (
            receipt_sudo.partner_id
            if request.env.user._is_public()
            else request.env.user.partner_id
        )
        if not token or token.partner_id != token_owner:
            params["error"] = "pay_receipt_invalid_token"
            return request.redirect(_build_url_w_params(error_url, params))

        vals = {
            "payment_token_id": token.id,
            "type": "server2server",
            "return_url": _build_url_w_params(success_url, params),
        }

        tx = receipt_sudo._create_payment_transaction(vals)
        PaymentProcessing.add_payment_transaction(tx)

        params["success"] = "pay_receipt"
        return request.redirect("/payment/process")
