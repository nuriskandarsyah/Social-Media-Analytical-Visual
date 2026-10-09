import {
    useEffect,
    useMemo,
    useState,
} from "react";

import {
    BarChart3,
    Brain,
    CalendarDays,
    CheckCircle2,
    ChevronDown,
    Clock3,
    Lightbulb,
    RefreshCw,
    Target,
    TrendingDown,
    TrendingUp,
    Users,
    WandSparkles,
} from "lucide-react";

import {
    Bar,
    BarChart,
    CartesianGrid,
    Line,
    LineChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";

import * as api from "../../services/api";


export default function AIAnalysis() {

    const [data, setData] = useState(null);

    const [loading, setLoading] =
        useState(true);

    const [refreshing, setRefreshing] =
        useState(false);

    const [error, setError] =
        useState("");

    const [month, setMonth] =
        useState("");

    const [year, setYear] =
        useState("");


    // =====================================================
    // FETCH ANALYSIS
    // =====================================================

    const fetchAnalysis = async (
        showRefresh = false
    ) => {

        try {

            if (showRefresh) {
                setRefreshing(true);
            } else {
                setLoading(true);
            }

            setError("");

            const body = {};

            if (month !== "") {
                body.month = Number(month);
            }

            if (year !== "") {
                body.year = Number(year);
            }

            console.log(
                "AI Analysis request:",
                body
            );

            // Satu request untuk seluruh proses analisis.
            const response =
                await api.post(
                    "/api/ai-analysis/",
                    body
                );

            console.log(
                "AI Analysis response:",
                response?.data
            );

            const payload =
                response?.data || {};

            if (
                payload?.success === false
            ) {
                throw new Error(
                    payload?.message ||
                    "Analisis AI gagal."
                );
            }

            const result =
                payload?.data ??
                payload;

            if (
                !result ||
                typeof result !== "object"
            ) {
                throw new Error(
                    "Response Analisis AI tidak valid."
                );
            }

            const cluster =
                result?.cluster &&
                typeof result.cluster === "object"
                    ? result.cluster
                    : {};

            const clusterSummary =
                Array.isArray(
                    result?.cluster_summary
                )
                    ? result.cluster_summary
                    : [];

            const aiInsight =
                result?.ai_insight &&
                typeof result.ai_insight === "object"
                    ? result.ai_insight
                    : {};

            const forecast =
                Array.isArray(
                    result?.forecast
                )
                    ? result.forecast
                    : [];

            const forecastPerContent =
                result?.forecast_per_content &&
                typeof result.forecast_per_content === "object"
                    ? result.forecast_per_content
                    : {};

            const bestContentNextWeek =
                result?.best_content_next_week &&
                typeof result.best_content_next_week === "object"
                    ? result.best_content_next_week
                    : {};

            const strategy =
                Array.isArray(
                    result?.strategy
                )
                    ? result.strategy
                    : (
                        Array.isArray(
                            aiInsight?.strategy
                        )
                            ? aiInsight.strategy
                            : []
                    );

            const analysis = {
                total_content:
                    Number(
                        result?.total_content ??
                        result?.total_data ??
                        cluster?.total_data ??
                        0
                    ) || 0,

                cluster: {
                    ...cluster,
                    cluster_count:
                        Number(
                            cluster?.cluster_count ??
                            result?.cluster_count ??
                            0
                        ) || 0,
                },

                cluster_summary:
                    clusterSummary,

                ai_insight:
                    aiInsight,

                forecast:
                    forecast,

                forecast_per_content:
                    forecastPerContent,

                best_content_next_week:
                    bestContentNextWeek,

                strategy:
                    strategy,
            };

            console.log(
                "FINAL AI ANALYSIS:",
                analysis
            );

            console.log(
                "STRATEGY DATA:",
                analysis.strategy
            );

            setData(
                analysis
            );

        } catch (err) {

            console.error(
                "AI Analysis error:",
                err
            );

            console.error(
                "API error:",
                err?.response?.data
            );

            setError(
                err?.response?.data?.message ||
                err?.message ||
                "Tidak dapat mengambil hasil Analisis AI."
            );

        } finally {

            setLoading(false);

            setRefreshing(false);

        }

    };

    useEffect(() => {

        fetchAnalysis();

    }, []);


    // =====================================================
    // FORMAT
    // =====================================================

    const formatNumber = (
        value
    ) => {

        if (
            value === null ||
            value === undefined
        ) {
            return "0";
        }


        return new Intl.NumberFormat(
            "id-ID"
        ).format(
            Number(value)
        );

    };


    const formatDecimal = (
        value
    ) => {

        if (
            value === null ||
            value === undefined
        ) {
            return "0";
        }


        return Number(value)
            .toLocaleString(
                "id-ID",
                {
                    maximumFractionDigits: 2,
                }
            );

    };


    const formatPercentage = (
        value
    ) => {

        if (
            value === null ||
            value === undefined
        ) {
            return "0%";
        }


        return `${Number(value).toFixed(2)}%`;

    };


    const normalizeLabel = (
        value
    ) => {

        if (!value) {
            return "-";
        }


        return String(value)
            .replaceAll("_", " ")
            .replace(
                /\b\w/g,
                (letter) =>
                    letter.toUpperCase()
            );

    };


    // =====================================================
    // DATA
    // =====================================================

    const totalContent =
        data?.total_content || 0;


    const cluster =
        data?.cluster || {};


    const clusterSummary =
        data?.cluster_summary || [];


    const aiInsight =
        data?.ai_insight || {};


    const forecast =
        data?.forecast || [];


    const forecastPerContent =
        data?.forecast_per_content || {};


    const bestContentNextWeek =
        data?.best_content_next_week || {};


    const strategy =
        data?.strategy || [];


    const distribution =
        cluster?.distribution || {};


    // =====================================================
    // DISTRIBUTION CHART
    // =====================================================

    const distributionData =
        useMemo(() => {

            return Object.entries(
                distribution
            ).map(
                (
                    [name, value]
                ) => ({
                    name,
                    value:
                        Number(value),
                })
            );

        }, [
            distribution,
        ]);


    // =====================================================
    // CLUSTER CHART
    // =====================================================

    const clusterChartData =
        useMemo(() => {

            return clusterSummary.map(
                (item) => ({
                    name:
                        item.cluster ||
                        "Cluster",

                    views:
                        Number(
                            item.average_views ||
                            0
                        ),

                    likes:
                        Number(
                            item.average_likes ||
                            0
                        ),

                    comments:
                        Number(
                            item.average_comments ||
                            0
                        ),

                    engagement:
                        Number(
                            item.average_engagement ||
                            0
                        ),
                })
            );

        }, [
            clusterSummary,
        ]);


    // =====================================================
    // FORECAST CHART
    // =====================================================

    const forecastChartData =
        useMemo(() => {

            return forecast.map(
                (item) => ({
                    day:
                        `Hari ${item.day}`,

                    engagement:
                        Number(
                            item.predicted_engagement ||
                            0
                        ),
                })
            );

        }, [
            forecast,
        ]);


    // =====================================================
    // CONTENT FORECAST
    // =====================================================

    const contentForecastData =
        useMemo(() => {

            return Object.entries(
                forecastPerContent
            ).map(
                (
                    [type, values]
                ) => {

                    const average =
                        values.length
                            ? values.reduce(
                                (
                                    total,
                                    value
                                ) =>
                                    total +
                                    Number(value || 0),
                                0
                            ) /
                              values.length
                            : 0;


                    return {
                        type,
                        average,
                    };

                }
            );

        }, [
            forecastPerContent,
        ]);


    // =====================================================
    // FILTER
    // =====================================================

    const applyFilter = () => {

        fetchAnalysis(true);

    };


    const resetFilter = () => {

        setMonth("");

        setYear("");


        setTimeout(
            () => {
                fetchAnalysis(true);
            },
            0
        );

    };


    // =====================================================
    // LOADING
    // =====================================================

    if (loading) {

        return (

            <div className="ai-analysis-loading">

                <div className="ai-analysis-spinner" />

                <span>
                    Menjalankan analisis AI...
                </span>

            </div>

        );

    }


    return (

        <div className="ai-analysis-page">

            {/* =================================================
                HEADER
            ================================================= */}

            <div className="ai-analysis-header">

                <div>

                    <div className="ai-analysis-breadcrumb">

                        <Brain
                            size={16}
                            strokeWidth={1.8}
                        />

                        <span>
                            Analisis AI
                        </span>

                    </div>


                    <h2>
                        Analisis Performa Konten
                    </h2>


                    <p>
                        Analisis otomatis menggunakan
                        K-Means++ dan forecasting untuk
                        menemukan pola performa konten.
                    </p>

                </div>


                <div className="ai-analysis-actions">

                    <div className="ai-filter-select">

                        <CalendarDays
                            size={15}
                        />

                        <select
                            value={month}
                            onChange={(event) =>
                                setMonth(
                                    event.target.value
                                )
                            }
                        >

                            <option value="">
                                Semua Bulan
                            </option>

                            <option value="1">
                                Januari
                            </option>

                            <option value="2">
                                Februari
                            </option>

                            <option value="3">
                                Maret
                            </option>

                            <option value="4">
                                April
                            </option>

                            <option value="5">
                                Mei
                            </option>

                            <option value="6">
                                Juni
                            </option>

                            <option value="7">
                                Juli
                            </option>

                            <option value="8">
                                Agustus
                            </option>

                            <option value="9">
                                September
                            </option>

                            <option value="10">
                                Oktober
                            </option>

                            <option value="11">
                                November
                            </option>

                            <option value="12">
                                Desember
                            </option>

                        </select>

                    </div>


                    <div className="ai-filter-select">

                        <select
                            value={year}
                            onChange={(event) =>
                                setYear(
                                    event.target.value
                                )
                            }
                        >

                            <option value="">
                                Semua Tahun
                            </option>

                            <option value="2026">
                                2026
                            </option>

                            <option value="2025">
                                2025
                            </option>

                            <option value="2024">
                                2024
                            </option>

                        </select>

                    </div>


                    <button
                        type="button"
                        className="ai-filter-button"
                        onClick={
                            applyFilter
                        }
                        disabled={
                            refreshing
                        }
                    >

                        <RefreshCw
                            size={14}
                            className={
                                refreshing
                                    ? "ai-spin"
                                    : ""
                            }
                        />

                        {refreshing
                            ? "Menganalisis..."
                            : "Analisis"}

                    </button>


                    {(month || year) && (

                        <button
                            type="button"
                            className="ai-reset-button"
                            onClick={
                                resetFilter
                            }
                        >
                            Reset
                        </button>

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
                        onClick={() =>
                            fetchAnalysis(true)
                        }
                    >
                        Coba lagi
                    </button>

                </div>

            )}


            {/* =================================================
                SUMMARY CARDS
            ================================================= */}

            <div className="ai-summary-grid">

                <AISummaryCard
                    icon={BarChart3}
                    label="Konten Dianalisis"
                    value={
                        formatNumber(
                            totalContent
                        )
                    }
                    description="Jumlah data yang diproses"
                />


                <AISummaryCard
                    icon={Target}
                    label="Jumlah Cluster"
                    value={
                        formatNumber(
                            cluster.cluster_count
                        )
                    }
                    description={
                        cluster.method ||
                        "K-Means++"
                    }
                />


                <AISummaryCard
                    icon={Brain}
                    label="Metode"
                    value={
                        cluster.method ||
                        "K-Means++"
                    }
                    description="Clustering performa konten"
                    compact
                />


                <AISummaryCard
                    icon={TrendingUp}
                    label="Prediksi Konten"
                    value={
                        normalizeLabel(
                            bestContentNextWeek.content_type
                        )
                    }
                    description="Potensi terbaik minggu depan"
                    compact
                />

            </div>


            {/* =================================================
                AI INSIGHT
            ================================================= */}

            <section className="ai-feature-panel">

                <div className="ai-feature-main">

                    <div className="ai-feature-icon">

                        <WandSparkles
                            size={21}
                            strokeWidth={1.8}
                        />

                    </div>


                    <div>

                        <span className="ai-eyebrow">
                            AI PERFORMANCE INSIGHT
                        </span>


                        <h3>
                            Insight Utama
                        </h3>


                        <p className="ai-feature-text">

                            {aiInsight.insight ||
                                "Belum terdapat insight."}

                        </p>

                    </div>

                </div>


                <div className="ai-feature-side">

                    <div className="ai-trend">

                        {aiInsight.trend === "Naik" ? (

                            <TrendingUp
                                size={17}
                            />

                        ) : aiInsight.trend === "Turun" ? (

                            <TrendingDown
                                size={17}
                            />

                        ) : (

                            <Clock3
                                size={17}
                            />

                        )}


                        <div>

                            <span>
                                Tren
                            </span>

                            <strong>
                                {
                                    aiInsight.trend ||
                                    "Stabil"
                                }
                            </strong>

                        </div>

                    </div>


                    <div className="ai-growth">

                        <span>
                            Perubahan
                        </span>

                        <strong>
                            {
                                formatPercentage(
                                    aiInsight.growth_percentage
                                )
                            }
                        </strong>

                    </div>

                </div>

            </section>


            {/* =================================================
                BEST CONTENT
            ================================================= */}

            <div className="ai-highlight-grid">

                <div className="ai-highlight-card">

                    <div className="ai-highlight-icon">
                        <CheckCircle2
                            size={18}
                        />
                    </div>


                    <div>

                        <span>
                            Konten Terbaik
                        </span>

                        <strong>
                            {
                                aiInsight.best_content ||
                                "-"
                            }
                        </strong>

                    </div>

                </div>


                <div className="ai-highlight-card">

                    <div className="ai-highlight-icon">
                        <Users
                            size={18}
                        />
                    </div>


                    <div>

                        <span>
                            Jenis Konten Unggul
                        </span>

                        <strong>
                            {
                                normalizeLabel(
                                    aiInsight.best_content_type
                                )
                            }
                        </strong>

                    </div>

                </div>


                <div className="ai-highlight-card">

                    <div className="ai-highlight-icon">
                        <TrendingUp
                            size={18}
                        />
                    </div>


                    <div>

                        <span>
                            Engagement Tertinggi
                        </span>

                        <strong>
                            {
                                formatNumber(
                                    aiInsight.best_engagement
                                )
                            }
                        </strong>

                    </div>

                </div>

            </div>


            {/* =================================================
                CLUSTER
            ================================================= */}

            <div className="ai-two-column">

                <section className="ai-panel">

                    <div className="ai-panel-header">

                        <div>

                            <span className="ai-eyebrow">
                                CLUSTER DISTRIBUTION
                            </span>

                            <h3>
                                Distribusi Cluster
                            </h3>

                        </div>

                        <div className="ai-panel-badge">
                            K-Means++
                        </div>

                    </div>


                    <div className="ai-distribution">

                        {distributionData.length === 0 ? (

                            <div className="ai-empty">
                                Belum terdapat hasil clustering.
                            </div>

                        ) : (

                            distributionData.map(
                                (
                                    item
                                ) => {

                                    const total =
                                        totalContent ||
                                        1;

                                    const percentage =
                                        (
                                            item.value /
                                            total
                                        ) *
                                        100;


                                    return (

                                        <div
                                            className="ai-distribution-row"
                                            key={
                                                item.name
                                            }
                                        >

                                            <div className="ai-distribution-top">

                                                <span>
                                                    {
                                                        item.name
                                                    }
                                                </span>

                                                <strong>
                                                    {
                                                        formatNumber(
                                                            item.value
                                                        )
                                                    }
                                                    {" "}
                                                    konten
                                                </strong>

                                            </div>


                                            <div className="ai-progress">

                                                <span
                                                    style={{
                                                        width: `${percentage}%`,
                                                    }}
                                                />

                                            </div>


                                            <div className="ai-distribution-percent">

                                                {
                                                    percentage.toFixed(
                                                        1
                                                    )
                                                }
                                                %

                                            </div>

                                        </div>

                                    );

                                }
                            )

                        )}

                    </div>

                </section>


                <section className="ai-panel">

                    <div className="ai-panel-header">

                        <div>

                            <span className="ai-eyebrow">
                                CLUSTER PERFORMANCE
                            </span>

                            <h3>
                                Rata-rata Performa
                            </h3>

                        </div>

                    </div>


                    <div className="ai-chart">

                        {clusterChartData.length === 0 ? (

                            <div className="ai-empty">
                                Belum terdapat data cluster.
                            </div>

                        ) : (

                            <ResponsiveContainer
                                width="100%"
                                height={260}
                            >

                                <BarChart
                                    data={
                                        clusterChartData
                                    }
                                    margin={{
                                        top: 10,
                                        right: 10,
                                        left: -18,
                                        bottom: 5,
                                    }}
                                >

                                    <CartesianGrid
                                        strokeDasharray="3 3"
                                        vertical={false}
                                    />

                                    <XAxis
                                        dataKey="name"
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{
                                            fontSize: 10,
                                        }}
                                    />

                                    <YAxis
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{
                                            fontSize: 10,
                                        }}
                                    />

                                    <Tooltip />

                                    <Bar
                                        dataKey="engagement"
                                        name="Engagement"
                                        radius={[
                                            6,
                                            6,
                                            0,
                                            0,
                                        ]}
                                        barSize={38}
                                    />

                                </BarChart>

                            </ResponsiveContainer>

                        )}

                    </div>

                </section>

            </div>


            {/* =================================================
                CLUSTER SUMMARY TABLE
            ================================================= */}

            <section className="ai-panel">

                <div className="ai-panel-header">

                    <div>

                        <span className="ai-eyebrow">
                            CLUSTER CHARACTERISTICS
                        </span>

                        <h3>
                            Karakteristik Cluster
                        </h3>

                    </div>

                </div>


                <div className="ai-table-wrapper">

                    {clusterSummary.length === 0 ? (

                        <div className="ai-empty">
                            Belum terdapat karakteristik cluster.
                        </div>

                    ) : (

                        <table className="ai-table">

                            <thead>

                                <tr>

                                    <th>
                                        Cluster
                                    </th>

                                    <th>
                                        Konten
                                    </th>

                                    <th>
                                        Avg. Views
                                    </th>

                                    <th>
                                        Avg. Likes
                                    </th>

                                    <th>
                                        Avg. Comments
                                    </th>

                                    <th>
                                        Avg. Engagement
                                    </th>

                                </tr>

                            </thead>


                            <tbody>

                                {clusterSummary.map(
                                    (
                                        item,
                                        index
                                    ) => (

                                        <tr
                                            key={
                                                `${item.cluster}-${index}`
                                            }
                                        >

                                            <td>

                                                <span className="ai-cluster-name">
                                                    {
                                                        item.cluster ||
                                                        "-"
                                                    }
                                                </span>

                                            </td>


                                            <td>
                                                {
                                                    formatNumber(
                                                        item.total_posts
                                                    )
                                                }
                                            </td>


                                            <td>
                                                {
                                                    formatDecimal(
                                                        item.average_views
                                                    )
                                                }
                                            </td>


                                            <td>
                                                {
                                                    formatDecimal(
                                                        item.average_likes
                                                    )
                                                }
                                            </td>


                                            <td>
                                                {
                                                    formatDecimal(
                                                        item.average_comments
                                                    )
                                                }
                                            </td>


                                            <td>

                                                <strong>
                                                    {
                                                        formatDecimal(
                                                            item.average_engagement
                                                        )
                                                    }
                                                </strong>

                                            </td>

                                        </tr>

                                    )
                                )}

                            </tbody>

                        </table>

                    )}

                </div>

            </section>


            {/* =================================================
                FORECAST
            ================================================= */}

            <div className="ai-two-column">

                <section className="ai-panel">

                    <div className="ai-panel-header">

                        <div>

                            <span className="ai-eyebrow">
                                FORECASTING
                            </span>

                            <h3>
                                Prediksi Engagement 7 Hari
                            </h3>

                        </div>

                        <div className="ai-panel-icon">
                            <TrendingUp
                                size={17}
                            />
                        </div>

                    </div>


                    <div className="ai-chart">

                        {forecastChartData.length === 0 ? (

                            <div className="ai-empty">
                                Data belum cukup untuk melakukan forecasting.
                            </div>

                        ) : (

                            <ResponsiveContainer
                                width="100%"
                                height={270}
                            >

                                <LineChart
                                    data={
                                        forecastChartData
                                    }
                                    margin={{
                                        top: 10,
                                        right: 10,
                                        left: -18,
                                        bottom: 5,
                                    }}
                                >

                                    <CartesianGrid
                                        strokeDasharray="3 3"
                                        vertical={false}
                                    />

                                    <XAxis
                                        dataKey="day"
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{
                                            fontSize: 10,
                                        }}
                                    />

                                    <YAxis
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{
                                            fontSize: 10,
                                        }}
                                    />

                                    <Tooltip />

                                    <Line
                                        type="monotone"
                                        dataKey="engagement"
                                        name="Prediksi Engagement"
                                        strokeWidth={2}
                                        dot={{
                                            r: 3,
                                        }}
                                    />

                                </LineChart>

                            </ResponsiveContainer>

                        )}

                    </div>

                </section>


                <section className="ai-panel">

                    <div className="ai-panel-header">

                        <div>

                            <span className="ai-eyebrow">
                                CONTENT FORECAST
                            </span>

                            <h3>
                                Prediksi per Jenis Konten
                            </h3>

                        </div>

                    </div>


                    <div className="ai-content-forecast">

                        {contentForecastData.length === 0 ? (

                            <div className="ai-empty">
                                Belum cukup data per jenis konten.
                            </div>

                        ) : (

                            contentForecastData.map(
                                (
                                    item
                                ) => (

                                    <div
                                        className="ai-content-forecast-item"
                                        key={
                                            item.type
                                        }
                                    >

                                        <div>

                                            <span>
                                                {
                                                    normalizeLabel(
                                                        item.type
                                                    )
                                                }
                                            </span>

                                            <strong>
                                                {
                                                    formatDecimal(
                                                        item.average
                                                    )
                                                }
                                            </strong>

                                        </div>


                                        <span className="ai-forecast-label">
                                            rata-rata prediksi
                                        </span>

                                    </div>

                                )
                            )

                        )}

                    </div>

                </section>

            </div>


            {/* =================================================
                NEXT WEEK
            ================================================= */}

            <section className="ai-next-week">

                <div className="ai-next-week-icon">

                    <Target
                        size={21}
                    />

                </div>


                <div className="ai-next-week-content">

                    <span className="ai-eyebrow">
                        BEST CONTENT NEXT WEEK
                    </span>

                    <h3>
                        {
                            normalizeLabel(
                                bestContentNextWeek.content_type
                            )
                        }
                    </h3>

                    <p>
                        Rata-rata prediksi engagement:
                        {" "}
                        <strong>
                            {
                                formatDecimal(
                                    bestContentNextWeek.average_prediction
                                )
                            }
                        </strong>
                    </p>

                </div>

            </section>


            {/* =================================================
                PREDICTION
            ================================================= */}

            {aiInsight.prediction && (

                <section className="ai-prediction-panel">

                    <div className="ai-prediction-icon">

                        <TrendingUp
                            size={19}
                        />

                    </div>


                    <div>

                        <span className="ai-eyebrow">
                            PREDICTION
                        </span>

                        <p>
                            {
                                aiInsight.prediction
                            }
                        </p>

                    </div>

                </section>

            )}


            {/* =================================================
                STRATEGY
            ================================================= */}

            <section className="ai-panel">

                <div className="ai-panel-header">

                    <div>

                        <span className="ai-eyebrow">
                            AUTO STRATEGY RECOMMENDATION
                        </span>

                        <h3>
                            Rekomendasi Strategi
                        </h3>

                    </div>

                    <Lightbulb
                        size={18}
                        strokeWidth={1.8}
                    />

                </div>


                <div className="ai-strategy-list">

                    {strategy.length === 0 ? (

                        <div className="ai-empty">
                            Belum terdapat rekomendasi strategi.
                        </div>

                    ) : (

                        strategy.map(
                            (
                                item,
                                index
                            ) => (

                                <div
                                    className="ai-strategy-item"
                                    key={
                                        index
                                    }
                                >

                                    <div className="ai-strategy-number">
                                        {
                                            String(
                                                index + 1
                                            ).padStart(
                                                2,
                                                "0"
                                            )
                                        }
                                    </div>


                                    <p>
                                        {item}
                                    </p>

                                </div>

                            )
                        )

                    )}

                </div>

            </section>

        </div>

    );

}


// =========================================================
// SUMMARY CARD
// =========================================================

function AISummaryCard({
    icon: Icon,
    label,
    value,
    description,
    compact = false,
}) {

    return (

        <div className="ai-summary-card">

            <div className="ai-summary-top">

                <div className="ai-summary-icon">

                    <Icon
                        size={18}
                        strokeWidth={1.8}
                    />

                </div>

            </div>


            <span className="ai-summary-label">
                {label}
            </span>


            <strong
                className={
                    compact
                        ? "ai-summary-value compact"
                        : "ai-summary-value"
                }
            >
                {value}
            </strong>


            <p>
                {description}
            </p>

        </div>

    );

}