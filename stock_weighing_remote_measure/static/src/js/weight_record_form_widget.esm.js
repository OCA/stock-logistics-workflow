/** @odoo-module **/
import {RemoteMeasure} from "@web_widget_remote_measure/js/remote_measure_widget.esm";
import fieldRegistry from "web.field_registry";
import {qweb} from "web.core";

export const RemoteMeasureForm = RemoteMeasure.extend({
    _template: "weigh_remote_measure.RemoteMeasureForm",
    events: Object.assign(
        {},
        // Let's map all the existing events to input.o_input_weight so we can
        // add an extra input for the manual tare
        Object.entries(RemoteMeasure.prototype.events).reduce(
            (events, [event, func]) => {
                events[`${event} input.o_input_weight`] = func;
                return events;
            },
            {}
        ),
        // Manual tare events
        {
            "focusin div[name='manual_tare'] input": "_onFocusInputTare",
            "change div[name='manual_tare'] input": "_onChangeInputTare",
            "click div[name='manual_tare'] button": "_onStepTare",
        }
    ),
    /**
     * Add tare options
     * @override
     */
    init() {
        this._super(...arguments);
        this.tares = this.nodeOptions.tares;
        this.tare = 0;
        this.number_format_options = {
            minimumFractionDigits: 3,
            useGrouping: false,
        };
    },
    /**
     * Number formatting helper
     * @param {Number} weight
     * @returns {String}
     */
    format_weight(weight) {
        return weight.toLocaleString(this.locale_code, this.number_format_options);
    },
    /**
     * Render tare options and infos and set special layout
     * @override
     */
    _renderEdit() {
        const def = this._super(...arguments);
        if (!this.remote_device_data) {
            return def;
        }
        this.amount = this.input_val;
        this.$el.prepend(
            qweb.render(this._template, {
                tares: this.tares || [],
                uom_name: (this.uom && this.uom.name) || "",
                amount: this.input_val,
                device_name:
                    (this.remote_device_data && this.remote_device_data.name) || "",
            })
        );
        this.$el.addClass("weight_wizard");
        this.$el.find("btn[data-tare]").on("click", this._onClickTare.bind(this));
        this.$tare_amount = this.$el.find("span[name='tare_amount']");
        this.$real_amount = this.$el.find("span[name='real_amount']");
        const $weight_control = this.$el.find("div[name='weight_control']");
        // Tweak the base widget
        this.$start_measure.appendTo($weight_control);
        this.$start_measure.addClass("btn-lg float-left");
        this.$stop_measure.addClass("btn-lg float-left");
        this.$stop_measure.appendTo($weight_control);
        this.$input.appendTo($weight_control);
        this.$input.attr("inputemode", "decimal");
        this.$input.addClass("text-info o_input_weight w-50");
        this.$el.removeClass("form-control-lg");
        this.$input.val(
            this.value.toLocaleString(this.locale_code, {
                minimumFractionDigits: 3,
                useGrouping: false,
            })
        );
        return def;
    },
    /**
     * Add the tare to the real weighted measure
     * @override
     */
    async _setMeasure() {
        await this._super(...arguments);
        let total = this.amount;
        this.$input.val(this.format_weight(total));
        if (this.tare) {
            total = this.amount - this.tare;
            this.$real_amount.text(this.amount);
            this.$input.val(this.format_weight(total));
            this._setValue(this.$input.val());
        }
    },

    /* TARE METHODS */

    _updateTare() {
        this.$tare_amount.text(this.format_weight(this.tare));
        this.$real_amount.text(this.format_weight(this.amount));
        this._setMeasure();
    },
    /**
     * Add the tare to the total weight
     * @param {Event} ev
     */
    _onClickTare(ev) {
        ev.preventDefault();
        const tare = parseFloat(ev.currentTarget.dataset.tare);
        this.tare = Math.max(0, this.tare + tare);
        this._updateTare();
    },
    /**
     * Upgrade the measure counter
     */
    _onChange() {
        this.amount = parseFloat(this.$input.val() || "0");
        this._super(...arguments);
    },
    /**
     * Auto select
     * @param {Event} ev
     */
    _onFocusInputTare(ev) {
        ev.currentTarget.select();
    },
    /**
     * Generic method to update the tare
     * @param {Number} tare
     */
    _changeTare(tare) {
        this.tare = tare;
        this._updateTare();
    },
    /**
     * Update the tare manually
     * @param {Event} ev
     */
    _onChangeInputTare(ev) {
        this._changeTare(parseFloat(ev.currentTarget.value));
    },
    /**
     * Step up/down the manual tare value
     * @param {Event} ev
     */
    _onStepTare(ev) {
        const step_button = ev.currentTarget;
        const input = step_button
            .closest("[name='manual_tare']")
            .querySelector("input");
        if (step_button.dataset.mode === "plus") {
            input.stepUp();
        } else {
            input.stepDown();
        }
        this._changeTare(parseFloat(input.value));
    },
});

fieldRegistry.add("remote_measure_form", RemoteMeasureForm);
