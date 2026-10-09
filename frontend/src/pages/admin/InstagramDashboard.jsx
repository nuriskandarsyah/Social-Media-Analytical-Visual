import React, {
    useCallback,
    useEffect,
    useMemo,
    useState,
} from "react";

import * as api from "../../services/api";


// =========================================================
// ICON
// =========================================================

function Icon({
    type,
    size = 20,
}) {

    const common = {
        width: size,
        height: size,
        viewBox: "0 0 24 24",
        fill: "none",
        stroke: "currentColor",
        strokeWidth: 1.8,
        strokeLinecap: "round",
        strokeLinejoin: "round",
    };


    if (type === "eye") {
        return (
            <svg {...common}>
                <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z" />
                <circle cx="12" cy="12" r="2.5" />
            </svg>
        );
    }


    if (type === "users") {
        return (
            <svg {...common}>
                <circle cx="9" cy="7" r="3" />
                <path d="M3 21v-2a6 6 0 0 1 12 0v2" />
                <path d="M16 4.5a3 3 0 0 1 0 5.8" />
                <path d="M19 21v-2a6 6 0 0 0-3-5.2" />
            </svg>
        );
    }


    if (type === "heart") {
        return (
            <svg {...common}>
                <path d="M20.8 8.8c0 5.5-8.8 10.2-8.8 10.2S3.2 14.3 3.2 8.8A4.8 4.8 0 0 1 12 6.2a4.8 4.8 0 0 1 8.8 2.6Z" />
            </svg>
        );
    }


    if (type === "user") {
        return (
            <svg {...common}>
                <circle cx="12" cy="8" r="4" />
                <path d="M4 21a8 8 0 0 1 16 0" />
            </svg>
        );
    }


    if (type === "message") {
        return (
            <svg {...common}>
                <path d="M20 11.5a7.5 7.5 0 0 1-7.8 7.5H7l-4 2v-5.2A7.5 7.5 0 1 1 20 11.5Z" />
            </svg>
        );
    }


    if (type === "calendar") {
        return (
            <svg {...common}>
                <rect x="3" y="4" width="18" height="17" rx="2" />
                <path d="M16 2v4M8 2v4M3 10h18" />
            </svg>
        );
    }


    if (type === "refresh") {
        return (
            <svg {...common}>
                <path d="M20 11a8 8 0 0 0-14.8-4L3 9" />
                <path d="M3 4v5h5" />
                <path d="M4 13a8 8 0 0 0 14.8 4L21 15" />
                <path d="M21 20v-5h-5" />
            </svg>
        );
    }


    if (type === "chart") {
        return (
            <svg {...common}>
                <path d="M4 19V5" />
                <path d="M4 19h16" />
                <path d="m7 15 3-4 3 2 5-7" />
            </svg>
        );
    }


    if (type === "trend") {
        return (
            <svg {...common}>
                <path d="m4 16 5-5 3 3 7-8" />
                <path d="M14 6h5v5" />
            </svg>
        );
    }


    if (type === "target") {
        return (
            <svg {...common}>
                <circle cx="12" cy="12" r="8" />
                <circle cx="12" cy="12" r="4" />
                <circle cx="12" cy="12" r="1" />
            </svg>
        );
    }


    return (
        <svg {...common}>
            <circle cx="12" cy="12" r="9" />
        </svg>
    );
}


// =========================================================
// FORMAT NUMBER
// =========================================================

function formatNumber(value) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "0";
    }


    const number = Number(value);


    if (Number.isNaN(number)) {
        return String(value);
    }


    return new Intl.NumberFormat(
        "id-ID"
    ).format(number);
}


// =========================================================
// FORMAT PERCENT
// =========================================================

function formatPercent(value) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "0%";
    }


    const number = Number(value);


    if (Number.isNaN(number)) {
        return `${value}%`;
    }


    return `${number.toFixed(0)}%`;
}


// =========================================================
// SAFE NUMBER
// =========================================================

function numberValue(...values) {

    for (const value of values) {

        if (
            value !== null &&
            value !== undefined &&
            value !== ""
        ) {

            const number = Number(value);

            if (!Number.isNaN(number)) {
                return number;
            }
        }
    }

    return 0;
}


// =========================================================
// METRIC CARD
// =========================================================

