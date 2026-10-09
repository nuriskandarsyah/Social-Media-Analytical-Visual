import {
    useCallback,
    useEffect,
    useState,
} from "react";

import {
    Bar,
    BarChart,
    CartesianGrid,
    Cell,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";

import {
    useLocation,
    useNavigate,
} from "react-router-dom";

import * as api from "../../services/api";


// =====================================================
// GENERIC SVG ICON
// =====================================================

function MetaIcon({
    type,
    size = 20,
    className = "",
    strokeWidth = 1.8,
}) {
    const common = {
        width: size,
        height: size,
        viewBox: "0 0 24 24",
        fill: "none",
        xmlns: "http://www.w3.org/2000/svg",
        className,
        "aria-hidden": true,
    };

    switch (type) {
        case "instagram":
            return (
                <svg
                    {...common}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                >
                    <rect
                        x="3"
                        y="3"
                        width="18"
                        height="18"
                        rx="5"
                    />

                    <circle
                        cx="12"
                        cy="12"
                        r="4"
                    />

                    <circle
                        cx="17.5"
                        cy="6.5"
                        r="1"
                        fill="currentColor"
                        stroke="none"
                    />
                </svg>
            );

        case "eye":
            return (
                <svg
                    {...common}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                >
                    <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z" />

                    <circle
                        cx="12"
                        cy="12"
                        r="2.8"
                    />
                </svg>
            );

        case "heart":
            return (
                <svg
                    {...common}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                >
                    <path d="M20.8 8.6c0 5-8.8 10-8.8 10S3.2 13.6 3.2 8.6A4.6 4.6 0 0 1 12 6.2a4.6 4.6 0 0 1 8.8 2.4Z" />
                </svg>
            );

        case "message":
            return (
                <svg
                    {...common}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                >
                    <path d="M21 11.5a8.3 8.3 0 0 1-8.5 8.2 9.4 9.4 0 0 1-4.1-.9L3 20l1.2-4.2A8 8 0 0 1 4 11.5 8.3 8.3 0 0 1 12.5 3 8.3 8.3 0 0 1 21 11.5Z" />
                </svg>
            );

        case "share":
            return (
                <svg
                    {...common}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                >
                    <circle cx="18" cy="5" r="3" />
                    <circle cx="6" cy="12" r="3" />
                    <circle cx="18" cy="19" r="3" />

                    <path d="m8.6 13.5 6.8 4" />
                    <path d="m15.4 6.5-6.8 4" />
                </svg>
            );

        case "trend":
            return (
                <svg
                    {...common}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                >
                    <polyline points="3 17 9 11 13 15 21 7" />
                    <polyline points="14 7 21 7 21 14" />
                </svg>
            );

        case "users":
            return (
                <svg
                    {...common}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                >
                    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />

                    <circle
                        cx="9"
                        cy="7"
                        r="4"
                    />

                    <path d="M22 21v-2a4 4 0 0 0-3-3.87" />

                    <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                </svg>
            );

        case "video":
            return (
                <svg
                    {...common}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                >
                    <rect
                        x="3"
                        y="5"
                        width="13"
                        height="14"
                        rx="2"
                    />

                    <path d="m16 10 5-3v10l-5-3z" />
                </svg>
            );

        case "chart":
            return (
                <svg
                    {...common}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                >
                    <path d="M4 20V10" />
                    <path d="M10 20V4" />
                    <path d="M16 20v-7" />
                    <path d="M22 20V7" />
                </svg>
            );

        case "calendar":
            return (
                <svg
                    {...common}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                >
                    <rect
                        x="3"
                        y="4"
                        width="18"
                        height="17"
                        rx="2"
                    />

                    <line
                        x1="16"
                        y1="2"
                        x2="16"
                        y2="6"
                    />

                    <line
                        x1="8"
                        y1="2"
                        x2="8"
                        y2="6"
                    />

                    <line
                        x1="3"
                        y1="10"
                        x2="21"
                        y2="10"
                    />
                </svg>
            );

        case "refresh":
            return (
                <svg
                    {...common}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                >
                    <path d="M20 11a8 8 0 0 0-14.9-4" />
                    <path d="M4 4v4h4" />
                    <path d="M4 13a8 8 0 0 0 14.9 4" />
                    <path d="M20 20v-4h-4" />
                </svg>
            );

        default:
            return (
                <svg
                    {...common}
                    stroke="currentColor"
                    strokeWidth={strokeWidth}
                >
                    <circle
                        cx="12"
                        cy="12"
                        r="9"
                    />
                </svg>
            );
    }
}


// =====================================================
// ICON ALIASES
// =====================================================

const Instagram = (props) => (
    <MetaIcon
        type="instagram"
        {...props}
    />
);

const Eye = (props) => (
    <MetaIcon
        type="eye"
        {...props}
    />
);

const Heart = (props) => (
    <MetaIcon
        type="heart"
        {...props}
    />
);

const MessageCircle = (props) => (
    <MetaIcon
        type="message"
        {...props}
    />
);

const Share2 = (props) => (
    <MetaIcon
        type="share"
        {...props}
    />
);

const TrendingUp = (props) => (
    <MetaIcon
        type="trend"
        {...props}
    />
);

const Users = (props) => (
    <MetaIcon
        type="users"
        {...props}
    />
);

const Video = (props) => (
    <MetaIcon
        type="video"
        {...props}
    />
);

const BarChart3 = (props) => (
    <MetaIcon
        type="chart"
        {...props}
    />
);

const CalendarDays = (props) => (
    <MetaIcon
        type="calendar"
        {...props}
    />
);

const RefreshCw = (props) => (
    <MetaIcon
        type="refresh"
        {...props}
    />
);


// =====================================================
// FACEBOOK MARK
// =====================================================

function FacebookMark({
    size = 20,
    className = "",
}) {
    const box =
        Math.max(
            28,
            size + 10
        );

    return (
        <span
            className={`inline-flex items-center justify-center rounded-full bg-slate-900 font-bold leading-none text-white ${className}`}
            style={{
                width: `${box}px`,
                height: `${box}px`,
                fontSize: `${Math.max(
                    13,
                    Math.round(size * 0.72)
                )}px`,
            }}
            aria-label="Facebook"
            title="Facebook"
        >
            f
        </span>
    );
}


// =====================================================
// HELPERS
// =====================================================

function formatNumber(value) {
    if (
        value === null ||
        value === undefined ||
        Number.isNaN(
            Number(value)
        )
    ) {
        return "0";
    }

    return new Intl.NumberFormat(
        "id-ID"
    ).format(
        Number(value)
    );
}


function formatPercentage(value) {
    if (
        value === null ||
        value === undefined ||
        Number.isNaN(
            Number(value)
        )
    ) {
        return "0%";
    }

    return `${Number(value).toFixed(2)}%`;
}


function formatDate(value) {
    if (!value) {
        return "-";
    }

    const date = new Date(value);

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


function getMediaLabel(value) {
    if (!value) {
        return "Tidak diketahui";
    }

    const normalized =
        String(value).toLowerCase();

    if (
        normalized.includes(
            "reel"
        )
    ) {
        return "Reels";
    }

    if (
        normalized.includes(
            "video"
        )
    ) {
        return "Video";
    }

    if (
        normalized.includes(
            "image"
        ) ||
        normalized.includes(
            "photo"
        )
    ) {
        return "Foto";
    }

    if (
        normalized.includes(
            "carousel"
        ) ||
        normalized.includes(
            "album"
        )
    ) {
        return "Carousel";
    }

    return value;
}


// =====================================================
// RESPONSE NORMALIZER
// =====================================================

function unwrapResponse(response) {
    if (
        !response ||
        typeof response !==
            "object"
    ) {
        return response || {};
    }

    if (
        Object.prototype.hasOwnProperty.call(
            response,
            "success"
        )
    ) {
        return response;
    }

    if (
        response.data &&
        typeof response.data ===
            "object" &&
        (
            Object.prototype.hasOwnProperty.call(
                response.data,
                "success"
            ) ||
            Object.prototype.hasOwnProperty.call(
                response.data,
                "summary"
            ) ||
            Object.prototype.hasOwnProperty.call(
                response.data,
                "insights"
            ) ||
            Object.prototype.hasOwnProperty.call(
                response.data,
                "contents"
            )
        )
    ) {
        return response.data;
    }

    return response;
}


// =====================================================
// FACEBOOK METRIC HELPER
// =====================================================

function getFacebookMetricTotal(
    insights,
    metricName
) {
    if (
        !Array.isArray(
            insights
        )
    ) {
        return 0;
    }

    const metric =
        insights.find(
            (item) =>
                item?.name ===
                    metricName ||
                item?.metric_name ===
                    metricName
        );

    if (!metric) {
        return 0;
    }

    const values =
        Array.isArray(
            metric.values
        )
            ? metric.values
            : [];

    return values.reduce(
        (
            total,
            item
        ) =>
            total +
            Number(
                item?.value || 0
            ),
        0
    );
}


// =====================================================
// INSIGHT CARD
// =====================================================

function InsightCard({
    title,
    value,
    icon: Icon,
    description,
}) {
    return (
        <div className="meta-kpi-card">

            <div className="meta-kpi-top">

                <div>

                    <span>
                        {title}
                    </span>

                    <strong>
                        {value}
                    </strong>

                </div>

                <div className="meta-kpi-icon">

                    <Icon
                        size={19}
                        strokeWidth={1.8}
                    />

                </div>

            </div>


            <div className="meta-kpi-footer">

                <TrendingUp
                    size={13}
                />

                <span>
                    {description}
                </span>

            </div>

        </div>
    );
}


// =====================================================
// MINI METRIC
// =====================================================

function MiniMetric({
    icon: Icon,
    label,
    value,
}) {
    return (
        <div className="meta-mini-metric">

            <div className="meta-mini-icon">

                <Icon
                    size={16}
                    strokeWidth={1.8}
                />

            </div>

            <div>

                <span>
                    {label}
                </span>

                <strong>
                    {value}
                </strong>

            </div>

        </div>
    );
}


// =====================================================
// PLATFORM TABS
// =====================================================

function PlatformTabs({
    platform,
    navigate,
}) {
    const isInstagram =
        platform ===
        "instagram";

    const isFacebook =
        platform ===
        "facebook";

    return (
        <div
            className="
                mb-6
                flex
                flex-wrap
                items-center
                gap-2
            "
        >

            {/* INSTAGRAM */}

            <button
                type="button"
                onClick={() =>
                    navigate(
                        "/admin/meta-insight/instagram"
                    )
                }
                className={`
                    inline-flex
                    items-center
                    gap-2
                    rounded-xl
                    border
                    px-4
                    py-2.5
                    text-sm
                    font-semibold
                    transition
                    ${
                        isInstagram
                            ? `
                                border-gray-900
                                bg-gray-900
                                text-white
                              `
                            : `
                                border-gray-200
                                bg-white
                                text-gray-600
                                hover:bg-gray-50
                              `
                    }
                `}
            >

                <Instagram
                    size={16}
                />

                Instagram

            </button>


            {/* FACEBOOK */}

            <button
                type="button"
                onClick={() =>
                    navigate(
                        "/admin/meta-insight/facebook"
                    )
                }
                className={`
                    inline-flex
                    items-center
                    gap-2
                    rounded-xl
                    border
                    px-4
                    py-2.5
                    text-sm
                    font-semibold
                    transition
                    ${
                        isFacebook
                            ? `
                                border-gray-900
                                bg-gray-900
                                text-white
                              `
                            : `
                                border-gray-200
                                bg-white
                                text-gray-600
                                hover:bg-gray-50
                              `
                    }
                `}
            >

                <FacebookMark
                    size={16}
                />

                Facebook

            </button>

        </div>
    );
}


// =====================================================
// INSTAGRAM VIEW
// =====================================================

function InstagramInsightView({
    data,
    formatNumber,
    formatPercentage,
    formatDate,
    getMediaLabel,
}) {
    const summary =
        data?.summary &&
        typeof data.summary ===
            "object"
            ? data.summary
            : {};

    const insights =
        Array.isArray(
            data?.insights
        )
            ? data.insights
            : [];

    const bestContent =
        Array.isArray(
            data?.best_content
        )
            ? data.best_content
            : [];

    const worstContent =
        Array.isArray(
            data?.worst_content
        )
            ? data.worst_content
            : [];

    const mediaPerformance =
        Array.isArray(
            data?.media_performance
        )
            ? data.media_performance
            : [];

    const mediaChartData =
        mediaPerformance.map(
            (item) => ({
                name:
                    getMediaLabel(
                        item?.media_type
                    ),
                engagement:
                    Number(
                        item?.average_engagement_rate ||
                        0
                    ),
                posts:
                    Number(
                        item?.total_posts ||
                        0
                    ),
            })
        );


    return (
        <>

            {/* KPI */}

            <div className="meta-insight-kpi-grid">

                <InsightCard
                    title="Views"
                    value={formatNumber(
                        summary.total_views
                    )}
                    icon={Eye}
                    description="Total tayangan konten"
                />

                <InsightCard
                    title="Reach"
                    value={formatNumber(
                        summary.total_reach
                    )}
                    icon={Users}
                    description="Total akun yang dijangkau"
                />

                <InsightCard
                    title="Impressions"
                    value={formatNumber(
                        summary.total_impressions
                    )}
                    icon={TrendingUp}
                    description="Total impresi"
                />

                <InsightCard
                    title="Engagement Rate"
                    value={formatPercentage(
                        summary.average_engagement_rate
                    )}
                    icon={Heart}
                    description="Rata-rata engagement"
                />

            </div>


            {/* SECONDARY */}

            <div className="meta-insight-secondary-grid">

                <MiniMetric
                    icon={Heart}
                    label="Likes"
                    value={formatNumber(
                        summary.total_likes
                    )}
                />

                <MiniMetric
                    icon={MessageCircle}
                    label="Comments"
                    value={formatNumber(
                        summary.total_comments
                    )}
                />

                <MiniMetric
                    icon={Share2}
                    label="Shares"
                    value={formatNumber(
                        summary.total_shares
                    )}
                />

                <MiniMetric
                    icon={SaveIcon}
                    label="Saves"
                    value={formatNumber(
                        summary.total_saves
                    )}
                />

                <MiniMetric
                    icon={Video}
                    label="Total Data"
                    value={formatNumber(
                        summary.total_data
                    )}
                />

            </div>


            {/* INSIGHT + MEDIA */}

            <div className="meta-insight-main-grid">

                <section className="meta-insight-panel">

                    <div className="meta-panel-header">

                        <div>

                            <span className="meta-panel-eyebrow">
                                ANALISIS OTOMATIS
                            </span>

                            <h3>
                                Insight Performa Instagram
                            </h3>

                        </div>

                        <div className="meta-panel-icon">

                            <Instagram
                                size={18}
                            />

                        </div>

                    </div>


                    <div className="meta-insight-list">

                        {insights.length ===
                        0 ? (
                            <div className="meta-empty">
                                Belum terdapat
                                insight.
                            </div>
                        ) : (
                            insights.map(
                                (
                                    insight,
                                    index
                                ) => (
                                    <div
                                        className="meta-insight-item"
                                        key={index}
                                    >

                                        <span className="meta-insight-number">
                                            {String(
                                                index +
                                                1
                                            ).padStart(
                                                2,
                                                "0"
                                            )}
                                        </span>

                                        <p>
                                            {insight}
                                        </p>

                                    </div>
                                )
                            )
                        )}

                    </div>

                </section>


                <section className="meta-insight-panel">

                    <div className="meta-panel-header">

                        <div>

                            <span className="meta-panel-eyebrow">
                                MEDIA PERFORMANCE
                            </span>

                            <h3>
                                Engagement per Media
                            </h3>

                        </div>

                    </div>


                    <div className="meta-chart">

                        {mediaChartData.length ===
                        0 ? (
                            <div className="meta-empty">
                                Belum terdapat
                                data media.
                            </div>
                        ) : (

                            <ResponsiveContainer
                                width="100%"
                                height={270}
                            >

                                <BarChart
                                    data={
                                        mediaChartData
                                    }
                                    margin={{
                                        top: 10,
                                        right: 10,
                                        left: -20,
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
                                            fontSize: 11,
                                        }}
                                    />

                                    <YAxis
                                        axisLine={false}
                                        tickLine={false}
                                        tick={{
                                            fontSize: 10,
                                        }}
                                        tickFormatter={(
                                            value
                                        ) =>
                                            `${value}%`
                                        }
                                    />

                                    <Tooltip
                                        formatter={(
                                            value
                                        ) => [
                                            `${Number(
                                                value
                                            ).toFixed(
                                                2
                                            )}%`,
                                            "Engagement",
                                        ]}
                                    />

                                    <Bar
                                        dataKey="engagement"
                                        radius={[
                                            7,
                                            7,
                                            0,
                                            0,
                                        ]}
                                        barSize={42}
                                    >

                                        {mediaChartData.map(
                                            (
                                                item,
                                                index
                                            ) => (
                                                <Cell
                                                    key={
                                                        index
                                                    }
                                                />
                                            )
                                        )}

                                    </Bar>

                                </BarChart>

                            </ResponsiveContainer>
                        )}

                    </div>

                </section>

            </div>


            {/* BEST */}

            <ContentTable
                title="Konten Terbaik"
                eyebrow="TOP PERFORMANCE"
                posts={
                    bestContent
                }
                emptyText="Belum terdapat konten terbaik."
                formatNumber={
                    formatNumber
                }
                formatPercentage={
                    formatPercentage
                }
                formatDate={
                    formatDate
                }
                getMediaLabel={
                    getMediaLabel
                }
            />


            {/* WORST */}

            <ContentTable
                title="Konten dengan Performa Rendah"
                eyebrow="NEEDS ATTENTION"
                posts={
                    worstContent
                }
                emptyText="Belum terdapat konten dengan performa rendah."
                formatNumber={
                    formatNumber
                }
                formatPercentage={
                    formatPercentage
                }
                formatDate={
                    formatDate
                }
                getMediaLabel={
                    getMediaLabel
                }
                lowPerformance
            />

        </>
    );
}


// =====================================================
// FACEBOOK VIEW
// =====================================================

function FacebookInsightView({
    data,
    formatNumber,
    formatDate,
}) {
    const insights =
        Array.isArray(
            data?.insights
        )
            ? data.insights
            : [];

    const contents =
        Array.isArray(
            data?.contents
        )
            ? data.contents
            : [];

    const page =
        data?.page || null;


    const pageViews =
        getFacebookMetricTotal(
            insights,
            "page_views_total"
        );

    const mediaViews =
        getFacebookMetricTotal(
            insights,
            "page_media_view"
        );

    const postEngagements =
        getFacebookMetricTotal(
            insights,
            "page_post_engagements"
        );


    const engagementRate =
        pageViews > 0
            ? (
                (
                    postEngagements /
                    pageViews
                ) *
                100
            )
            : 0;


    const chartData = (() => {

                const map = {};

                insights.forEach(
                    (metric) => {

                        const metricName =
                            metric?.name ||
                            metric?.metric_name ||
                            "";

                        const title =
                            metricName ===
                            "page_views_total"
                                ? "Page Views"
                                : metricName ===
                                  "page_media_view"
                                    ? "Media Views"
                                    : metricName ===
                                      "page_post_engagements"
                                        ? "Engagement"
                                        : metricName;

                        const values =
                            Array.isArray(
                                metric?.values
                            )
                                ? metric.values
                                : [];

                        values.forEach(
                            (row) => {

                                const dateKey =
                                    row?.end_time
                                        ? String(
                                            row.end_time
                                        ).slice(
                                            0,
                                            10
                                        )
                                        : "Data";

                                if (
                                    !map[
                                        dateKey
                                    ]
                                ) {
                                    map[
                                        dateKey
                                    ] = {
                                        date:
                                            dateKey,
                                        "Page Views":
                                            0,
                                        "Media Views":
                                            0,
                                        Engagement:
                                            0,
                                    };
                                }


                                if (
                                    title ===
                                    "Page Views"
                                ) {
                                    map[
                                        dateKey
                                    ]["Page Views"] +=
                                        Number(
                                            row?.value ||
                                            0
                                        );
                                }


                                if (
                                    title ===
                                    "Media Views"
                                ) {
                                    map[
                                        dateKey
                                    ]["Media Views"] +=
                                        Number(
                                            row?.value ||
                                            0
                                        );
                                }


                                if (
                                    title ===
                                    "Engagement"
                                ) {
                                    map[
                                        dateKey
                                    ].Engagement +=
                                        Number(
                                            row?.value ||
                                            0
                                        );
                                }

                            }
                        );

                    }
                );


                return Object.values(
                    map
                );

            })();


    return (
        <>

            {/* FACEBOOK PAGE HEADER */}

            <div
                className="
                    mb-5
                    rounded-2xl
                    border
                    border-gray-200
                    bg-white
                    p-5
                    shadow-sm
                "
            >

                <div
                    className="
                        flex
                        flex-col
                        gap-3
                        md:flex-row
                        md:items-center
                        md:justify-between
                    "
                >

                    <div>

                        <span
                            className="
                                text-xs
                                font-semibold
                                tracking-widest
                                text-gray-400
                            "
                        >
                            FACEBOOK PAGE
                        </span>

                        <h3
                            className="
                                mt-1
                                text-xl
                                font-bold
                                text-gray-900
                            "
                        >
                            {page?.name ||
                                "Facebook"}
                        </h3>

                        <p
                            className="
                                mt-1
                                text-sm
                                text-gray-500
                            "
                        >
                            Insight halaman Facebook
                            berdasarkan data yang
                            tersimpan dan tersedia.
                        </p>

                    </div>


                    <div
                        className="
                            inline-flex
                            items-center
                            gap-2
                            rounded-xl
                            bg-gray-50
                            px-4
                            py-3
                            text-sm
                            text-gray-600
                        "
                    >

                        <FacebookMark
                            size={17}
                        />

                        {contents.length}
                        {" "}
                        content

                    </div>

                </div>

            </div>


            {/* KPI */}

            <div className="meta-insight-kpi-grid">

                <InsightCard
                    title="Page Views"
                    value={formatNumber(
                        pageViews
                    )}
                    icon={Eye}
                    description="Total kunjungan halaman"
                />

                <InsightCard
                    title="Media Views"
                    value={formatNumber(
                        mediaViews
                    )}
                    icon={Video}
                    description="Total tayangan media"
                />

                <InsightCard
                    title="Post Engagement"
                    value={formatNumber(
                        postEngagements
                    )}
                    icon={Heart}
                    description="Interaksi posting"
                />

                <InsightCard
                    title="Engagement / Views"
                    value={formatPercentage(
                        engagementRate
                    )}
                    icon={TrendingUp}
                    description="Rasio engagement terhadap views"
                />

            </div>


            {/* SECONDARY */}

            <div className="meta-insight-secondary-grid">

                <MiniMetric
                    icon={Eye}
                    label="Page Views"
                    value={formatNumber(
                        pageViews
                    )}
                />

                <MiniMetric
                    icon={Video}
                    label="Media Views"
                    value={formatNumber(
                        mediaViews
                    )}
                />

                <MiniMetric
                    icon={Heart}
                    label="Post Engagement"
                    value={formatNumber(
                        postEngagements
                    )}
                />

                <MiniMetric
                    icon={FacebookMark}
                    label="Facebook Content"
                    value={formatNumber(
                        contents.length
                    )}
                />

            </div>


            {/* CHART + SUMMARY */}

            <div className="meta-insight-main-grid">

                <section className="meta-insight-panel">

                    <div className="meta-panel-header">

                        <div>

                            <span className="meta-panel-eyebrow">
                                PAGE INSIGHTS
                            </span>

                            <h3>
                                Perkembangan Insight Facebook
                            </h3>

                        </div>

                    </div>


                    <div className="meta-chart">

                        {chartData.length ===
                        0 ? (

                            <div className="meta-empty">
                                Belum terdapat data
                                histori Facebook.
                            </div>

                        ) : (

                            <ResponsiveContainer
                                width="100%"
                                height={290}
                            >

                                <BarChart
                                    data={
                                        chartData
                                    }
                                    margin={{
                                        top: 10,
                                        right: 10,
                                        left: -20,
                                        bottom: 5,
                                    }}
                                >

                                    <CartesianGrid
                                        strokeDasharray="3 3"
                                        vertical={false}
                                    />

                                    <XAxis
                                        dataKey="date"
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
                                        dataKey="Page Views"
                                        radius={[
                                            5,
                                            5,
                                            0,
                                            0,
                                        ]}
                                    />

                                    <Bar
                                        dataKey="Media Views"
                                        radius={[
                                            5,
                                            5,
                                            0,
                                            0,
                                        ]}
                                    />

                                    <Bar
                                        dataKey="Engagement"
                                        radius={[
                                            5,
                                            5,
                                            0,
                                            0,
                                        ]}
                                    />

                                </BarChart>

                            </ResponsiveContainer>

                        )}

                    </div>

                </section>


                <section className="meta-insight-panel">

                    <div className="meta-panel-header">

                        <div>

                            <span className="meta-panel-eyebrow">
                                SUMMARY
                            </span>

                            <h3>
                                Ringkasan Facebook
                            </h3>

                        </div>

                    </div>


                    <div
                        className="
                            grid
                            grid-cols-1
                            gap-3
                        "
                    >

                        <SummaryRow
                            label="Page"
                            value={
                                page?.name ||
                                "-"
                            }
                        />

                        <SummaryRow
                            label="Total Content"
                            value={formatNumber(
                                contents.length
                            )}
                        />

                        <SummaryRow
                            label="Page Views"
                            value={formatNumber(
                                pageViews
                            )}
                        />

                        <SummaryRow
                            label="Media Views"
                            value={formatNumber(
                                mediaViews
                            )}
                        />

                        <SummaryRow
                            label="Post Engagement"
                            value={formatNumber(
                                postEngagements
                            )}
                        />

                    </div>

                </section>

            </div>


            {/* FACEBOOK CONTENT */}

            <section className="meta-insight-panel">

                <div className="meta-panel-header">

                    <div>

                        <span className="meta-panel-eyebrow">
                            FACEBOOK CONTENT
                        </span>

                        <h3>
                            Daftar Konten Facebook
                        </h3>

                    </div>

                    <span className="meta-panel-count">
                        {contents.length} konten
                    </span>

                </div>


                <div className="meta-content-table-wrapper">

                    {contents.length ===
                    0 ? (

                        <div className="meta-empty">
                            Belum terdapat
                            konten Facebook.
                        </div>

                    ) : (

                        <table className="meta-content-table">

                            <thead>

                                <tr>

                                    <th>
                                        Konten
                                    </th>

                                    <th>
                                        Media
                                    </th>

                                    <th>
                                        Tanggal
                                    </th>

                                    <th>
                                        Views
                                    </th>

                                    <th>
                                        Engagement
                                    </th>

                                    <th>
                                        Aksi
                                    </th>

                                </tr>

                            </thead>


                            <tbody>

                                {contents.map(
                                    (
                                        post,
                                        index
                                    ) => (

                                        <tr
                                            key={
                                                post.id ||
                                                post.post_id ||
                                                index
                                            }
                                        >

                                            <td>

                                                <div className="meta-content-name">

                                                    <strong>
                                                        {
                                                            post.post_id ||
                                                            `Post #${
                                                                index +
                                                                1
                                                            }`
                                                        }
                                                    </strong>

                                                    <span>
                                                        {
                                                            post.message
                                                                ? post.message
                                                                      .length >
                                                                  75
                                                                    ? `${post.message.slice(
                                                                        0,
                                                                        75
                                                                    )}...`
                                                                    : post.message
                                                                : "Tanpa caption"
                                                        }
                                                    </span>

                                                </div>

                                            </td>


                                            <td>

                                                <span className="meta-media-badge">

                                                    {getMediaLabel(
                                                        post.content_type
                                                    )}

                                                </span>

                                            </td>


                                            <td>
                                                {formatDate(
                                                    post.created_time
                                                )}
                                            </td>


                                            <td>
                                                {Number(
                                                    post.views ||
                                                    0
                                                ) > 0
                                                    ? formatNumber(
                                                        post.views
                                                    )
                                                    : "-"}
                                            </td>


                                            <td>
                                                {Number(
                                                    post.engagement ||
                                                    0
                                                ) > 0
                                                    ? formatNumber(
                                                        post.engagement
                                                    )
                                                    : "-"}
                                            </td>


                                            <td>

                                                {post.permalink_url ? (

                                                    <a
                                                        href={
                                                            post.permalink_url
                                                        }
                                                        target="_blank"
                                                        rel="noreferrer"
                                                        className="
                                                            text-sm
                                                            font-semibold
                                                            text-gray-700
                                                            hover:underline
                                                        "
                                                    >
                                                        Buka
                                                    </a>

                                                ) : (

                                                    <span className="text-sm text-gray-400">
                                                        -
                                                    </span>

                                                )}

                                            </td>

                                        </tr>

                                    )
                                )}

                            </tbody>

                        </table>

                    )}

                </div>

            </section>


            {/* NOTE */}

            <div
                className="
                    mt-5
                    rounded-2xl
                    border
                    border-amber-200
                    bg-amber-50
                    px-5
                    py-4
                    text-sm
                    leading-6
                    text-amber-800
                "
            >
                Metric per-post Facebook seperti
                likes, comments, shares, views, dan
                impressions belum ditampilkan sebagai
                angka 0 karena endpoint penyimpanan saat
                ini baru menyediakan data content dasar
                dan Page Insights.
            </div>

        </>
    );
}


// =====================================================
// CONTENT TABLE - INSTAGRAM
// =====================================================

function ContentTable({
    title,
    eyebrow,
    posts,
    emptyText,
    formatNumber,
    formatPercentage,
    formatDate,
    getMediaLabel,
    lowPerformance = false,
}) {
    return (
        <section className="meta-insight-panel">

            <div className="meta-panel-header">

                <div>

                    <span className="meta-panel-eyebrow">
                        {eyebrow}
                    </span>

                    <h3>
                        {title}
                    </h3>

                </div>

                <span className="meta-panel-count">
                    {posts.length} konten
                </span>

            </div>


            <div className="meta-content-table-wrapper">

                {posts.length ===
                0 ? (

                    <div className="meta-empty">
                        {emptyText}
                    </div>

                ) : (

                    <table className="meta-content-table">

                        <thead>

                            <tr>

                                <th>
                                    Konten
                                </th>

                                <th>
                                    Media
                                </th>

                                <th>
                                    Tanggal
                                </th>

                                <th>
                                    Reach
                                </th>

                                <th>
                                    Engagement
                                </th>

                                <th>
                                    ER
                                </th>

                            </tr>

                        </thead>


                        <tbody>

                            {posts.map(
                                (
                                    post,
                                    index
                                ) => (

                                    <tr
                                        key={
                                            post.id_posts ||
                                            post.meta_post_id ||
                                            index
                                        }
                                    >

                                        <td>

                                            <div className="meta-content-name">

                                                <strong>
                                                    {
                                                        post.meta_post_id ||
                                                        `Post #${
                                                            post.id_posts ||
                                                            index +
                                                            1
                                                        }`
                                                    }
                                                </strong>

                                                <span>
                                                    {
                                                        post.caption
                                                            ? post.caption
                                                                  .length >
                                                              75
                                                                ? `${post.caption.slice(
                                                                    0,
                                                                    75
                                                                )}...`
                                                                : post.caption
                                                            : "Tanpa caption"
                                                    }
                                                </span>

                                            </div>

                                        </td>


                                        <td>

                                            <span className="meta-media-badge">

                                                {getMediaLabel(
                                                    post.media_type
                                                )}

                                            </span>

                                        </td>


                                        <td>
                                            {formatDate(
                                                post.posted_at
                                            )}
                                        </td>


                                        <td>
                                            {formatNumber(
                                                post.reach
                                            )}
                                        </td>


                                        <td>
                                            {formatNumber(
                                                Number(
                                                    post.likes ||
                                                    0
                                                ) +
                                                Number(
                                                    post.comments ||
                                                    0
                                                ) +
                                                Number(
                                                    post.shares ||
                                                    0
                                                ) +
                                                Number(
                                                    post.saves ||
                                                    0
                                                )
                                            )}
                                        </td>


                                        <td>

                                            <strong
                                                className={
                                                    lowPerformance
                                                        ? "meta-er-low"
                                                        : "meta-er-value"
                                                }
                                            >
                                                {formatPercentage(
                                                    post.engagement_rate
                                                )}
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
    );
}


// =====================================================
// SUMMARY ROW
// =====================================================

function SummaryRow({
    label,
    value,
}) {
    return (
        <div
            className="
                flex
                items-center
                justify-between
                rounded-xl
                border
                border-gray-100
                px-4
                py-3
                text-sm
            "
        >

            <span className="text-gray-500">
                {label}
            </span>

            <strong className="text-gray-900">
                {value}
            </strong>

        </div>
    );
}


// =====================================================
// SAVE ICON
// =====================================================

function SaveIcon(props) {
    return (
        <svg
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.8"
            strokeLinecap="round"
            strokeLinejoin="round"
            {...props}
        >

            <path
                d="
                    M19 21
                    l-7-4
                    -7 4
                    V5
                    a2 2 0 0 1 2-2
                    h10
                    a2 2 0 0 1 2 2
                    z
                "
            />

        </svg>
    );
}


// =====================================================
// MAIN COMPONENT
// =====================================================

export default function MetaInsight() {
    const location =
        useLocation();

    const navigate =
        useNavigate();


    const platform =
        location.pathname.includes(
            "/meta-insight/facebook"
        )
            ? "facebook"
            : "instagram";


    const [data, setData] =
        useState(null);

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
    // FETCH
    // =====================================================

    const fetchInsight =
        useCallback(
            async (
                showRefresh = false
            ) => {

                try {

                    if (showRefresh) {

                        setRefreshing(
                            true
                        );

                    } else {

                        setLoading(
                            true
                        );

                    }

                    setError("");


                    // ==========================================
                    // INSTAGRAM
                    // ==========================================

                    if (
                        platform ===
                        "instagram"
                    ) {

                        const params =
                            new URLSearchParams();

                        if (month) {

                            params.set(
                                "month",
                                month
                            );

                        }

                        if (year) {

                            params.set(
                                "year",
                                year
                            );

                        }


                        let endpoint =
                            "/api/meta-insight/";

                        const query =
                            params.toString();

                        if (query) {

                            endpoint +=
                                `?${query}`;

                        }


                        const response =
                            await api.get(
                                endpoint
                            );

                        const payload =
                            unwrapResponse(
                                response
                            );


                        if (
                            payload?.success ===
                            false
                        ) {

                            throw new Error(
                                payload.message ||
                                "Data Meta Insight gagal diambil."
                            );

                        }


                        const result =
                            payload?.data &&
                            typeof payload.data ===
                                "object"
                                ? payload.data
                                : payload;


                        setData(
                            result
                        );

                        return;
                    }


                    // ==========================================
                    // FACEBOOK
                    // ==========================================

                    const [
                        statusResponse,
                        insightResponse,
                        contentResponse,
                    ] =
                        await Promise.all(
                            [

                                api.get(
                                    "/api/facebook/status"
                                ),

                                api.get(
                                    "/api/facebook/insights?metric=page_post_engagements,page_views_total,page_media_view&period=days_28"
                                ),

                                api.get(
                                    "/api/facebook/contents"
                                ),

                            ]
                        );


                    const statusPayload =
                        unwrapResponse(
                            statusResponse
                        );

                    const insightPayload =
                        unwrapResponse(
                            insightResponse
                        );

                    const contentPayload =
                        unwrapResponse(
                            contentResponse
                        );


                    const statusData =
                        statusPayload?.data &&
                        typeof statusPayload.data ===
                            "object" &&
                        !Array.isArray(
                            statusPayload.data
                        )
                            ? statusPayload.data
                            : statusPayload;


                    const insightData =
                        insightPayload?.data &&
                        typeof insightPayload.data ===
                            "object" &&
                        !Array.isArray(
                            insightPayload.data
                        )
                            ? insightPayload.data
                            : insightPayload;


                    const contentData =
                        contentPayload?.data &&
                        typeof contentPayload.data ===
                            "object" &&
                        !Array.isArray(
                            contentPayload.data
                        )
                            ? contentPayload.data
                            : contentPayload;


                    const page =
                        statusData?.selected_page ||
                        statusData?.pages?.[0] ||
                        insightData?.page ||
                        null;


                    const insights =
                        Array.isArray(
                            insightData?.insights
                        )
                            ? insightData.insights
                            : [];


                    const contents =
                        Array.isArray(
                            contentData
                        )
                            ? contentData
                            : Array.isArray(
                                contentData?.contents
                            )
                                ? contentData.contents
                                : Array.isArray(
                                    contentData?.data
                                )
                                    ? contentData.data
                                    : [];


                    setData({
                        connected:
                            Boolean(
                                statusData?.connected
                            ),
                        page,
                        insights,
                        contents,
                    });

                } catch (err) {

                    console.error(
                        "Meta Insight error:",
                        err
                    );

                    setData(
                        null
                    );

                    setError(
                        err?.response
                            ?.data
                            ?.message ||
                        err?.message ||
                        "Tidak dapat terhubung ke server."
                    );

                } finally {

                    setLoading(
                        false
                    );

                    setRefreshing(
                        false
                    );

                }

            },
            [
                platform,
                month,
                year,
            ]
        );


    // =====================================================
    // INITIAL FETCH
    // =====================================================

    useEffect(
        () => {

            const timer =
                setTimeout(
                    () => {
                        fetchInsight();
                    },
                    0
                );

            return () => {
                clearTimeout(timer);
            };

        },
        // Sengaja hanya memuat ulang saat platform berubah.
        // Filter month/year dijalankan melalui tombol Terapkan.
        // eslint-disable-next-line react-hooks/exhaustive-deps
        [
            platform,
        ]
    );


    // =====================================================
    // FILTER
    // =====================================================

    const applyFilter =
        () => {

            fetchInsight(
                true
            );

        };


    const resetFilter =
        () => {

            setMonth("");
            setYear("");

            setTimeout(
                () => {

                    fetchInsight(
                        true
                    );

                },
                0
            );

        };


    // =====================================================
    // LOADING
    // =====================================================

    if (loading) {

        return (
            <div className="meta-insight-loading">

                <div className="meta-insight-spinner" />

                <span>
                    Memuat Meta Insight...
                </span>

            </div>
        );

    }


    // =====================================================
    // RENDER
    // =====================================================

    return (
        <div className="meta-insight-page">

            {/* HEADER */}

            <div className="meta-insight-top">

                <div className="meta-insight-heading">

                    <div className="meta-insight-breadcrumb">

                        <BarChart3
                            size={17}
                            strokeWidth={1.8}
                        />

                        <span>
                            Meta Insight
                        </span>

                    </div>


                    <h2>
                        {
                            platform ===
                            "instagram"
                                ? "Performa Konten Instagram"
                                : "Performa Facebook Page"
                        }
                    </h2>


                    <p>
                        {
                            platform ===
                            "instagram"
                                ? "Analisis performa Instagram berdasarkan data yang tersimpan pada MAVis."
                                : "Analisis performa Facebook Page berdasarkan Page Insights dan content yang tersimpan pada MAVis."
                        }
                    </p>

                </div>


                {/* FILTER */}

                <div className="meta-insight-filters">

                    <div className="meta-filter-select">

                        <CalendarDays
                            size={16}
                            strokeWidth={1.8}
                        />

                        <select
                            value={month}
                            onChange={(
                                event
                            ) =>
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


                    <div className="meta-filter-select">

                        <select
                            value={year}
                            onChange={(
                                event
                            ) =>
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
                        className="meta-filter-button"
                        onClick={
                            applyFilter
                        }
                        disabled={
                            refreshing
                        }
                    >

                        <RefreshCw
                            size={15}
                            className={
                                refreshing
                                    ? "meta-spin"
                                    : ""
                            }
                        />

                        {
                            refreshing
                                ? "Memuat..."
                                : "Terapkan"
                        }

                    </button>


                    {(month ||
                        year) && (

                        <button
                            type="button"
                            className="meta-reset-button"
                            onClick={
                                resetFilter
                            }
                        >
                            Reset
                        </button>

                    )}

                </div>

            </div>


            {/* PLATFORM TABS */}

            <PlatformTabs
                platform={
                    platform
                }
                navigate={
                    navigate
                }
            />


            {/* ERROR */}

            {error && (

                <div className="meta-insight-error">

                    <span>
                        {error}
                    </span>

                    <button
                        type="button"
                        onClick={() =>
                            fetchInsight(
                                true
                            )
                        }
                    >
                        Coba lagi
                    </button>

                </div>

            )}


            {/* INSTAGRAM */}

            {!error &&
                platform ===
                    "instagram" && (

                    <InstagramInsightView
                        data={
                            data
                        }
                        formatNumber={
                            formatNumber
                        }
                        formatPercentage={
                            formatPercentage
                        }
                        formatDate={
                            formatDate
                        }
                        getMediaLabel={
                            getMediaLabel
                        }
                    />
                )}


            {/* FACEBOOK */}

            {!error &&
                platform ===
                    "facebook" && (

                    data?.connected ? (

                        <FacebookInsightView
                            data={
                                data
                            }
                            formatNumber={
                                formatNumber
                            }
                            formatDate={
                                formatDate
                            }
                        />

                    ) : (

                        <div
                            className="
                                rounded-2xl
                                border
                                border-gray-200
                                bg-white
                                p-10
                                text-center
                                shadow-sm
                            "
                        >

                            <div
                                className="
                                    mx-auto
                                    flex
                                    h-14
                                    w-14
                                    items-center
                                    justify-center
                                    rounded-2xl
                                    bg-gray-100
                                "
                            >

                                <FacebookMark
                                    size={25}
                                />

                            </div>


                            <h3
                                className="
                                    mt-4
                                    text-lg
                                    font-bold
                                    text-gray-900
                                "
                            >
                                Facebook belum terhubung
                            </h3>


                            <p
                                className="
                                    mx-auto
                                    mt-2
                                    max-w-lg
                                    text-sm
                                    leading-6
                                    text-gray-500
                                "
                            >
                                Hubungkan Facebook melalui
                                halaman Meta Connection
                                terlebih dahulu.
                            </p>


                            <button
                                type="button"
                                onClick={() =>
                                    navigate(
                                        "/admin/meta-connection/facebook"
                                    )
                                }
                                className="
                                    mt-5
                                    inline-flex
                                    items-center
                                    gap-2
                                    rounded-xl
                                    bg-gray-900
                                    px-5
                                    py-3
                                    text-sm
                                    font-semibold
                                    text-white
                                    hover:bg-gray-800
                                "
                            >
                                Buka Meta Connection
                            </button>

                        </div>

                    )
                )}

        </div>
    );
}