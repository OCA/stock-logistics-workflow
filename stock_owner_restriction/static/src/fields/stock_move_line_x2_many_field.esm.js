/** @odoo-module **/
import {Domain} from "@web/core/domain";
import {SMLX2ManyField} from "@stock/fields/stock_move_line_x2_many_field";
import {patch} from "@web/core/utils/patch";

patch(SMLX2ManyField.prototype, {
    setup() {
        super.setup();
        const selectCreate = this.selectCreate;
        this.selectCreate = (params) => {
            const restrictionDomain = this._getOwnerRestrictionDomain();
            if (restrictionDomain.length) {
                params.domain = Domain.and([
                    params.domain || [],
                    restrictionDomain,
                ]).toList();
            }
            return selectCreate(params);
        };
    },
    /**
     * Restrict the quants offered by the "Add line" dialog according to the
     * picking type owner restriction, mirroring the reservation rules.
     *
     * @returns {Array} domain leaves to append, empty when unrestricted
     */
    _getOwnerRestrictionDomain() {
        const data = this.props.record.data;
        const ownerId = data.restricted_owner_id ? data.restricted_owner_id[0] : false;
        switch (data.owner_restriction) {
            case "unassigned_owner":
                return [["owner_id", "=", false]];
            case "picking_partner":
                return [["owner_id", "=", ownerId]];
            case "partner_or_unassigned":
                return ["|", ["owner_id", "=", false], ["owner_id", "=", ownerId]];
            default:
                return [];
        }
    },
});
