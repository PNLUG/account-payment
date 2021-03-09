# Copyright 2021 Sergio Zanchetta (Associazione PNLUG - Gruppo Odoo)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Portal Receipt Payment",
    "version": "14.0.1.0.0",
    "category": "Accounting & Finance",
    "summary": "Pay your sale receipts in the customer portal",
    "author": "Pordenone Linux User Group (PNLUG), Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/account-payment",
    "license": "AGPL-3",
    "depends": ["account_payment", "account_portal_receipt"],
    "data": [
        "views/account_portal_templates.xml",
    ],
    "installable": True,
}
