$(document).ready(function () {
    // Add Warranty Field
    $('#is_warranty').on('click', function () {
        // let value = $('#is_warranty').val()
        if ($('#is_warranty').prop('checked')) {
            $('#warranty_details').removeClass('d-none')
        } else {
            $('#warranty_details').addClass('d-none')
        }
    });


    // get inspection record
    if ($(".evs-ins-portal").length > 0) {
        $(".evs-ins-portal").on("click", function (e) {
            let action = $(this).attr('id')
            window.location.href = "/my/tasks/portal-inspection/" + action
        });
    }


    // Function to open accordion based on hash
    function openAccordionFromHash() {
        let hash = window.location.hash;
        window.location.hash = hash
        if (hash) {
            let accordionCollapse = document.querySelector(hash);
            if (accordionCollapse) {
                let accordionButton = accordionCollapse.previousElementSibling.querySelector('.accordion-button');
                if (accordionButton.classList.contains('collapsed')) {
                    accordionButton.click(); // Simulate a click to open the accordion

                }
                // Scroll to the accordion section
                accordionCollapse.scrollIntoView();
            }
        }
    }

    openAccordionFromHash();

    // Optional: Update hash when an accordion is opened
    let accordions = document.querySelectorAll('.accordion-button');
    accordions.forEach(function (accordion) {
        accordion.addEventListener('click', function () {
            let target = accordion.getAttribute('data-bs-target');
        });
    });

    // Modal Z- Index
    $('#taskStopTimer, #portalQcConfirmation').on('show.bs.modal', function () {
        // Adjust z-index to ensure the modal is on top and append it to body
        $(this).css('z-index', 1050).appendTo('body');
        $('.modal-backdrop').css('z-index', 1040);

        // Hide overflow of the accordion to prevent text from overlapping
        $('.accordion').css('overflow', 'hidden');
    });

    // Reset overflow when the modal is hidden
    $('#taskStopTimer, #portalQcConfirmation').on('hidden.bs.modal', function () {
        $('.accordion').css('overflow', 'auto');
    });

    // Add Line
    $('.add-service-part').on('click', function () {
        $('.add-line-th').removeClass('d-none')
        $(this).addClass('d-none')
    });

    // Add Additional Part Line
    $('.add-additional-part-line').on('click', function () {
        $('.add-additional-line').removeClass('d-none')
        $(this).addClass('d-none')
        $('.request-additional-part').addClass('d-none')
        $("#additional_part_id").val('default').selectpicker("refresh");
        $("#additional_service_id").val('default').selectpicker("refresh");
        $('#additional_product_qty').val('');
        $('#additional_service_hours').val('');
    });

    // Unlink Additional Part Line
    $('.unlink-additional-part').on('click', function () {
        $('.add-additional-line').addClass('d-none')
        $('.add-additional-part-line').removeClass('d-none')
        $('.request-additional-part').removeClass('d-none')
        $("#additional_part_id").val('default').selectpicker("refresh");
        $("#additional_service_id").val('default').selectpicker("refresh");
        $('#additional_product_qty').val('');
        $('#additional_service_hours').val('');
    });

    // Onchange Addition Part Unit
    $('#additional_part_id').on('change', function () {
        let selectedOption = $(this).find('option:selected');
        let dataValue = selectedOption.data('unit-value');
        $('#add_product_unit').empty().append(`(${dataValue})`);
    });


    // Unlink Line
    $('.unlink-service-part').on('click', function () {
        $('.add-line-th').addClass('d-none')
        $('.add-service-part').removeClass('d-none')
        let currentId = this.id
        let form_id = currentId.replace('unlink', 'form');
        $(`#${form_id}`)[0].reset()
    });

    $('.alert_message_reset').on('click', function () {
        $('.alert_message').empty()
        $('.add-line-th').addClass('d-none')
        $('.add-service-part').removeClass('d-none')
    });

    // Select Unit Bases on Product
    $('.option-select').on('change', function () {
        let selectedOption = $(this).find('option:selected');
        let dataValue = selectedOption.data('unit-value');
        let dataValueId = selectedOption.data('id')
        $(`#${dataValueId}`).empty().append(dataValue);
    });

    // Refresh all selected image
    $('.add-details').on('click', function () {
        $('.ins-image-submit').addClass('d-none')
        $('.image-upload-label').empty().append(`<i class="fa fa-cloud-upload me-1" aria-hidden="true"></i>Add Image`)
    });

    // Select Search - Search Picker
    $('.selectpicker').selectpicker();


});

