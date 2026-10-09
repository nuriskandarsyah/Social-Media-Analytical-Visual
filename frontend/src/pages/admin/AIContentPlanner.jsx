import {
    CalendarDays,
    CheckCircle2,
    Clock3,
    Database,
    Download,
    Lightbulb,
    RefreshCw,
    Sparkles,
    Target,
    TrendingUp,
} from "lucide-react";

import {
    useCallback,
    useEffect,
    useRef,
    useState,
} from "react";

import * as XLSX from "xlsx";

import * as api from "../../services/api";


// =====================================================
// AI CONTENT PLANNER
// =====================================================

export default function AIContentPlanner() {

    // =================================================
    // STATE
    // =================================================

    const [plans, setPlans] = useState([]);

    const [recommendation, setRecommendation] =
        useState(null);

    const [saved, setSaved] =
        useState(null);

    const [numberOfDays, setNumberOfDays] =
        useState(30);

    const [loading, setLoading] =
        useState(true);

    const [generating, setGenerating] =
        useState(false);

    const [generationStage, setGenerationStage] =
        useState(0);

    const [error, setError] =
        useState("");

    const [activeMeta, setActiveMeta] =
        useState(null);

    const initialLoadRef =
        useRef(false);


    // =================================================
    // GET EXISTING CONTENT RECOMMENDATIONS
    //
    // GET /api/ai-content-planner/
    // =================================================

    const fetchMetaAccount = useCallback(async () => {

        const result =
            await api.get(
                "/api/meta/status"
            );

        if (result?.success === false) {

            throw new Error(
                result?.message ||
                "Akun Instagram aktif tidak ditemukan."
            );

        }

        const data =
            result?.data || {};

        const instagramUserId =
            data?.instagram_user_id ||
            data?.account?.user_id ||
            null;

        if (!instagramUserId) {

            throw new Error(
                "Akun Instagram aktif tidak ditemukan. Hubungkan akun Instagram terlebih dahulu."
            );

        }

        setActiveMeta({
            instagram_user_id:
                String(instagramUserId),

            username:
                data?.account?.username ||
                "-",

            name:
                data?.account?.name ||
                data?.account?.username ||
                "-",
        });

        return String(
            instagramUserId
        );

    }, []);


    const fetchPlans = useCallback(async () => {

        try {

            setLoading(true);

            setError("");


            const instagramUserId =
                await fetchMetaAccount();


            const result =
                await api.get(
                    `/api/ai-content-planner/?instagram_user_id=${encodeURIComponent(
                        instagramUserId
                    )}`
                );


            console.log(
                "Content Planner GET response:",
                result
            );


            if (
                result?.success
            ) {

                const plansData =
                    result?.data || [];


                setPlans(
                    Array.isArray(
                        plansData
                    )
                        ? plansData
                        : []
                );

            } else {

                throw new Error(
                    result?.message ||
                    "Gagal mengambil Content Planner."
                );

            }

        } catch (err) {

            console.error(
                "Content Planner GET error:",
                err
            );


            console.error(
                "Backend error:",
                err?.response?.data
            );


            setError(
                err?.response?.data?.message ||
                "Gagal mengambil Content Planner."
            );

        } finally {

            setLoading(false);

        }

    }, [
        fetchMetaAccount,
    ]);


    // =================================================
    // INITIAL LOAD
    // =================================================

    useEffect(() => {

        if (
            initialLoadRef.current
        ) {

            return;

        }


        initialLoadRef.current =
            true;


        fetchPlans();

    }, [
        fetchPlans,
    ]);


    // =================================================
    // GENERATION PROGRESS
    //
    // Catatan:
    // Backend saat ini mengembalikan satu response
    // setelah seluruh proses selesai.
    //
    // Jadi tahap di bawah adalah indikator visual
    // frontend, bukan progress asli backend.
    // =================================================

    useEffect(() => {

        if (!generating) {
            return;
        }


        const timer1 =
            setTimeout(() => {

                setGenerationStage(2);

            }, 2500);


        const timer2 =
            setTimeout(() => {

                setGenerationStage(3);

            }, 6000);


        const timer3 =
            setTimeout(() => {

                setGenerationStage(4);

            }, 10000);


        return () => {

            clearTimeout(timer1);

            clearTimeout(timer2);

            clearTimeout(timer3);

        };

    }, [
        generating,
    ]);


    // =================================================
    // GENERATE CONTENT PLAN
    //
    // POST /api/ai-content-planner/generate
    //
    // BODY:
    // {
    //     number_of_days: 30
    // }
    // =================================================

    const generatePlan = async () => {

        try {

            setGenerationStage(1);

            setGenerating(true);

            setError("");

            setRecommendation(null);

            setSaved(null);


            console.log(
                "================================"
            );


            console.log(
                "GENERATE CONTENT PLANNER"
            );


            console.log(
                "number_of_days:",
                Number(numberOfDays)
            );


            const instagramUserId =
                await fetchMetaAccount();


            const result =
                await api.post(
                    "/api/ai-content-planner/generate",
                    {
                        number_of_days:
                            Number(numberOfDays),

                        instagram_user_id:
                            instagramUserId,
                    }
                );


            console.log(
                "Content Planner GENERATE response:",
                result
            );


            if (
                !result?.success
            ) {

                throw new Error(
                    result?.message ||
                    "Content Planner gagal dibuat."
                );

            }


            const planResult =
                result?.data || {};


            const generatedPlan =
                Array.isArray(
                    planResult?.plan
                )
                    ? planResult.plan
                    : [];


            const recommendationResult =
                planResult?.recommendation ||
                null;


            const savedResult =
                planResult?.saved ||
                null;

            setPlans(
                generatedPlan
            );


            setRecommendation(
                recommendationResult
            );


            setSaved(
                savedResult
            );


            setGenerationStage(4);


            console.log(
                "Generated plan:",
                generatedPlan
            );


            console.log(
                "Total generated:",
                generatedPlan.length
            );


            console.log(
                "Recommendation:",
                recommendationResult
            );


            console.log(
                "Saved:",
                savedResult
            );


        } catch (err) {

            console.error(
                "================================"
            );


            console.error(
                "Content Planner GENERATE error:",
                err
            );


            console.error(
                "Backend response:",
                err
            );


            setError(
                err?.message ||
                "Gagal membuat Content Planner."
            );

        } finally {

            setGenerating(false);

            setGenerationStage(0);

        }

    };


    // =================================================
    // EXPORT TO EXCEL
    // =================================================

    const exportToExcel = () => {

        if (
            !plans.length
        ) {

            alert(
                "Belum ada Content Planner yang dapat diekspor."
            );

            return;

        }


        console.log(
            "Exporting Content Planner:",
            plans
        );


        const excelData =
            plans.map(
                (
                    item,
                    index
                ) => ({

                    "No":
                        index + 1,

                    "Hari":
                        item.day ||
                        index + 1,

                    "Tanggal Posting":
                        formatDate(
                            item.posting_date
                        ),

                    "Judul Konten":
                        item.content_title ||
                        "-",

                    "Deskripsi Konten":
                        item.content_description ||
                        "-",

                    "Tipe Konten":
                        normalizeText(
                            item.content_type
                        ),

                    "Objective":
                        item.objective ||
                        "-",

                    "Content Pillar":
                        normalizeText(
                            item.content_pillar
                        ),

                    "AIDA Stage":
                        normalizeText(
                            item.aida_stage
                        ),

                    "Predicted Engagement":
                        Number(
                            item.predicted_engagement ||
                            0
                        ),

                })
            );


        const worksheet =
            XLSX.utils.json_to_sheet(
                excelData
            );


        worksheet["!cols"] = [

            {
                wch: 6,
            },

            {
                wch: 8,
            },

            {
                wch: 18,
            },

            {
                wch: 40,
            },

            {
                wch: 60,
            },

            {
                wch: 18,
            },

            {
                wch: 28,
            },

            {
                wch: 20,
            },

            {
                wch: 18,
            },

            {
                wch: 24,
            },

        ];


        const workbook =
            XLSX.utils.book_new();


        XLSX.utils.book_append_sheet(
            workbook,
            worksheet,
            "Content Planner"
        );


        XLSX.writeFile(
            workbook,
            "MAVis_Content_Planner.xlsx"
        );

    };


    // =================================================
    // FORMAT DATE
    // =================================================

    function formatDate(
        value
    ) {

        if (!value) {

            return "-";

        }


        const date =
            new Date(value);


        if (
            Number.isNaN(
                date.getTime()
            )
        ) {

            return value;

        }


        return date.toLocaleDateString(
            "id-ID",
            {
                day: "2-digit",
                month: "short",
                year: "numeric",
            }
        );

    }


    // =================================================
    // FORMAT NUMBER
    // =================================================

    function formatNumber(
        value
    ) {

        const number =
            Number(value || 0);


        return number.toLocaleString(
            "id-ID",
            {
                maximumFractionDigits: 2,
            }
        );

    }


    // =================================================
    // NORMALIZE TEXT
    // =================================================

    function normalizeText(
        value
    ) {

        if (!value) {

            return "-";

        }


        return String(value)
            .replaceAll(
                "_",
                " "
            )
            .replace(
                /\b\w/g,
                (
                    letter
                ) =>
                    letter.toUpperCase()
            );

    }


    // =================================================
    // LOADING INITIAL PAGE
    // =================================================

    if (loading) {

        return (

            <div className="ai-analysis-loading">

                <div className="ai-analysis-loading-spinner" />

                <p>
                    Memuat Content Planner...
                </p>

            </div>

        );

    }


    // =================================================
    // AVERAGE PREDICTION
    // =================================================

    const averagePrediction =
        plans.length > 0
            ? plans.reduce(
                (
                    total,
                    item
                ) =>
                    total +
                    Number(
                        item.predicted_engagement ||
                        0
                    ),
                0
            ) /
            plans.length
            : 0;


    // =================================================
    // PAGE
    // =================================================

    return (

        <div className="ai-planner-page">


            {/* =================================================
                HEADER
            ================================================= */}

            <div className="ai-planner-header">

                <div>

                    <div className="ai-planner-breadcrumb">

                        <Sparkles
                            size={15}
                        />

                        <span>
                            AI Content Planner
                        </span>

                    </div>


                    <h1>
                        Perencanaan Konten AI
                    </h1>


                    <p>
                        Membuat rekomendasi konten
                        berdasarkan data dan analisis
                        yang tersedia pada sistem.
                    </p>

                    {activeMeta && (

                        <div
                            className="ai-planner-active-account"
                        >

                            <span>
                                Akun aktif
                            </span>

                            <strong>
                                {
                                    activeMeta.name ||
                                    activeMeta.username ||
                                    "-"
                                }
                            </strong>

                            <small>
                                @{
                                    activeMeta.username ||
                                    "-"
                                }
                            </small>

                        </div>

                    )}

                </div>

            </div>


            {/* =================================================
                ERROR
            ================================================= */}

            {error && (

                <div className="ai-analysis-error">

                    <span>
                        {error}
                    </span>


                    <button
                        type="button"
                        onClick={
                            fetchPlans
                        }
                    >
                        Coba lagi
                    </button>

                </div>

            )}


            {/* =================================================
                GENERATOR
            ================================================= */}

            <section className="ai-planner-generator">

                <div className="ai-planner-generator-header">

                    <div className="ai-planner-generator-icon">

                        <Sparkles
                            size={20}
                        />

                    </div>


                    <div>

                        <span>
                            AI CONTENT GENERATOR
                        </span>


                        <h2>
                            Buat Content Plan
                        </h2>


                        <p>
                            Tentukan jumlah hari untuk
                            menghasilkan rekomendasi
                            content plan.
                        </p>

                    </div>

                </div>


                <div className="ai-planner-generator-body">

                    <div className="ai-planner-field">

                        <label>
                            Jumlah Hari
                        </label>


                        <div className="ai-planner-input">

                            <CalendarDays
                                size={16}
                            />


                            <select
                                value={
                                    numberOfDays
                                }
                                onChange={(
                                    event
                                ) =>
                                    setNumberOfDays(
                                        Number(
                                            event.target.value
                                        )
                                    )
                                }
                                disabled={
                                    generating
                                }
                            >

                                <option value={7}>
                                    7 Hari
                                </option>

                                <option value={14}>
                                    14 Hari
                                </option>

                                <option value={21}>
                                    21 Hari
                                </option>

                                <option value={30}>
                                    30 Hari
                                </option>

                            </select>

                        </div>

                    </div>


                    <button
                        type="button"
                        className="ai-planner-generate-button"
                        onClick={
                            generatePlan
                        }
                        disabled={
                            generating
                        }
                    >

                        {generating ? (

                            <>
                                <RefreshCw
                                    size={16}
                                    className="ai-planner-spin"
                                />

                                Menyusun {numberOfDays} hari...

                            </>

                        ) : (

                            <>
                                <Sparkles
                                    size={16}
                                />

                                Generate Content Plan

                            </>

                        )}

                    </button>

                </div>

            </section>


            {/* =================================================
                GENERATION PROGRESS
            ================================================= */}

            {generating && (

                <div className="ai-planner-generation-progress">

                    <div className="ai-planner-generation-top">

                        <div>

                            <span>
                                AI CONTENT PLANNER
                            </span>


                            <h3>
                                Sedang membuat rencana konten
                            </h3>


                            <p>
                                Proses dapat membutuhkan waktu
                                lebih lama untuk periode yang lebih panjang.
                            </p>

                        </div>


                        <div className="ai-planner-generation-count">

                            {numberOfDays} Hari

                        </div>

                    </div>


                    <div className="ai-planner-progress-line">

                        <div
                            className="ai-planner-progress-fill"
                        />

                    </div>


                    <div className="ai-planner-generation-steps">


                        <GenerationStep
                            number="01"
                            title="Mempersiapkan data"
                            description="Menyiapkan proses content planning"
                            active={
                                generationStage >= 1
                            }
                            done={
                                generationStage > 1
                            }
                        />


                        <GenerationStep
                            number="02"
                            title="Menganalisis rekomendasi"
                            description="Memproses dasar rekomendasi konten"
                            active={
                                generationStage >= 2
                            }
                            done={
                                generationStage > 2
                            }
                        />


                        <GenerationStep
                            number="03"
                            title="Menyusun content plan"
                            description={
                                `Membuat rencana untuk ${numberOfDays} hari`
                            }
                            active={
                                generationStage >= 3
                            }
                            done={
                                generationStage > 3
                            }
                        />


                        <GenerationStep
                            number="04"
                            title="Menyelesaikan hasil"
                            description="Menunggu hasil dari server"
                            active={
                                generationStage >= 4
                            }
                            done={false}
                        />

                    </div>

                </div>

            )}


            {/* =================================================
                SUMMARY
            ================================================= */}

            <div className="ai-planner-summary-grid">


                <PlannerSummary
                    icon={
                        CalendarDays
                    }
                    label="Total Konten"
                    value={
                        plans.length
                    }
                    description="Content plan tersedia"
                />


                <PlannerSummary
                    icon={
                        TrendingUp
                    }
                    label="Prediksi Rata-rata"
                    value={
                        formatNumber(
                            averagePrediction
                        )
                    }
                    description="Predicted engagement"
                />


                <PlannerSummary
                    icon={
                        Target
                    }
                    label="Periode"
                    value={
                        `${numberOfDays} Hari`
                    }
                    description="Content planner"
                />


                <PlannerSummary
                    icon={
                        Database
                    }
                    label="Recommendation"
                    value={
                        recommendation
                            ? "Ready"
                            : "-"
                    }
                    description="AI recommendation"
                />

            </div>


            {/* =================================================
                EMPTY STATE
            ================================================= */}

            {plans.length === 0 && !generating && (

                <div className="ai-planner-empty">

                    <div className="ai-planner-empty-icon">

                        <CalendarDays
                            size={25}
                        />

                    </div>


                    <h3>
                        Belum ada Content Planner
                    </h3>


                    <p>
                        Pilih jumlah hari kemudian
                        klik Generate Content Plan
                        untuk membuat rekomendasi.
                    </p>

                </div>

            )}


            {/* =================================================
                RESULT
            ================================================= */}

            {plans.length > 0 && !generating && (

                <section className="ai-planner-result">

                    <div className="ai-planner-result-header">

                        <div>

                            <span>
                                AI GENERATED CONTENT PLAN
                            </span>


                            <h2>
                                Rekomendasi Konten
                            </h2>


                            <p>
                                {
                                    plans.length
                                }{" "}
                                rekomendasi konten tersedia.
                            </p>

                        </div>


                        <div className="ai-planner-result-actions">

                            <button
                                type="button"
                                className="ai-planner-export-button"
                                onClick={
                                    exportToExcel
                                }
                                disabled={
                                    !plans.length
                                }
                            >

                                <Download
                                    size={15}
                                />

                                Export Excel

                            </button>

                        </div>

                    </div>


                    {/* =========================================
                        PLAN LIST
                    ========================================= */}

                    <div className="ai-planner-list">

                        {plans.map(
                            (
                                item,
                                index
                            ) => (

                                <PlannerCard
                                    key={
                                        item.id_cr ||
                                        `${item.day}-${index}`
                                    }
                                    item={
                                        item
                                    }
                                    index={
                                        index
                                    }
                                    formatDate={
                                        formatDate
                                    }
                                    formatNumber={
                                        formatNumber
                                    }
                                    normalizeText={
                                        normalizeText
                                    }
                                />

                            )
                        )}

                    </div>

                </section>

            )}


            {/* =================================================
                RECOMMENDATION
            ================================================= */}

            {recommendation && !generating && (

                <section className="ai-planner-rag-panel">

                    <div className="ai-planner-rag-icon">

                        <Lightbulb
                            size={19}
                        />

                    </div>


                    <div>

                        <span>
                            AI RECOMMENDATION
                        </span>


                        <h3>
                            Informasi Recommendation
                        </h3>


                        <p>
                            Model:
                            {" "}
                            {
                                recommendation.model ||
                                "-"
                            }
                        </p>


                        <p>
                            Embedding Model:
                            {" "}
                            {
                                recommendation.embedding_model ||
                                "-"
                            }
                        </p>


                        <p>
                            RAG Sources:
                            {" "}
                            {
                                Array.isArray(
                                    recommendation.rag_sources
                                )
                                    ? recommendation.rag_sources.length
                                    : 0
                            }
                        </p>

                    </div>

                </section>

            )}


            {/* =================================================
                SAVED
            ================================================= */}

            {saved && !generating && (

                <section className="ai-planner-saved-panel">

                    <CheckCircle2
                        size={17}
                    />

                    <div>

                        <strong>
                            Content Planner tersimpan
                        </strong>


                        <p>
                            Hasil generate berhasil
                            diproses oleh backend.
                        </p>

                    </div>

                </section>

            )}

        </div>

    );

}


