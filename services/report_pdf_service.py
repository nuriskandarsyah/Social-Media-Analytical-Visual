from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak
)


class ReportPDFService:

    @staticmethod
    def generate(report, report_data):

        buffer = BytesIO()

        document = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=15 * mm,
            leftMargin=15 * mm,
            topMargin=15 * mm,
            bottomMargin=15 * mm
        )

        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "ReportTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=16,
            leading=20,
            spaceAfter=6
        )

        subtitle_style = ParagraphStyle(
            "ReportSubtitle",
            parent=styles["Normal"],
            alignment=TA_CENTER,
            fontSize=10,
            leading=14,
            spaceAfter=12
        )

        heading_style = ParagraphStyle(
            "ReportHeading",
            parent=styles["Heading2"],
            fontSize=12,
            leading=15,
            spaceBefore=10,
            spaceAfter=7
        )

        normal_style = ParagraphStyle(
            "ReportNormal",
            parent=styles["Normal"],
            fontSize=8.5,
            leading=12
        )

        small_style = ParagraphStyle(
            "ReportSmall",
            parent=styles["Normal"],
            fontSize=7,
            leading=9
        )

        story = []

        # ==================================================
        # DATA DASAR
        # ==================================================

        month = int(
            report.report_month
        )

        year = int(
            report.report_year
        )

        summary = report_data.get(
            "summary",
            {}
        )

        # ==================================================
        # COVER / HEADER
        # ==================================================

        story.append(
            Spacer(
                1,
                25 * mm
            )
        )

        story.append(
            Paragraph(
                "LAPORAN ANALISIS",
                title_style
            )
        )

        story.append(
            Paragraph(
                "PERFORMA KONTEN",
                title_style
            )
        )

        story.append(
            Spacer(
                1,
                8 * mm
            )
        )

        story.append(
            Paragraph(
                "DEALER HONDA",
                title_style
            )
        )

        story.append(
            Spacer(
                1,
                10 * mm
            )
        )

        story.append(
            Paragraph(
                f"Periode Laporan: "
                f"{month:02d}/{year}",
                subtitle_style
            )
        )

        story.append(
            Spacer(
                1,
                20 * mm
            )
        )

        story.append(
            Paragraph(
                "MAVis - Meta Analytical Visual",
                subtitle_style
            )
        )

        story.append(
            PageBreak()
        )

        # ==================================================
        # 1. RINGKASAN PERFORMA
        # ==================================================

        story.append(
            Paragraph(
                "1. Ringkasan Performa",
                heading_style
            )
        )

        summary_rows = [
            [
                "Indikator",
                "Nilai"
            ],
            [
                "Total Posting",
                str(
                    summary.get(
                        "total_posts",
                        0
                    )
                )
            ],
            [
                "Total Views",
                str(
                    summary.get(
                        "total_views",
                        0
                    )
                )
            ],
            [
                "Total Reach",
                str(
                    summary.get(
                        "total_reach",
                        0
                    )
                )
            ],
            [
                "Total Impressions",
                str(
                    summary.get(
                        "total_impressions",
                        0
                    )
                )
            ],
            [
                "Total Likes",
                str(
                    summary.get(
                        "total_likes",
                        0
                    )
                )
            ],
            [
                "Total Comments",
                str(
                    summary.get(
                        "total_comments",
                        0
                    )
                )
            ],
            [
                "Total Shares",
                str(
                    summary.get(
                        "total_shares",
                        0
                    )
                )
            ],
            [
                "Total Saves",
                str(
                    summary.get(
                        "total_saves",
                        0
                    )
                )
            ],
            [
                "Average Engagement Rate",
                str(
                    summary.get(
                        "average_engagement_rate",
                        0
                    )
                )
            ]
        ]

        summary_table = Table(
            summary_rows,
            colWidths=[
                90 * mm,
                70 * mm
            ],
            repeatRows=1
        )

        summary_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.5,
                    colors.grey
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "MIDDLE"
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    5
                )
            ])
        )

        story.append(
            summary_table
        )

        story.append(
            Spacer(
                1,
                10
            )
        )

        # ==================================================
        # 2. PERFORMA POSTING
        # ==================================================

        story.append(
            Paragraph(
                "2. Performa Konten",
                heading_style
            )
        )

        posts = report_data.get(
            "posts",
            []
        )

        post_rows = [
            [
                "No",
                "Caption",
                "Views",
                "Reach",
                "Likes",
                "Comments",
                "Shares",
                "ER"
            ]
        ]

        for index, item in enumerate(
            posts,
            start=1
        ):

            caption = (
                item.get(
                    "caption"
                )
                or "-"
            )

            caption = str(
                caption
            )

            if len(caption) > 45:

                caption = (
                    caption[:42]
                    + "..."
                )

            post_rows.append([
                str(index),

                Paragraph(
                    caption,
                    small_style
                ),

                str(
                    item.get(
                        "views",
                        0
                    )
                ),

                str(
                    item.get(
                        "reach",
                        0
                    )
                ),

                str(
                    item.get(
                        "likes",
                        0
                    )
                ),

                str(
                    item.get(
                        "comments",
                        0
                    )
                ),

                str(
                    item.get(
                        "shares",
                        0
                    )
                ),

                str(
                    item.get(
                        "engagement_rate",
                        0
                    )
                )
            ])

        if len(post_rows) == 1:

            post_rows.append([
                "-",
                "Tidak ada data posting",
                "-",
                "-",
                "-",
                "-",
                "-",
                "-"
            ])

        post_table = Table(
            post_rows,
            repeatRows=1,
            colWidths=[
                8 * mm,
                62 * mm,
                18 * mm,
                18 * mm,
                17 * mm,
                20 * mm,
                17 * mm,
                15 * mm
            ]
        )

        post_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.3,
                    colors.grey
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    6.5
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                )
            ])
        )

        story.append(
            post_table
        )

        # ==================================================
        # 3. FORECAST
        # ==================================================

        story.append(
            PageBreak()
        )

        story.append(
            Paragraph(
                "3. Forecast Engagement",
                heading_style
            )
        )

        forecasts = report_data.get(
            "forecasts",
            []
        )

        forecast_rows = [
            [
                "No",
                "Tanggal",
                "Predicted Engagement"
            ]
        ]

        for index, item in enumerate(
            forecasts,
            start=1
        ):

            forecast_rows.append([
                str(index),
                str(
                    item.get(
                        "forecast_date",
                        "-"
                    )
                ),
                str(
                    item.get(
                        "predicted_engagement",
                        0
                    )
                )
            ])

        if len(forecast_rows) == 1:

            forecast_rows.append([
                "-",
                "Tidak ada data forecast",
                "-"
            ])

        forecast_table = Table(
            forecast_rows,
            repeatRows=1,
            colWidths=[
                15 * mm,
                65 * mm,
                70 * mm
            ]
        )

        forecast_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    7
                )
            ])
        )

        story.append(
            forecast_table
        )

        # ==================================================
        # 4. AI CONTENT PLANNER
        # ==================================================

        story.append(
            Paragraph(
                "4. AI Content Planner",
                heading_style
            )
        )

        content_data = report_data.get(
            "content_recommendations",
            []
        )

        content_rows = [
            [
                "No",
                "Tanggal",
                "Content Title",
                "Pillar",
                "AIDA",
                "Predicted"
            ]
        ]

        for index, item in enumerate(
            content_data,
            start=1
        ):

            title = (
                item.get(
                    "content_title"
                )
                or "-"
            )

            title = str(
                title
            )

            if len(title) > 38:

                title = (
                    title[:35]
                    + "..."
                )

            content_rows.append([
                str(index),

                str(
                    item.get(
                        "posting_date",
                        "-"
                    )
                ),

                Paragraph(
                    title,
                    small_style
                ),

                str(
                    item.get(
                        "content_pillar",
                        "-"
                    )
                ),

                str(
                    item.get(
                        "aida_stage",
                        "-"
                    )
                ),

                str(
                    item.get(
                        "predicted_engagement",
                        0
                    )
                )
            ])

        if len(content_rows) == 1:

            content_rows.append([
                "-",
                "-",
                "Tidak ada content recommendation",
                "-",
                "-",
                "-"
            ])

        content_table = Table(
            content_rows,
            repeatRows=1,
            colWidths=[
                9 * mm,
                27 * mm,
                60 * mm,
                30 * mm,
                25 * mm,
                25 * mm
            ]
        )

        content_table.setStyle(
            TableStyle([
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.lightgrey
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold"
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.3,
                    colors.grey
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    6.5
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP"
                )
            ])
        )

        story.append(
            content_table
        )

        # ==================================================
        # 5. EVALUASI MANAGER
        # ==================================================

        story.append(
            PageBreak()
        )

        story.append(
            Paragraph(
                "5. Evaluasi Manager",
                heading_style
            )
        )

        evaluations = (
            report.evaluations
            or []
        )

        if not evaluations:

            story.append(
                Paragraph(
                    "Belum terdapat evaluasi dari Manager.",
                    normal_style
                )
            )

        else:

            for item in evaluations:

                story.append(
                    Paragraph(
                        "<b>Evaluasi:</b>",
                        normal_style
                    )
                )

                story.append(
                    Paragraph(
                        str(
                            item.evaluation
                            or "-"
                        ),
                        normal_style
                    )
                )

                story.append(
                    Spacer(
                        1,
                        5
                    )
                )

                story.append(
                    Paragraph(
                        "<b>Feedback:</b>",
                        normal_style
                    )
                )

                story.append(
                    Paragraph(
                        str(
                            item.feedback
                            or "-"
                        ),
                        normal_style
                    )
                )

                story.append(
                    Spacer(
                        1,
                        10
                    )
                )

        # ==================================================
        # 6. APPROVAL MANAGER
        # ==================================================

        story.append(
            Paragraph(
                "6. Persetujuan Manager",
                heading_style
            )
        )

        approvals = (
            report.approvals
            or []
        )

        if not approvals:

            story.append(
                Paragraph(
                    "Belum terdapat persetujuan laporan.",
                    normal_style
                )
            )

        else:

            approval_rows = [
                [
                    "Status",
                    "Signature",
                    "Tanggal Approval"
                ]
            ]

            for item in approvals:

                approval_rows.append([
                    str(
                        item.status
                        or "-"
                    ),

                    str(
                        item.signature_data
                        or "-"
                    ),

                    str(
                        item.approved_at
                        or "-"
                    )
                ])

            approval_table = Table(
                approval_rows,
                repeatRows=1,
                colWidths=[
                    45 * mm,
                    60 * mm,
                    55 * mm
                ]
            )

            approval_table.setStyle(
                TableStyle([
                    (
                        "BACKGROUND",
                        (0, 0),
                        (-1, 0),
                        colors.lightgrey
                    ),
                    (
                        "FONTNAME",
                        (0, 0),
                        (-1, 0),
                        "Helvetica-Bold"
                    ),
                    (
                        "GRID",
                        (0, 0),
                        (-1, -1),
                        0.4,
                        colors.grey
                    ),
                    (
                        "FONTSIZE",
                        (0, 0),
                        (-1, -1),
                        8
                    )
                ])
            )

            story.append(
                approval_table
            )

        # ==================================================
        # FOOTER
        # ==================================================

        story.append(
            Spacer(
                1,
                15
            )
        )

        story.append(
            Paragraph(
                "Laporan dibuat oleh sistem MAVis.",
                subtitle_style
            )
        )

        # ==================================================
        # BUILD PDF
        # ==================================================

        document.build(
            story
        )

        # Pastikan pointer kembali ke awal
        buffer.seek(0)

        return buffer