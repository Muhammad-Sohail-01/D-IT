/** @odoo-module **/
import {jsonrpc} from "@web/core/network/rpc_service";

$(document).ready(function () {
    $('.add_part_line').on('click', function (e) {
        e.preventDefault();
        let error
        const [inspection_type, part_line_id] = this.id.split('-');
        const form_id = `${inspection_type}-${part_line_id}-sp-form`;
        const $formElements = $(`#${form_id} input[name], #${form_id} select[name]`);
        const part_data = {};

        $formElements.each(function () {
            const name = this.name;
            if (['service_id', 'part_id', 'product_qty'].includes(name)) {
                part_data[name] = $(this).val();
            }
        });
        if (!part_data['service_id']) {
            error = "Please add service"
        } else if (part_data['part_id'] && part_data['product_qty'] <= 0) {
            error = "Product Qty can not be zero"
        }

        // Validation
        if (error) {
            $('.alert_message').empty().append(`
                <div class="alert alert-danger alert-dismissible fade show" role="alert">
                  <strong>${error}</strong>
                  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            `)
        }

        if (!error) {
            $('.alert_message').empty()
            part_data['type'] = inspection_type
            part_data['id'] = part_line_id
            jsonrpc("/add/parts-services", {
                data: part_data
            }).then(function (service_part) {
                if (service_part) {
                    if (!service_part['status']) {
                        window.location = service_part['url']
                    } else if (service_part['part_name']) {
                        let line = `
                        <tr id="${service_part['part_line_id']}">
                            <td class="col-3">
                               ${service_part['service_name']}
                            </td>
                            <td class="col-3">
                                ${service_part['part_name']}
                            </td>
                            <td class="text-end col-2">
                                ${service_part['product_qty']}
                            </td>
                            <td class="col-2">
                                ${service_part['product_unit']}
                            </td>
                            <td class="col-2">
                                 <a href="#"
                                   id="${service_part['part_unlink_id']}"
                                   class="btn btn-outline-danger border-0 btn-sm unlink-service-part-line">
                                    <i class="fa fa-trash" aria-hidden="true"></i>
                                </a>
                            </td>
                        </tr>
                        `
                        $(`#${inspection_type}-${part_line_id}-sp-table tbody`).append(line);
                    } else if (!service_part['part_name']) {
                        $(`#${inspection_type}-${part_line_id}-sp-service`).append(`
                            <span class="badge evs-badge"
                                  id="${service_part['service_id']}-span">
                                ${service_part['service_name']}
                                <a href="#"
                                   class="unlink-service"
                                   id="${service_part['service_id']}">
                                    <i class="fa fa-trash ms-1 text-white"
                                       aria-hidden="true"></i>
                                </a>
                            </span>`);
                    }
                    $formElements.each(function () {
                        if ($(this).is('input')) {
                            $(this).val('');  // Clear input values
                        } else if ($(this).is('select')) {
                            $(this).val('');  // Clear the selection
                            $(this).selectpicker('refresh');  // Refresh Selectpicker to reflect the change
                        }
                    });
                }
            });
            // Button Visible or Invisible
            $('.add-service-part').removeClass('d-none')
            $('.add-line-th').addClass('d-none')
        }
    });

    // Unlink Part Line
    $(document).on("click", ".unlink-service-part-line", function (e) {
        e.preventDefault();
        const [inspection_type, part_line_id] = this.id.split('-');
        let unlink_tr_id = `${this.id}-line`
        let unlink_data = {
            'type': inspection_type,
            'part_line_id': part_line_id
        }
        jsonrpc("/unlink/part-line", {
            data: unlink_data
        }).then(function (resp) {
            if (!resp['status']) {
                window.location = resp['url']
            } else {
                $(`#${unlink_tr_id}`).remove();
            }
        });
    });

    // # Unlink Service
    $(document).on("click", ".unlink-service", function (e) {
        e.preventDefault();
        let currentId = this.id
        const [inspection_type, record_id, service_id] = currentId.split('-');
        let service_data = {
            'type': inspection_type,
            'record_id': record_id,
            'service_id': service_id
        }
        jsonrpc("/unlink/services", {
            data: service_data
        }).then(function (resp) {
            if (!resp['status']) {
                window.location = resp['url']
            } else if (resp['status'] && resp['service_name']) {
                $('.alert_message').empty().append(`
                <div class="alert alert-info alert-dismissible fade show" role="alert">
                <i class="fa fa-exclamation-triangle me-1" aria-hidden="true"></i>
                You cannot delete the <strong>${resp['service_name']}</strong> because it is already linked with parts.
                  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                </div>
            `)
            } else if (resp['status'] && !resp['service_name']) {
                $(`#${currentId}-span`).addClass('d-none')
            }
        });
    });

    // Note Submit
    $(document).on("click", ".note-form-submit", function (e) {
        e.preventDefault();
        const currentId = this.id;
        const [inspectionType, recordId, submitType] = currentId.split('-');
        const dataId = `${currentId}-submit`;
        const formData = $(`#${dataId}`).val();
        jsonrpc("/inspection/details/video-note", {
            data: {
                'submit_type': submitType,
                'type': inspectionType,
                'record_id': recordId,
                'data': formData
            }
        }).then(function (resp) {
            if (!resp['status']) {
                window.location = resp['url']
            } else {
                $(`#${currentId}-notification`).removeClass('d-none');
                setTimeout(() => {
                    $(`#${currentId}-notification`).addClass('d-none');
                }, 3000);
            }
        })
    });

    // Image Upload
    $('.ins-image-upload').on('change', function () {
        let currantId = this.id
        if (this.files && this.files[0]) {
            let reader = new FileReader();
            reader.onload = function (e) {
                $('.img-preview').attr('src', e.target.result);
                $(`#${currantId}-title`).removeClass('d-none')
                $(`#${currantId}-preview`).removeClass('d-none')
                $('.ins-image-submit').removeClass('d-none')
                $('.image-upload-label').empty().append(`<i class="fa fa-refresh me-1" aria-hidden="true"></i>Change Image`)
            };
            reader.readAsDataURL(this.files[0]);
        }
    });
    $('.ins-image-submit').on('click', function () {
        let currantId = this.id
        const [inspection_type, record_id] = currantId.split('-');
        let input_image_id = currantId.replace('submit', 'upload');
        let inputImageTitle = $(`#${input_image_id}-title`).val();
        let image_input = null;
        let file = document.getElementById(`${input_image_id}`).files[0];
        if (file) {
            let reader = new FileReader();
            reader.readAsDataURL(file);
            reader.onload = function (e) {
                image_input = e.target.result;
                let image_data = {
                    'type': inspection_type,
                    'record_id': record_id,
                    'image_title': inputImageTitle,
                    'image': image_input,
                }
                jsonrpc("/inspection/details/add-image", {
                    data: image_data
                }).then(function (resp) {
                    if (!inputImageTitle) {
                        inputImageTitle = 'Image'
                    }
                    if (!resp['status']) {
                        window.location = resp['url']
                    } else {
                        $(`#${inspection_type}-${record_id}-image-div`).prepend(`
                     <div class="col-md-4 col-sm-12 col-12 mb-3" id="${inspection_type}-${resp['image_id']}-image-unlink-div">
                        <p class="mb-1 text-start">
                             <span>
                                ${inputImageTitle}
                            </span>
                            <a href="#"
                               class="unlink-image btn btn-outline-danger border-0 btn-sm"
                               id="${inspection_type}-${resp['image_id']}-image-unlink">
                                <i class="fa fa-trash-o"
                                   aria-hidden="true">
                                   </i>
                            </a>
                        </p>
                       <img src="${e.target.result}"
                             alt="Inspection Image"
                             class="img-thumbnail inspection-portal-image"/>
                     </div>
                    `)
                        $(`#${input_image_id}-title`).addClass('d-none')
                        $(`#${input_image_id}-preview`).addClass('d-none')
                        $('.ins-image-submit').addClass('d-none')
                        $('.image-upload-label').empty().append(`<i class="fa fa-cloud-upload me-1" aria-hidden="true"></i>Add Image`)
                    }
                });
            }
        } else {
            alert('Please add image.');
        }
    })
    $(document).on("click", ".unlink-image", function (e) {
        e.preventDefault();
        let currentId = this.id
        const [inspectionType, recordId] = currentId.split('-');
        jsonrpc("/inspection/details/image-unlink", {
            data: {
                'type': inspectionType,
                'record_id': recordId,
            }
        }).then(function (resp) {
            if (!resp['status']) {
                window.location = resp['url']
            } else {
                $(`#${currentId}-div`).addClass('d-none');
            }
        });
    })
    $('.tyre-detail-submit').on('click', function (e) {
        e.preventDefault();
        let currentId = this.id
        const [inspectionType, recordId] = currentId.split('-');
        let incoming = $(`#${inspectionType}-${recordId}-incoming-submit`).val();
        let adjust = $(`#${inspectionType}-${recordId}-adjust-submit`).val();
        let tread = $(`#${inspectionType}-${recordId}-tread-submit`).val();
        jsonrpc("/inspection/details/tyre-info", {
            data: {
                'record_id': recordId,
                'type': inspectionType,
                'tyre_info': {
                    'incoming': incoming,
                    'adjust_to': adjust,
                    'tread_depth': tread
                },
            }
        }).then(function (resp) {
            if (!resp['status']) {
                window.location = resp['url']
            } else {
                $(`#${currentId}-notification`).removeClass('d-none');
                setTimeout(() => {
                    $(`#${currentId}-notification`).addClass('d-none');
                }, 3000);
            }
        });
    });

    // Complete Inspection
    $('.check-active-user').on('click', function (e) {
        e.preventDefault();
        const [health_report_id] = this.id.split('-');
        jsonrpc("/inspection/check-timer-users/", {
            data: {
                'health_report_id': health_report_id
            }
        }).then(function (resp) {
            if (!resp['status']) {
                window.location = resp['url']
            } else if (resp['status'] && resp['url']) {
                window.location = resp['url']
            } else if (resp['status'] && resp['users']) {
                $('.active-timer-users').empty().append(`
                  <div class="alert alert-info alert-dismissible fade show text-center m-2" role="alert">
                        Following user's timer are running you cannot complete inspection.
                        <br/>
                        <strong>${resp['users']}</strong>
                        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
                    </div>
                `)
            }
        })
    });

    // Send Task for QC Check
    $('.task-qc-check').on('click', function (e) {
        e.preventDefault();
        const [task_id] = this.id.split('-');
        jsonrpc("/inspection/qc-check/request", {
            'data': {
                'task_id': task_id
            }
        }).then(function (resp) {
            if (!resp['status'] && resp['url']) {
                window.location = resp['url']
            } else if (!resp['status'] && resp['error']) {
                $('#qc_check_notification').removeClass('d-none');
                $('#qc_check_notification').empty().append(`
                <div class="alert alert-warning alert-dismissible fade show text-center mb-0"
                     role="alert">
                     <i class="fa fa-exclamation-triangle me-1" aria-hidden="true"></i>
                     <strong>
                        ${resp['error']}
                    </strong>
                    <button type="button" class="btn-close" data-bs-dismiss="alert"
                            aria-label="Close"></button>
                </div>
                `)
                setTimeout(() => {
                    $('#qc_check_notification').addClass('d-none');
                }, 3000);
            } else if (resp['status']) {
                window.location.reload()
            }
        })
    })

    // Add Additional Part
    $('.add_additional_part_line').on('click', function (e) {
        e.preventDefault();

        const access_token = this.id;
        const $errorDiv = $('#additional_part_error');
        const part_id = $('#additional_part_id').val();
        const service_id = $('#additional_service_id').val();
        const part_qty = $('#additional_product_qty').val();
        const additional_time = $('#additional_service_hours').val();

        const error = validateInputs(part_id, part_qty, service_id);
        if (error) {
            showError($errorDiv, error);
            return;
        }

        jsonrpc("/add/addition-part", {
            data: {
                part_id,
                service_id,
                part_qty,
                additional_time,
                access_token
            }
        }).then(resp => {
            if (!resp.status) {
                window.location = resp.url;
            } else if (resp.status) {
                let line = `
                 <tr id=${resp['tr_line_id']}>
                    <td class="">
                        <span>${resp['part_name']}</span>
                    </td>
                    <td class="text-end">
                        <span>${resp['qty']}</span>
                    </td>
                    <td class="">
                        <span>${resp['unit']}</span>
                    </td>
                    <td class="">
                        <span>${resp['service_name']}</span>
                    </td>
                    <td class="text-center">
                        <span>${resp['required_time']}</span>
                    </td>
                    <td class="text-center">
                        <span class="badge text-bg-warning">
                        Pending Request
                        </span>
                    </td>
                    <td class="text-center">
                        <a href="#"
                           id="${resp['additional_part_line_id']}-additional-part-unlink"
                           class="btn btn-outline-danger border-0 btn-sm unlink-additional-part-line">
                            <i class="fa fa-trash"
                               aria-hidden="true"></i>
                        </a>
                    </td>
                </tr>
                `
                $('#additional-part-table tbody').append(line);
                $('.add-additional-line').addClass('d-none')
                $('.add-additional-part-line').removeClass('d-none')
                $('.request-additional-part').removeClass('d-none')
                $("#additional_part_id").val('default').selectpicker("refresh");
                $("#additional_service_id").val('default').selectpicker("refresh");
                $('#additional_product_qty').val('');
                $('#additional_service_hours').val('');
            }
        });
    });

    function validateInputs(part_id, part_qty, service_id) {
        if (!part_id) return "Add Part!";
        if (part_qty <= 0) return "Part quantity should be greater than zero.";
        if (!service_id) return "Add Service!";
        return null;
    }

    function showError($errorDiv, error) {
        $errorDiv.removeClass('d-none').html(`
        <div class="alert alert-warning alert-dismissible fade show text-center" role="alert">
            <strong>${error}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `);
        setTimeout(() => $errorDiv.addClass('d-none'), 5000);
    }

    // Unlink Additional Part Line
    $(document).on("click", ".unlink-additional-part-line", function (e) {
        e.preventDefault();
        const [part_line_id] = this.id.split('-');
        // let unlink_tr_id = `${this.id}-line`
        let unlink_data = {
            'part_line_id': part_line_id
        }
        jsonrpc("/unlink/additional-part-line", {
            data: unlink_data
        }).then(function (resp) {
            if (!resp['status']) {
                window.location = resp['url']
  add_additional_part_line          } else {
                $(`#${resp['tr_line_id']}`).remove();
            }
        });
    })

    // Request Parts
    $('.request-additional-part').on('click', function (e) {
        let task_id = this.id
        const $errorDiv = $('#additional_part_error');
        let access_token = task_id.substring(4);
        jsonrpc("/request/pending/additional-part", {
            data: {
                'access_token': access_token
            }
        }).then(function (resp) {
            if (!resp['status']) {
                window.location = resp['url']
            } else if(resp['status'] && resp['error']) {
                showError($errorDiv, resp['error']);
            } else if(resp['status'] && !resp['error']){
                window.location = resp['url']
            }
        });

    })
});

