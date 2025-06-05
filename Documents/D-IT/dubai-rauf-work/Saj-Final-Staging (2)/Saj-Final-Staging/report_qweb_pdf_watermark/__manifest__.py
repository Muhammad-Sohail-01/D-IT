{
    "name": "Pdf watermark",
    "version": "17.1.0",
    "author": "Rauff Imasdeen",
    "license": "LGPL-3",
    "category": "Technical Settings",
    "development_status": "Production/Stable",
    "summary": "Add watermarks to your QWEB PDF reports",
    "depends": ["web"],
    "data": [
        "demo/report.xml",
        "views/ir_actions_report_xml.xml",
        "views/res_company.xml",
    ],
    "assets": {
        "web.report_assets_pdf": [
            "/report_qweb_pdf_watermark/static/src/css/report_qweb_pdf_watermark.css"
        ],
    },
    "demo": ["demo/report.xml"],
    "installable": True,
}
