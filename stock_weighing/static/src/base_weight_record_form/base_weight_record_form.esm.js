/** @odoo-module **/
/* Copyright 2024 Tecnativa - David Vidal
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import ControlPanel from "web.ControlPanel";
import FormView from "web.FormView";
import viewRegistry from "web.view_registry";

export class WeightRecordingFormControlPanel extends ControlPanel {}
WeightRecordingFormControlPanel.template = "WeightRecording.DetailControlPanel";

export const WeightRecordingFormView = FormView.extend({
    // We just want to avoid useless space for this form
    config: _.extend({}, FormView.prototype.config, {
        ControlPanel: WeightRecordingFormControlPanel,
    }),
});

viewRegistry.add("base_weight_record_form", WeightRecordingFormView);