// =====================================================
// SUMMARY CARD
// =====================================================

function PlannerSummary({
    icon: Icon,
    label,
    value,
    description,
}) {

    return (

        <div className="ai-planner-summary-card">

            <div className="ai-planner-summary-icon">

                <Icon
                    size={18}
                />

            </div>


            <span>
                {label}
            </span>


            <strong>
                {value}
            </strong>


            <p>
                {description}
            </p>

        </div>

    );

}


// =====================================================
// GENERATION STEP
// =====================================================

function GenerationStep({
    number,
    title,
    description,
    active,
    done,
}) {

    return (

        <div
            className={
                `ai-planner-generation-step ${
                    active
                        ? "is-active"
                        : ""
                } ${
                    done
                        ? "is-done"
                        : ""
                }`
            }
        >

            <div className="ai-planner-generation-step-number">

                {done ? (

                    <CheckCircle2
                        size={14}
                    />

                ) : (

                    number

                )}

            </div>


            <div className="ai-planner-generation-step-content">

                <strong>
                    {title}
                </strong>


                <span>
                    {description}
                </span>

            </div>


            {active && !done && (

                <RefreshCw
                    size={14}
                    className="ai-planner-generation-step-spin"
                />

            )}

        </div>

    );

}


// =====================================================
// PLAN CARD
// =====================================================

