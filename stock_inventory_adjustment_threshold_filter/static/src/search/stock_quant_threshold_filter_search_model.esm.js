/** @odoo-module **/

import {Domain} from "@web/core/domain";
import {SearchModel} from "@web/search/search_model";

/**
 * Rounds a value to a number of decimal digits, e.g. roundFloat(1.2345, 2)
 * -> 1.23. Same convention as `field.digits` and the core `formatFloat`
 * helper (@web/views/fields/formatters), but we need a Number rounded
 * to a specific number of decimal digits....
 *
 * @param {Number} value
 * @param {Number} digits
 * @returns {Number}
 */
export function roundFloat(value, digits) {
    return Number(value.toFixed(digits));
}

const DEFAULT_CRITERIA = {
    costThreshold: 0,
    // "min": keep quants whose adjustment magnitude is *at least*
    // costThreshold (find everything beyond a threshold). "max": keep
    // quants whose magnitude is *at most* costThreshold (bulk-process
    // everything under a threshold).
    costMode: "min",
    qtyDiffThreshold: 0,
    qtyDiffMode: "min",
    positiveAdjustment: false,
    negativeAdjustment: false,
    zeroAdjustment: false,
};

export class StockQuantThresholdFilterSearchModel extends SearchModel {
    /**
     * @override
     */
    setup() {
        this.thresholdFilterState = {
            costBoundMax: 0,
            qtyDiffBoundMax: 0,
            costDefaultThreshold: 0,
            qtyDiffDefaultThreshold: 0,
            costDigits: 2,
            qtyDigits: 2,
            totalAmount: 0,
            totalCount: 0,
        };
        this._appliedThresholdFilterFilters = {...DEFAULT_CRITERIA};
        this._thresholdFilterDefaults = null;
        this._thresholdFilterBoundsInitialized = false;
        super.setup(...arguments);
    }

    exportState() {
        const state = super.exportState();
        state.appliedThresholdFilterFilters = this._appliedThresholdFilterFilters;
        return state;
    }

    _importState(state) {
        super._importState(...arguments);
        if (state.appliedThresholdFilterFilters) {
            this._appliedThresholdFilterFilters = state.appliedThresholdFilterFilters;
            this._thresholdFilterBoundsInitialized = true;
        }
    }

    /**
     * @override
     */
    async load() {
        await super.load(...arguments);
        await this._loadThresholdFilterState();
    }

    /**
     * @override
     */
    async _notify() {
        if (!this.display) {
            return super._notify();
        }
        await this._loadThresholdFilterState();
        super._notify();
    }

    get thresholdFilterFilters() {
        return {...this._appliedThresholdFilterFilters, ...this.thresholdFilterState};
    }

    get appliedThresholdFilterFilters() {
        return this._appliedThresholdFilterFilters;
    }

    async applyThresholdFilterFilters(criteria) {
        this._appliedThresholdFilterFilters = {...criteria};
        await this._notify();
    }

    async resetThresholdFilterFilters() {
        this._thresholdFilterBoundsInitialized = false;
        await this._notify();
    }

    async _loadThresholdFilterState() {
        const wasInitialized = this._thresholdFilterBoundsInitialized;
        const baseDomain = super._getDomain();
        const signDomain = this._getAdjustmentSignDomain();
        const readGroupDomain = signDomain.length
            ? Domain.and([baseDomain, signDomain]).toList()
            : baseDomain;
        const result = await this.orm.readGroup(
            this.resModel,
            readGroupDomain,
            [
                "cost_min:min(adjustment_cost)",
                "cost_max:max(adjustment_cost)",
                "qty_diff_min:min(inventory_diff_quantity)",
                "qty_diff_max:max(inventory_diff_quantity)",
            ],
            []
        );
        if (!this._thresholdFilterDefaults) {
            this._thresholdFilterDefaults = await this.orm.call(
                "res.company",
                "get_threshold_filter_defaults",
                []
            );
        }
        const defaults = this._thresholdFilterDefaults;
        const group = result[0] || {};
        const costBoundMax = this._getDataBoundMax(
            group.cost_min,
            group.cost_max,
            defaults.cost_digits
        );
        const qtyDiffBoundMax = this._getDataBoundMax(
            group.qty_diff_min,
            group.qty_diff_max,
            defaults.qty_digits
        );
        this.thresholdFilterState.costBoundMax = costBoundMax;
        this.thresholdFilterState.qtyDiffBoundMax = qtyDiffBoundMax;
        this.thresholdFilterState.costDigits = defaults.cost_digits;
        this.thresholdFilterState.qtyDigits = defaults.qty_digits;
        this.thresholdFilterState.costDefaultThreshold = this._getDefaultRangeValue(
            0,
            costBoundMax,
            defaults.cost_min,
            defaults.cost_digits
        );
        this.thresholdFilterState.qtyDiffDefaultThreshold = this._getDefaultRangeValue(
            0,
            qtyDiffBoundMax,
            defaults.qty_diff_min,
            defaults.qty_digits
        );

        if (wasInitialized) {
            const criteria = this._appliedThresholdFilterFilters;
            criteria.costThreshold = Math.max(
                0,
                Math.min(criteria.costThreshold, costBoundMax)
            );
            criteria.qtyDiffThreshold = Math.max(
                0,
                Math.min(criteria.qtyDiffThreshold, qtyDiffBoundMax)
            );
        } else {
            this._appliedThresholdFilterFilters = {
                ...DEFAULT_CRITERIA,
                costThreshold: this.thresholdFilterState.costDefaultThreshold,
                qtyDiffThreshold: this.thresholdFilterState.qtyDiffDefaultThreshold,
            };
            this._thresholdFilterBoundsInitialized = true;
        }

        const totalResult = await this.orm.readGroup(
            this.resModel,
            this._getDomain(),
            ["adjustment_cost:sum"],
            []
        );
        const totalGroup = totalResult[0];
        this.thresholdFilterState.totalCount = totalGroup ? totalGroup.__count : 0;
        this.thresholdFilterState.totalAmount = totalGroup
            ? totalGroup.adjustment_cost
            : 0;
    }

