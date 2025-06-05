/** @odoo-module **/
import {jsonrpc} from "@web/core/network/rpc_service";

$(document).ready(function () {
    $("#vehicle_brand_id").on("change", function () {
        let text = "<option value='' selected='selected'>Select Model</option>";
        let brandId = $(this).val();
        jsonrpc("/get_model", {brand_id: brandId}).then(function (model_ids) {
            if (model_ids) {
                for (let key in model_ids) {
                    text = text + '<option value="' + key + '">' + model_ids[key] + '</option>'
                }
                $('#vehicle_model_id').empty().append(text);
            }
        });
    });
    $("#vin_no").on("change", function () {
        let vinNo = $(this).val();
        let text = ' <small class="form-text text-danger" id="vin_no_validation">\n' +
            '                            <i class="fa fa-exclamation-triangle ms-2 me-1"/>\n' +
            '                            VIN No should be 17 characters long.\n' +
            '                        </small>'
        if (vinNo && vinNo.length !== 17) {
            $('#vin_no_validation').empty().append(text);
        } else {
            $('#vin_no_validation').empty();
        }
    });
});

