import {WarningDialog} from "@web/core/errors/error_dialogs";
import {registry} from "@web/core/registry";

registry
    .category("error_dialogs")
    .add(
        "odoo.addons.stock_picking_batch_creation.exceptions.NoSuitableDeviceError",
        WarningDialog
    )
    .add(
        "odoo.addons.stock_picking_batch_creation.exceptions.NoPickingCandidateError",
        WarningDialog
    );