    _getAdjustmentSignDomain() {
        const criteria = this._appliedThresholdFilterFilters;
        if (criteria.zeroAdjustment) {
            return [["adjustment_cost", "=", 0]];
        }
        const includePositive =
            criteria.positiveAdjustment ||
            (!criteria.positiveAdjustment && !criteria.negativeAdjustment);
        const includeNegative =
            criteria.negativeAdjustment ||
            (!criteria.positiveAdjustment && !criteria.negativeAdjustment);

        const buckets = [];
        if (includePositive) {
            buckets.push([["adjustment_cost", ">", 0]]);
        }
        if (includeNegative) {
            buckets.push([["adjustment_cost", "<", 0]]);
        }
        return buckets.length ? Domain.or(buckets).toList() : [];
    }

    _getDataBoundMax(rawMin, rawMax, digits) {
        return roundFloat(
            Math.max(Math.abs(rawMin || 0), Math.abs(rawMax || 0)),
            digits
        );
    }

    _getDefaultRangeValue(minBound, maxBound, defaultValue, digits) {
        const fallback = minBound;
        const candidate = defaultValue ? roundFloat(defaultValue, digits) : fallback;
        return Math.max(minBound, Math.min(candidate, maxBound));
    }

    _getThresholdFilterDomain() {
        const criteria = this._appliedThresholdFilterFilters;
        if (criteria.zeroAdjustment) {
            return [["adjustment_cost", "=", 0]];
        }
        const includePositive =
            criteria.positiveAdjustment ||
            (!criteria.positiveAdjustment && !criteria.negativeAdjustment);
        const includeNegative =
            criteria.negativeAdjustment ||
            (!criteria.positiveAdjustment && !criteria.negativeAdjustment);
        // "min" mode: magnitude >= threshold (positive op ">=", mirrored
        // "<=" on the negative side). "max" mode: magnitude <= threshold
        // (operators flipped).
        const costOp = criteria.costMode === "max" ? "<=" : ">=";
        const costOpNeg = criteria.costMode === "max" ? ">=" : "<=";
        const qtyOp = criteria.qtyDiffMode === "max" ? "<=" : ">=";
        const qtyOpNeg = criteria.qtyDiffMode === "max" ? ">=" : "<=";
        const positiveDomain = [
            ["adjustment_cost", ">", 0],
            ["adjustment_cost", costOp, criteria.costThreshold],
            ["inventory_diff_quantity", ">", 0],
            ["inventory_diff_quantity", qtyOp, criteria.qtyDiffThreshold],
        ];
        const negativeDomain = [
            ["adjustment_cost", "<", 0],
            ["adjustment_cost", costOpNeg, -criteria.costThreshold],
            ["inventory_diff_quantity", "<", 0],
            ["inventory_diff_quantity", qtyOpNeg, -criteria.qtyDiffThreshold],
        ];
        const buckets = [];
        if (includePositive) {
            buckets.push(positiveDomain);
        }
        if (includeNegative) {
            buckets.push(negativeDomain);
        }
        return buckets.length === 1 ? buckets[0] : Domain.or(buckets).toList();
    }

    /**
     * @override
     */
    _getDomain(params = {}) {
        const domain = super._getDomain(params);
        const thresholdFilterDomain = this._getThresholdFilterDomain();
        if (!thresholdFilterDomain.length) {
            return domain;
        }
        const result = Domain.and([domain, thresholdFilterDomain]);
        return params.raw ? result : result.toList();
    }
}
