from odoo import SUPERUSER_ID
from odoo.api import Environment

def post_init_hook(cr):
    # Use the cursor directly to create the Environment
    env = Environment(cr, SUPERUSER_ID, {})
    env["account.asset"]._install_fixed_asset_ext()

import logging
_logger = logging.getLogger(__name__)

def post_init_hook(cr):
    _logger.debug("Cursor type: %s", type(cr))
    env = Environment(cr, SUPERUSER_ID, {})
    env["account.asset"]._install_fixed_asset_ext()