function PlannerCard({
    item,
    index,
    formatDate,
    formatNumber,
    normalizeText,
}) {

    return (

        <article
            className="ai-planner-card"
            style={{
                animationDelay:
                    `${index * 60}ms`,
            }}
        >

            {/* =============================================
                NUMBER
            ============================================= */}

            <div className="ai-planner-card-number">

                {
                    String(
                        item.day ||
                        index + 1
                    ).padStart(
                        2,
                        "0"
                    )
                }

            </div>


            <div className="ai-planner-card-content">


                {/* =============================================
                    DATE / TYPE
                ============================================= */}

                <div className="ai-planner-card-top">

                    <span className="ai-planner-date">

                        <CalendarDays
                            size={13}
                        />

                        {
                            formatDate(
                                item.posting_date
                            )
                        }

                    </span>


                    <span className="ai-planner-type">

                        {
                            normalizeText(
                                item.content_type
                            )
                        }

                    </span>

                </div>


                {/* =============================================
                    TITLE
                ============================================= */}

                <h3>

                    {
                        item.content_title ||
                        "-"
                    }

                </h3>


                {/* =============================================
                    DESCRIPTION
                ============================================= */}

                <p className="ai-planner-description">

                    {
                        item.content_description ||
                        "-"
                    }

                </p>


                {/* =============================================
                    OBJECTIVE
                ============================================= */}

                <div className="ai-planner-objective">

                    <Target
                        size={13}
                    />

                    <span>

                        {
                            item.objective ||
                            "-"
                        }

                    </span>

                </div>


                {/* =============================================
                    META
                ============================================= */}

                <div className="ai-planner-card-meta">

                    <span>

                        <Lightbulb
                            size={13}
                        />

                        {
                            normalizeText(
                                item.content_pillar
                            )
                        }

                    </span>


                    <span>

                        <Target
                            size={13}
                        />

                        {
                            normalizeText(
                                item.aida_stage
                            )
                        }

                    </span>


                    <span>

                        <TrendingUp
                            size={13}
                        />

                        {
                            formatNumber(
                                item.predicted_engagement
                            )
                        }

                    </span>

                </div>


                {/* =============================================
                    FOOTER
                ============================================= */}

                <div className="ai-planner-card-footer">

                    <span>

                        <Clock3
                            size={12}
                        />

                        {
                            formatDate(
                                item.posting_date
                            )
                        }

                    </span>


                    <span className="ai-planner-ready">

                        <CheckCircle2
                            size={12}
                        />

                        Ready

                    </span>

                </div>

            </div>

        </article>

    );

}