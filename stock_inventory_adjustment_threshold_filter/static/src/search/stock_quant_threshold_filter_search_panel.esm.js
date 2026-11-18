/** @odoo-module **/
import {SearchPanel} from "@web/search/search_panel/search_panel";
import {roundFloat} from "./stock_quant_threshold_filter_search_model.esm";
import {useBus} from "@web/core/utils/hooks";

const {useState} = owl;

export class StockQuantThresholdFilterSearchPanel extends SearchPanel {
    setup() {
        super.setup(...arguments);
        this.filters = useState({...this.env.searchModel.thresholdFilterFilters});
        useBus(this.env.searchModel, "update", () => {
            Object.assign(this.filters, this.env.searchModel.thresholdFilterFilters);
        });
    }

    // ---------------------------------------------------------------------
    // Actions / Getters
    // ---------------------------------------------------------------------

    _digitsFor(fieldName) {
        return fieldName.startsWith("cost")
            ? this.filters.costDigits
            : this.filters.qtyDigits;
    }

    _setThreshold(fieldName, ev) {
        const value = roundFloat(
            parseFloat(ev.target.value),
            this._digitsFor(fieldName)
        );
        const boundField =
            fieldName === "costThreshold" ? "costBoundMax" : "qtyDiffBoundMax";
        this.filters[fieldName] = Math.max(
            0,
            Math.min(value, this.filters[boundField])
        );
    }

    _applyThreshold(fieldName, ev) {
        this._setThreshold(fieldName, ev);
        this._applyFilters();
    }

    onInputThreshold(fieldName, ev) {
        this._setThreshold(fieldName, ev);
    }

    onChangeThreshold(fieldName, ev) {
        this._applyThreshold(fieldName, ev);
    }

    onChangeMode(prefix, mode) {
        const modeField = `${prefix}Mode`;
        if (this.filters[modeField] === mode) {
            return;
        }
        const thresholdField = `${prefix}Threshold`;
        const currentThreshold = this.filters[thresholdField];
        const boundField = prefix === "cost" ? "costBoundMax" : "qtyDiffBoundMax";
        this.filters[modeField] = mode;
        // Switching mode without resetting the threshold would silently
        // turn a "no restriction" position into a highly restrictive one
        // (e.g. min=0 becomes max=0).
        // Reset to the neutral position for the new mode instead if the
        // the current threshold is not in the neutral position.
        if (currentThreshold === (mode === "max" ? 0 : this.filters[boundField])) {
            this.filters[thresholdField] =
                mode === "max" ? this.filters[boundField] : 0;
        }
        this._applyFilters();
    }

    onChangeFlag(fieldName, ev) {
        this.filters[fieldName] = ev.target.checked;
        if (fieldName === "zeroAdjustment" && ev.target.checked) {
            this.filters.positiveAdjustment = false;
            this.filters.negativeAdjustment = false;
            this._resetThresholdsToZero();
        } else if (ev.target.checked) {
            this.filters.zeroAdjustment = false;
            this._resetThresholdsToBounds();
        }
        this._applyFilters();
    }

    _resetThresholdsToZero() {
        this.filters.costThreshold = 0;
        this.filters.qtyDiffThreshold = 0;
    }

    _resetThresholdsToBounds() {
        this.filters.costThreshold =
            this.filters.costMode === "max"
                ? this.filters.costBoundMax
                : Math.max(
                      0,
                      Math.min(
                          this.filters.costDefaultThreshold,
                          this.filters.costBoundMax
                      )
                  );
        this.filters.qtyDiffThreshold =
            this.filters.qtyDiffMode === "max"
                ? this.filters.qtyDiffBoundMax
                : Math.max(
                      0,
                      Math.min(
                          this.filters.qtyDiffDefaultThreshold,
                          this.filters.qtyDiffBoundMax
                      )
                  );
    }

    _applyFilters() {
        this.env.searchModel.applyThresholdFilterFilters({...this.filters});
    }

    _sliderStyle(value, minValue, maxValue) {
        const range = maxValue - minValue;
        const percent = range ? ((value - minValue) * 100) / range : 0;
        return `left: ${percent}%;`;
    }

    resetThresholdFilterFilters() {
        this.env.searchModel.resetThresholdFilterFilters();
    }
}

StockQuantThresholdFilterSearchPanel.template =
    "stock_inventory_adjustment_threshold_filter.StockQuantThresholdFilterSearchPanel";
