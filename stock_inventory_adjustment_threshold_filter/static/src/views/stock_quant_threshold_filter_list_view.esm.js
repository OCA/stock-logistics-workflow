/** @odoo-module */

import {InventoryReportListView} from "@stock/views/list/inventory_report_list_view";
import {registry} from "@web/core/registry";
import {StockQuantThresholdFilterSearchModel} from "../search/stock_quant_threshold_filter_search_model.esm";
import {StockQuantThresholdFilterSearchPanel} from "../search/stock_quant_threshold_filter_search_panel.esm";

export const StockQuantThresholdFilterListView = {
    ...InventoryReportListView,
    SearchModel: StockQuantThresholdFilterSearchModel,
    SearchPanel: StockQuantThresholdFilterSearchPanel,
};

registry
    .category("views")
    .add("stock_quant_threshold_filter_list", StockQuantThresholdFilterListView);
