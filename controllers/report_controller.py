from flask import (
    Blueprint,
    request,
    jsonify,
    send_file
)

from flask_jwt_extended import (
    get_jwt_identity
)

from services.report_service import (
    ReportService
)

from services.report_pdf_service import (
    ReportPDFService
)

from utils.auth import (
    jwt_required_role
)


report_bp = Blueprint(
    "report",
    __name__,
    url_prefix="/api/reports"
)


# =========================================================
# GET ALL REPORTS
# ADMIN & MANAGER
# =========================================================

@report_bp.route(
    "/",
    methods=["GET"]
)
@jwt_required_role(
    "admin",
    "manager"
)
def get_reports():

    month = request.args.get(
        "month",
        type=int
    )

    year = request.args.get(
        "year",
        type=int
    )

    try:

        data = ReportService.get_all(
            month=month,
            year=year
        )

        return jsonify({
            "success": True,
            "message": (
                "Data laporan berhasil diambil"
            ),
            "data": data,
            "filter": {
                "month": month,
                "year": year
            }
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": (
                "Gagal mengambil data laporan"
            ),
            "error": str(e)
        }), 500


# =========================================================
# GENERATE REPORT
# ADMIN & MANAGER
# =========================================================

@report_bp.route(
    "/generate",
    methods=["POST"]
)
@jwt_required_role(
    "admin",
    "manager"
)
def generate_report():

    data = request.get_json() or {}

    month = data.get(
        "month"
    )

    year = data.get(
        "year"
    )

    if month is None or year is None:

        return jsonify({
            "success": False,
            "message": (
                "Month dan year wajib diisi"
            )
        }), 400

    try:

        month = int(month)
        year = int(year)

    except (
        TypeError,
        ValueError
    ):

        return jsonify({
            "success": False,
            "message": (
                "Month dan year harus berupa angka"
            )
        }), 400

    if month < 1 or month > 12:

        return jsonify({
            "success": False,
            "message": (
                "Month tidak valid"
            )
        }), 400

    if year < 2000 or year > 2100:

        return jsonify({
            "success": False,
            "message": (
                "Year tidak valid"
            )
        }), 400

    try:

        report, created = (
            ReportService.create_report(
                month,
                year
            )
        )

        report_data = (
            ReportService.get_report_data(
                month,
                year
            )
        )

        return jsonify({
            "success": True,
            "message": (
                "Laporan berhasil dibuat"
            ),
            "data": {
                "report": (
                    ReportService
                    .serialize_report(
                        report
                    )
                ),
                "created": created,
                "report_data": report_data
            }
        }), 200

    except ValueError as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except Exception as e:

        return jsonify({
            "success": False,
            "message": (
                "Gagal membuat laporan"
            ),
            "error": str(e)
        }), 500


# =========================================================
# GET DETAIL REPORT
# ADMIN & MANAGER
# =========================================================

@report_bp.route(
    "/<int:id_report>",
    methods=["GET"]
)
@jwt_required_role(
    "admin",
    "manager"
)
def get_report(id_report):

    try:

        report = (
            ReportService.get_by_id(
                id_report
            )
        )

        if not report:

            return jsonify({
                "success": False,
                "message": (
                    "Laporan tidak ditemukan"
                )
            }), 404

        report_data = (
            ReportService.get_report_data(
                report.report_month,
                report.report_year
            )
        )

        return jsonify({
            "success": True,
            "message": (
                "Detail laporan berhasil diambil"
            ),
            "data": {
                "report": (
                    ReportService
                    .serialize_report(
                        report
                    )
                ),
                "report_data": report_data
            }
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "message": (
                "Gagal mengambil detail laporan"
            ),
            "error": str(e)
        }), 500


# =========================================================
# SAVE EVALUATION
# HANYA MANAGER
# =========================================================