function MetricCard({
    title,
    value,
    icon,
    suffix = "",
    description = "Berdasarkan data MAVis",
}) {

    return (
        <div
            className="
                bg-white
                border
                border-slate-200
                rounded-2xl
                p-5
                min-h-[145px]
                shadow-sm
                hover:shadow-md
                transition
            "
        >

            <div
                className="
                    flex
                    items-start
                    justify-between
                "
            >

                <div>

                    <p
                        className="
                            text-sm
                            text-slate-500
                            mb-2
                        "
                    >
                        {title}
                    </p>


                    <div
                        className="
                            text-3xl
                            font-bold
                            text-slate-900
                        "
                    >
                        {value}
                        {suffix}
                    </div>

                </div>


                <div
                    className="
                        w-11
                        h-11
                        rounded-xl
                        bg-slate-100
                        text-slate-600
                        flex
                        items-center
                        justify-center
                    "
                >
                    <Icon
                        type={icon}
                        size={22}
                    />
                </div>

            </div>


            <div
                className="
                    flex
                    items-center
                    gap-1.5
                    mt-5
                    text-xs
                    text-slate-400
                "
            >

                <Icon
                    type="trend"
                    size={13}
                />

                <span>
                    {description}
                </span>

            </div>

        </div>
    );
}


// =========================================================
// EMPTY STATE
// =========================================================

function EmptyState({
    children = "Belum ada data.",
}) {

    return (
        <div
            className="
                py-10
                text-center
                text-sm
                text-slate-400
            "
        >
            {children}
        </div>
    );
}


// =========================================================
// DASHBOARD
// =========================================================

