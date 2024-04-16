/** @odoo-module **/
/* Copyright 2024 Tecnativa - David Vidal
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */
import KanbanColumn from "web.KanbanColumn";
import KanbanController from "web.KanbanController";
import KanbanRenderer from "web.KanbanRenderer";
import KanbanView from "web.KanbanView";
import viewRegistry from "web.view_registry";

export const WeightRecordingKanbanColumn = KanbanColumn.extend({
    template: "WeightRecordingKanbanView.Group",
    events: _.extend({}, KanbanColumn.prototype.events || {}, {
        "click .toggle_kanban_fold": "_onToggleFold",
    }),
});

export const WeightRecordingKanbanController = KanbanController.extend({
    /**
     * Refresh the view after we change the record value so we can update filters,
     * progressbars, etc.
     * TODO: Depends on https://github.com/odoo/odoo/pull/161042 Otherwise we should
     * rewrite the whole method.
     * @override
     * @returns {Promise}
     */
    _reloadAfterButtonClick() {
        const def = this._super(...arguments);
        return def.then(() => {
            this.reload();
        });
    },
});

export const WeightRecordingKanbanRenderer = KanbanRenderer.extend({
    config: _.extend({}, KanbanRenderer.prototype.config, {
        KanbanColumn: WeightRecordingKanbanColumn,
    }),
});

export const WeightRecordingKanbanView = KanbanView.extend({
    config: _.extend({}, KanbanView.prototype.config, {
        Renderer: WeightRecordingKanbanRenderer,
        Controller: WeightRecordingKanbanController,
    }),
});

viewRegistry.add("base_weight_record_kanban", WeightRecordingKanbanView);