@report_bp.route(
    "/<int:id_report>/evaluation",
    methods=["POST"]
)
@jwt_required_role(
    "manager"
)
def save_evaluation(id_report):

    data = request.get_json() or {}

    evaluation = data.get(
        "evaluation"
    )

    feedback = data.get(
        "feedback"
    )

    user_id = get_jwt_identity()

    if not evaluation:

        return jsonify({
            "success": False,
            "message": (
                "Evaluation wajib diisi"
            )
        }), 400

    if not isinstance(
        evaluation,
        str
    ):

        return jsonify({
            "success": False,
            "message": (
                "Evaluation harus berupa teks"
            )
        }), 400

    evaluation = evaluation.strip()

    if not evaluation:

        return jsonify({
            "success": False,
            "message": (
                "Evaluation tidak boleh kosong"
            )
        }), 400

    if isinstance(
        feedback,
        str
    ):

        feedback = feedback.strip()

    try:

        item = (
            ReportService.save_evaluation(
                id_report=id_report,
                id_user=int(user_id),
                evaluation=evaluation,
                feedback=feedback
            )
        )

        return jsonify({
            "success": True,
            "message": (
                "Evaluasi laporan berhasil disimpan"
            ),
            "data": (
                ReportService
                .serialize_evaluation(
                    item
                )
            )
        }), 200

    except ValueError as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except Exception as e:

        return jsonify({
            "success": False,
            "message": (
                "Gagal menyimpan evaluasi"
            ),
            "error": str(e)
        }), 500


# =========================================================
# APPROVAL REPORT
# HANYA MANAGER
# =========================================================

@report_bp.route(
    "/<int:id_report>/approval",
    methods=["POST"]
)
@jwt_required_role(
    "manager"
)
def approve_report(id_report):

    data = request.get_json() or {}

    status = data.get(
        "status"
    )

    signature_data = data.get(
        "signature_data"
    )

    user_id = get_jwt_identity()

    if not status:

        return jsonify({
            "success": False,
            "message": (
                "Status approval wajib diisi"
            )
        }), 400

    if status not in [
        "pending",
        "approved",
        "rejected"
    ]:

        return jsonify({
            "success": False,
            "message": (
                "Status approval tidak valid"
            )
        }), 400

    if isinstance(
        signature_data,
        str
    ):

        signature_data = (
            signature_data.strip()
        )

    try:

        item = (
            ReportService.save_approval(
                id_report=id_report,
                id_user=int(user_id),
                status=status,
                signature_data=signature_data
            )
        )

        return jsonify({
            "success": True,
            "message": (
                "Persetujuan laporan berhasil disimpan"
            ),
            "data": (
                ReportService
                .serialize_approval(
                    item
                )
            )
        }), 200

    except ValueError as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400

    except Exception as e:

        return jsonify({
            "success": False,
            "message": (
                "Gagal menyimpan persetujuan"
            ),
            "error": str(e)
        }), 500


# =========================================================
# EXPORT PDF
# ADMIN & MANAGER
# =========================================================

@report_bp.route(
    "/<int:id_report>/export-pdf",
    methods=["GET"]
)
@jwt_required_role(
    "admin",
    "manager"
)
def export_pdf(id_report):

    try:

        # -------------------------------------------------
        # Ambil laporan
        # -------------------------------------------------

        report = (
            ReportService.get_by_id(
                id_report
            )
        )

        if not report:

            return jsonify({
                "success": False,
                "message": (
                    "Laporan tidak ditemukan"
                )
            }), 404

        # -------------------------------------------------
        # Ambil seluruh data laporan
        # -------------------------------------------------

        report_data = (
            ReportService.get_report_data(
                report.report_month,
                report.report_year
            )
        )

        # -------------------------------------------------
        # Generate PDF
        # -------------------------------------------------

        pdf_buffer = (
            ReportPDFService.generate(
                report=report,
                report_data=report_data
            )
        )

        # -------------------------------------------------
        # Nama file
        # -------------------------------------------------

        filename = (
            f"Laporan_MAVis_"
            f"{report.report_month:02d}_"
            f"{report.report_year}.pdf"
        )

        # -------------------------------------------------
        # Kirim file PDF
        # -------------------------------------------------

        return send_file(
            pdf_buffer,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:

        return jsonify({
            "success": False,
            "message": (
                "Gagal membuat PDF laporan"
            ),
            "error": str(e)
        }), 500