export default function InstagramDashboard() {

    // =====================================================
    // STATE
    // =====================================================

    const [
        dashboard,
        setDashboard,
    ] = useState(null);


    const [
        loading,
        setLoading,
    ] = useState(true);


    const [
        error,
        setError,
    ] = useState("");


    const [
        selectedMonth,
        setSelectedMonth,
    ] = useState("");


    const [
        selectedYear,
        setSelectedYear,
    ] = useState("");


    // =====================================================
    // YEAR
    // =====================================================

    const years = useMemo(() => {

        const currentYear =
            new Date().getFullYear();


        return Array.from(
            {
                length: 6,
            },
            (_, index) =>
                currentYear - index
        );

    }, []);


    // =====================================================
    // MONTH
    // =====================================================

    const months = [
        {
            value: "",
            label: "Semua Bulan",
        },
        {
            value: "1",
            label: "Januari",
        },
        {
            value: "2",
            label: "Februari",
        },
        {
            value: "3",
            label: "Maret",
        },
        {
            value: "4",
            label: "April",
        },
        {
            value: "5",
            label: "Mei",
        },
        {
            value: "6",
            label: "Juni",
        },
        {
            value: "7",
            label: "Juli",
        },
        {
            value: "8",
            label: "Agustus",
        },
        {
            value: "9",
            label: "September",
        },
        {
            value: "10",
            label: "Oktober",
        },
        {
            value: "11",
            label: "November",
        },
        {
            value: "12",
            label: "Desember",
        },
    ];


    // =====================================================
    // FETCH DASHBOARD
    // =====================================================

    const fetchDashboard = useCallback(
        async () => {

            try {

                setLoading(true);

                setError("");


                console.log(
                    "================================"
                );

                console.log(
                    "DASHBOARD REQUEST"
                );


                let endpoint =
                    "/api/dashboard/";


                const params =
                    new URLSearchParams();


                if (selectedMonth) {

                    params.append(
                        "month",
                        selectedMonth
                    );

                }


                if (selectedYear) {

                    params.append(
                        "year",
                        selectedYear
                    );

                }


                const query =
                    params.toString();


                if (query) {

                    endpoint +=
                        `?${query}`;

                }


                console.log(
                    "Endpoint:",
                    endpoint
                );


                console.log(
                    "JWT tersedia:",
                    Boolean(
                        localStorage.getItem(
                            "access_token"
                        )
                    )
                );


                const result =
                    await api.get(
                        endpoint
                    );


                // =================================================
                // DEBUG RESPONSE
                // =================================================

                console.log(
                    "FULL DASHBOARD DATA:",
                    JSON.stringify(
                        result,
                        null,
                        2
                    )
                );


                console.log(
                    "Dashboard response:",
                    result
                );


                setDashboard(
                    result
                );


            } catch (err) {

                console.error(
                    "Dashboard error:",
                    err
                );


                setDashboard(null);


                setError(
                    err?.message ||
                    "Data dashboard gagal diambil"
                );


            } finally {

                setLoading(false);

            }

        },
        [
            selectedMonth,
            selectedYear,
        ]
    );


    // =====================================================
    // INITIAL LOAD
    // =====================================================

    useEffect(() => {

        fetchDashboard();

    }, [
        fetchDashboard,
    ]);


    // =====================================================
    // NORMALIZE DATA
    // =====================================================

    const data =
        dashboard?.data ||
        dashboard ||
        {};


    // =====================================================
    // METRICS
    // =====================================================

    const metrics =
        data?.metrics ||
        data?.summary ||
        data?.overview ||
        {};


    const views =
        numberValue(
            metrics?.views,
            metrics?.total_views,
            data?.views,
            data?.total_views
        );


    const reach =
        numberValue(
            metrics?.reach,
            metrics?.total_reach,
            data?.reach,
            data?.total_reach
        );


    const engagement =
        numberValue(
            metrics?.engagement_rate,
            metrics?.engagement,
            data?.engagement_rate,
            data?.engagement
        );


    const followers =
        numberValue(
            metrics?.followers,
            metrics?.total_followers,
            data?.followers,
            data?.total_followers
        );


    const profileViews =
        numberValue(
            metrics?.profile_views,
            data?.profile_views,
            data?.account_metrics?.profile_views
        );


    const contentInteraction =
        numberValue(
            metrics?.content_interaction,
            metrics?.content_interactions,
            metrics?.interactions,
            data?.content_interaction,
            data?.content_interactions,
            data?.interactions
        );


    // =====================================================
    // FORECAST
    // =====================================================

    const forecast =
        data?.forecast_data ||
        data?.forecasts ||
        data?.forecast ||
        [];

    const forecastList =
        Array.isArray(forecast)
            ? forecast
            : (
                forecast?.data ||
                []
            );


    // =====================================================
    // CLUSTER
    // =====================================================

    const clusters =
        data?.clusters ||
        data?.cluster ||
        [];


    const clusterList =
        Array.isArray(clusters)
            ? clusters
            : (
                clusters?.data ||
                []
            );


    // =====================================================
    // POSTS
    // =====================================================

    const posts =
        data?.posts ||
        data?.recent_posts ||
        [];


    const postList =
        Array.isArray(posts)
            ? posts
            : (
                posts?.data ||
                []
            );


    // =====================================================
    // RENDER
    // =====================================================

    return (

        /*
         * PENTING:
         * Tidak ada <MainLayout> di sini.
         *
         * MainLayout sudah dipasang di AppRoutes.jsx.
         */

        <div
            className="
                w-full
                max-w-[1400px]
                mx-auto
                px-6
                py-6
            "
        >

            {/* =================================================
                HEADER
            ================================================= */}

            <div
                className="
                    flex
                    flex-col
                    lg:flex-row
                    lg:items-end
                    lg:justify-between
                    gap-5
                    mb-6
                "
            >

                <div>

                    <div
                        className="
                            flex
                            items-center
                            gap-2
                            text-sm
                            text-slate-400
                            mb-2
                        "
                    >

                        <Icon
                            type="chart"
                            size={17}
                        />

                        <span>
                            Dashboard
                        </span>

                    </div>


                    <h1
                        className="
                            text-4xl
                            font-bold
                            tracking-tight
                            text-slate-900
                        "
                    >
                        Overview
                    </h1>


                    <p
                        className="
                            mt-1
                            text-sm
                            text-slate-500
                        "
                    >
                        Ringkasan performa media sosial MAVis.
                    </p>

                </div>


                {/* =================================================
                    FILTER
                ================================================= */}

                <div
                    className="
                        flex
                        flex-col
                        sm:flex-row
                        gap-3
                    "
                >

                    <div
                        className="
                            relative
                            min-w-[170px]
                        "
                    >

                        <div
                            className="
                                absolute
                                left-4
                                top-1/2
                                -translate-y-1/2
                                text-slate-400
                                pointer-events-none
                            "
                        >

                            <Icon
                                type="calendar"
                                size={17}
                            />

                        </div>


                        <select
                            value={
                                selectedMonth
                            }
                            onChange={
                                event =>
                                    setSelectedMonth(
                                        event.target.value
                                    )
                            }
                            className="
                                w-full
                                appearance-none
                                bg-white
                                border
                                border-slate-200
                                rounded-xl
                                px-11
                                py-3
                                text-sm
                                text-slate-700
                                outline-none
                                focus:border-slate-400
                            "
                        >

                            {months.map(
                                month => (

                                    <option
                                        key={
                                            month.value
                                        }
                                        value={
                                            month.value
                                        }
                                    >
                                        {
                                            month.label
                                        }
                                    </option>

                                )
                            )}

                        </select>

                    </div>


                    <select
                        value={
                            selectedYear
                        }
                        onChange={
                            event =>
                                setSelectedYear(
                                    event.target.value
                                )
                        }
                        className="
                            min-w-[150px]
                            bg-white
                            border
                            border-slate-200
                            rounded-xl
                            px-4
                            py-3
                            text-sm
                            text-slate-700
                            outline-none
                            focus:border-slate-400
                        "
                    >

                        <option value="">
                            Semua Tahun
                        </option>


                        {years.map(
                            year => (

                                <option
                                    key={year}
                                    value={year}
                                >
                                    {year}
                                </option>

                            )
                        )}

                    </select>


                    <button
                        type="button"
                        onClick={
                            fetchDashboard
                        }
                        disabled={
                            loading
                        }
                        className="
                            min-w-[125px]
                            bg-slate-950
                            text-white
                            rounded-xl
                            px-5
                            py-3
                            text-sm
                            font-semibold
                            flex
                            items-center
                            justify-center
                            gap-2
                            hover:bg-slate-800
                            disabled:opacity-60
                            disabled:cursor-not-allowed
                            transition
                        "
                    >

                        <Icon
                            type="refresh"
                            size={17}
                        />

                        <span>
                            {loading
                                ? "Memuat..."
                                : "Terapkan"
                            }
                        </span>

                    </button>

                </div>

            </div>


            {/* =================================================
                ERROR
            ================================================= */}

            {error && (

                <div
                    className="
                        mb-6
                        border
                        border-red-200
                        bg-red-50
                        rounded-xl
                        px-5
                        py-4
                        flex
                        items-center
                        justify-between
                        gap-4
                    "
                >

                    <div>

                        <p
                            className="
                                text-sm
                                font-semibold
                                text-red-600
                            "
                        >
                            Data dashboard gagal diambil
                        </p>


                        <p
                            className="
                                text-xs
                                text-red-500
                                mt-1
                            "
                        >
                            {error}
                        </p>

                    </div>


                    <button
                        type="button"
                        onClick={
                            fetchDashboard
                        }
                        className="
                            text-sm
                            font-semibold
                            text-red-600
                            hover:underline
                            whitespace-nowrap
                        "
                    >
                        Coba lagi
                    </button>

                </div>

            )}


            {/* =================================================
                LOADING
            ================================================= */}

            {loading && !dashboard ? (

                <div
                    className="
                        grid
                        grid-cols-1
                        md:grid-cols-2
                        xl:grid-cols-3
                        gap-5
                    "
                >

                    {[1, 2, 3, 4, 5, 6].map(
                        item => (

                            <div
                                key={item}
                                className="
                                    h-[145px]
                                    bg-white
                                    border
                                    border-slate-200
                                    rounded-2xl
                                    animate-pulse
                                "
                            />

                        )
                    )}

                </div>

            ) : (

                <>

                    {/* =================================================
                        METRIC CARDS
                    ================================================= */}

                    <div
                        className="
                            grid
                            grid-cols-1
                            md:grid-cols-2
                            xl:grid-cols-3
                            gap-5
                        "
                    >

                        <MetricCard
                            title="Views"
                            value={
                                formatNumber(
                                    views
                                )
                            }
                            icon="eye"
                        />


                        <MetricCard
                            title="Reach"
                            value={
                                formatNumber(
                                    reach
                                )
                            }
                            icon="users"
                        />


                        <MetricCard
                            title="Engagement"
                            value={
                                formatPercent(
                                    engagement
                                )
                            }
                            icon="heart"
                        />


                        <MetricCard
                            title="Followers"
                            value={
                                formatNumber(
                                    followers
                                )
                            }
                            icon="user"
                        />


                        <MetricCard
                            title="Profile Views"
                            value={
                                formatNumber(
                                    profileViews
                                )
                            }
                            icon="user"
                        />


                        <MetricCard
                            title="Content Interaction"
                            value={
                                formatNumber(
                                    contentInteraction
                                )
                            }
                            icon="message"
                        />

                    </div>


                    {/* =================================================
                        FORECAST + CLUSTER
                    ================================================= */}

                    <div
                        className="
                            grid
                            grid-cols-1
                            xl:grid-cols-2
                            gap-5
                            mt-6
                        "
                    >

                        {/* =================================================
                            FORECAST
                        ================================================= */}

                        <div
                            className="
                                bg-white
                                border
                                border-slate-200
                                rounded-2xl
                                shadow-sm
                                overflow-hidden
                            "
                        >

                            <div
                                className="
                                    px-5
                                    py-4
                                    border-b
                                    border-slate-100
                                    flex
                                    items-center
                                    justify-between
                                "
                            >

                                <div>

                                    <h2
                                        className="
                                            font-semibold
                                            text-slate-900
                                        "
                                    >
                                        Forecast
                                    </h2>


                                    <p
                                        className="
                                            text-xs
                                            text-slate-400
                                            mt-1
                                        "
                                    >
                                        Prediksi performa konten.
                                    </p>

                                </div>


                                <div
                                    className="
                                        w-10
                                        h-10
                                        rounded-xl
                                        bg-slate-100
                                        text-slate-600
                                        flex
                                        items-center
                                        justify-center
                                    "
                                >
                                    <Icon
                                        type="trend"
                                        size={20}
                                    />
                                </div>

                            </div>


                            <div className="p-5">

                                {forecastList.length === 0 ? (

                                    <EmptyState>
                                        Belum ada data forecast.
                                    </EmptyState>

                                ) : (

                                    <div className="space-y-3">

                                        {forecastList
                                            .slice(0, 10)
                                            .map(
                                                (
                                                    item,
                                                    index
                                                ) => {

                                                    const label =
                                                         item?.forecast_date ||
                                                         item?.date ||
                                                         item?.period ||
                                                         item?.month ||
                                                         `Periode ${index + 1}`;

                                                     const value =
                                                         numberValue(
                                                             item?.predicted_engagement,
                                                             item?.prediction,
                                                             item?.predicted,
                                                             item?.forecast,
                                                             item?.value
                                                         );


                                                    return (

                                                        <div
                                                            key={index}
                                                            className="
                                                                flex
                                                                items-center
                                                                justify-between
                                                                gap-4
                                                                py-2
                                                            "
                                                        >

                                                            <span
                                                                className="
                                                                    text-sm
                                                                    text-slate-600
                                                                "
                                                            >
                                                                {label}
                                                            </span>


                                                            <span
                                                                className="
                                                                    text-sm
                                                                    font-semibold
                                                                    text-slate-900
                                                                "
                                                            >
                                                                {
                                                                    formatNumber(
                                                                        value
                                                                    )
                                                                }
                                                            </span>

                                                        </div>

                                                    );

                                                }
                                            )}

                                    </div>

                                )}

                            </div>

                        </div>


                        {/* =================================================
                            CLUSTER
                        ================================================= */}

                        <div
                            className="
                                bg-white
                                border
                                border-slate-200
                                rounded-2xl
                                shadow-sm
                                overflow-hidden
                            "
                        >

                            <div
                                className="
                                    px-5
                                    py-4
                                    border-b
                                    border-slate-100
                                    flex
                                    items-center
                                    justify-between
                                "
                            >

                                <div>

                                    <h2
                                        className="
                                            font-semibold
                                            text-slate-900
                                        "
                                    >
                                        Cluster Konten
                                    </h2>


                                    <p
                                        className="
                                            text-xs
                                            text-slate-400
                                            mt-1
                                        "
                                    >
                                        Pengelompokan performa konten.
                                    </p>

                                </div>


                                <div
                                    className="
                                        w-10
                                        h-10
                                        rounded-xl
                                        bg-slate-100
                                        text-slate-600
                                        flex
                                        items-center
                                        justify-center
                                    "
                                >
                                    <Icon
                                        type="target"
                                        size={20}
                                    />
                                </div>

                            </div>


                            <div className="p-5">

                                {clusterList.length === 0 ? (

                                    <EmptyState>
                                        Belum ada data cluster.
                                    </EmptyState>

                                ) : (

                                    <div
                                        className="
                                            grid
                                            grid-cols-1
                                            sm:grid-cols-2
                                            gap-3
                                        "
                                    >

                                        {clusterList
                                            .slice(0, 6)
                                            .map(
                                                (
                                                    item,
                                                    index
                                                ) => {

                                                    const name =
                                                        item?.name ||
                                                        item?.cluster_name ||
                                                        item?.label ||
                                                        `Cluster ${index + 1}`;


                                                    const count =
                                                        numberValue(
                                                            item?.count,
                                                            item?.total,
                                                            item?.total_posts,
                                                            item?.posts
                                                        );


                                                    return (

                                                        <div
                                                            key={index}
                                                            className="
                                                                border
                                                                border-slate-100
                                                                bg-slate-50
                                                                rounded-xl
                                                                p-4
                                                            "
                                                        >

                                                            <p
                                                                className="
                                                                    text-sm
                                                                    font-semibold
                                                                    text-slate-800
                                                                "
                                                            >
                                                                {name}
                                                            </p>


                                                            <p
                                                                className="
                                                                    text-xs
                                                                    text-slate-400
                                                                    mt-1
                                                                "
                                                            >
                                                                {
                                                                    formatNumber(
                                                                        count
                                                                    )
                                                                }{" "}
                                                                konten
                                                            </p>

                                                        </div>

                                                    );

                                                }
                                            )}

                                    </div>

                                )}

                            </div>

                        </div>

                    </div>


                    {/* =================================================
                        RECENT POSTS
                    ================================================= */}

                    <div
                        className="
                            bg-white
                            border
                            border-slate-200
                            rounded-2xl
                            shadow-sm
                            overflow-hidden
                            mt-6
                        "
                    >

                        <div
                            className="
                                px-5
                                py-4
                                border-b
                                border-slate-100
                                flex
                                items-center
                                justify-between
                            "
                        >

                            <div>

                                <h2
                                    className="
                                        font-semibold
                                        text-slate-900
                                    "
                                >
                                    Ringkasan Konten
                                </h2>


                                <p
                                    className="
                                        text-xs
                                        text-slate-400
                                        mt-1
                                    "
                                >
                                    Data konten terbaru MAVis.
                                </p>

                            </div>


                            <div
                                className="
                                    w-10
                                    h-10
                                    rounded-xl
                                    bg-slate-100
                                    text-slate-600
                                    flex
                                    items-center
                                    justify-center
                                "
                            >
                                <Icon
                                    type="chart"
                                    size={20}
                                />
                            </div>

                        </div>


                        <div className="p-5">

                            {postList.length === 0 ? (

                                <EmptyState>
                                    Belum ada data konten.
                                </EmptyState>

                            ) : (

                                <div className="overflow-x-auto">

                                    <table
                                        className="
                                            w-full
                                            text-sm
                                        "
                                    >

                                        <thead>

                                            <tr
                                                className="
                                                    border-b
                                                    border-slate-100
                                                    text-left
                                                "
                                            >

                                                <th
                                                    className="
                                                        py-3
                                                        px-3
                                                        font-medium
                                                        text-slate-400
                                                    "
                                                >
                                                    Konten
                                                </th>


                                                <th
                                                    className="
                                                        py-3
                                                        px-3
                                                        font-medium
                                                        text-slate-400
                                                    "
                                                >
                                                    Views
                                                </th>


                                                <th
                                                    className="
                                                        py-3
                                                        px-3
                                                        font-medium
                                                        text-slate-400
                                                    "
                                                >
                                                    Reach
                                                </th>


                                                <th
                                                    className="
                                                        py-3
                                                        px-3
                                                        font-medium
                                                        text-slate-400
                                                    "
                                                >
                                                    Engagement
                                                </th>

                                            </tr>

                                        </thead>


                                        <tbody>

                                            {postList
                                                .slice(0, 10)
                                                .map(
                                                    (
                                                        post,
                                                        index
                                                    ) => {

                                                        const title =
                                                            post?.caption ||
                                                            post?.title ||
                                                            post?.content ||
                                                            post?.id ||
                                                            `Konten ${index + 1}`;


                                                        const postViews =
                                                            numberValue(
                                                                post?.views,
                                                                post?.view_count
                                                            );


                                                        const postReach =
                                                            numberValue(
                                                                post?.reach,
                                                                post?.reach_count
                                                            );


                                                        const postEngagement =
                                                            numberValue(
                                                                post?.engagement_rate,
                                                                post?.engagement
                                                            );


                                                        return (

                                                            <tr
                                                                key={
                                                                    post?.id ||
                                                                    index
                                                                }
                                                                className="
                                                                    border-b
                                                                    border-slate-50
                                                                    last:border-0
                                                                "
                                                            >

                                                                <td
                                                                    className="
                                                                        py-3
                                                                        px-3
                                                                        max-w-[420px]
                                                                    "
                                                                >

                                                                    <div
                                                                        className="
                                                                            truncate
                                                                            text-slate-700
                                                                        "
                                                                    >
                                                                        {title}
                                                                    </div>

                                                                </td>


                                                                <td
                                                                    className="
                                                                        py-3
                                                                        px-3
                                                                        text-slate-600
                                                                    "
                                                                >
                                                                    {
                                                                        formatNumber(
                                                                            postViews
                                                                        )
                                                                    }
                                                                </td>


                                                                <td
                                                                    className="
                                                                        py-3
                                                                        px-3
                                                                        text-slate-600
                                                                    "
                                                                >
                                                                    {
                                                                        formatNumber(
                                                                            postReach
                                                                        )
                                                                    }
                                                                </td>


                                                                <td
                                                                    className="
                                                                        py-3
                                                                        px-3
                                                                        text-slate-600
                                                                    "
                                                                >
                                                                    {
                                                                        formatPercent(
                                                                            postEngagement
                                                                        )
                                                                    }
                                                                </td>

                                                            </tr>

                                                        );

                                                    }
                                                )}

                                        </tbody>

                                    </table>

                                </div>

                            )}

                        </div>

                    </div>


                    {/* =================================================
                        RAW SUMMARY
                    ================================================= */}

                    <div
                        className="
                            grid
                            grid-cols-1
                            sm:grid-cols-2
                            lg:grid-cols-4
                            gap-4
                            mt-6
                        "
                    >

                        <div
                            className="
                                bg-white
                                border
                                border-slate-200
                                rounded-xl
                                p-4
                            "
                        >

                            <p
                                className="
                                    text-xs
                                    text-slate-400
                                "
                            >
                                Total Konten
                            </p>


                            <p
                                className="
                                    text-xl
                                    font-bold
                                    text-slate-900
                                    mt-1
                                "
                            >
                                {
                                    formatNumber(
                                        numberValue(
                                            data?.total_posts,
                                            data?.total_content,
                                            data?.post_count,
                                            postList.length
                                        )
                                    )
                                }
                            </p>

                        </div>


                        <div
                            className="
                                bg-white
                                border
                                border-slate-200
                                rounded-xl
                                p-4
                            "
                        >

                            <p
                                className="
                                    text-xs
                                    text-slate-400
                                "
                            >
                                Total Followers
                            </p>


                            <p
                                className="
                                    text-xl
                                    font-bold
                                    text-slate-900
                                    mt-1
                                "
                            >
                                {
                                    formatNumber(
                                        followers
                                    )
                                }
                            </p>

                        </div>


                        <div
                            className="
                                bg-white
                                border
                                border-slate-200
                                rounded-xl
                                p-4
                            "
                        >

                            <p
                                className="
                                    text-xs
                                    text-slate-400
                                "
                            >
                                Total Reach
                            </p>


                            <p
                                className="
                                    text-xl
                                    font-bold
                                    text-slate-900
                                    mt-1
                                "
                            >
                                {
                                    formatNumber(
                                        reach
                                    )
                                }
                            </p>

                        </div>


                        <div
                            className="
                                bg-white
                                border
                                border-slate-200
                                rounded-xl
                                p-4
                            "
                        >

                            <p
                                className="
                                    text-xs
                                    text-slate-400
                                "
                            >
                                Engagement Rate
                            </p>


                            <p
                                className="
                                    text-xl
                                    font-bold
                                    text-slate-900
                                    mt-1
                                "
                            >
                                {
                                    formatPercent(
                                        engagement
                                    )
                                }
                            </p>

                        </div>

                    </div>

                </>

            )}

        </div>

    );
}