import { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import * as api from "../../services/api";

/* =========================================================
   ICON COMPONENT
   Tidak menggunakan lucide-react agar kompatibel dengan
   versi package yang ada di project.
========================================================= */

function Icon({
    type,
    size = 20,
    className = "",
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
                <svg {...common} stroke="currentColor" strokeWidth="1.8">
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
                <svg {...common} stroke="currentColor" strokeWidth="1.8">
                    <path d="M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12Z" />
                    <circle cx="12" cy="12" r="2.8" />
                </svg>
            );

        case "users":
            return (
                <svg {...common} stroke="currentColor" strokeWidth="1.8">
                    <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                    <circle cx="9" cy="7" r="4" />
                    <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                    <path d="M16 3.13a4 4 0 0 1 0 7.75" />
                </svg>
            );

        case "heart":
            return (
                <svg {...common} stroke="currentColor" strokeWidth="1.8">
                    <path d="M20.8 8.6c0 5-8.8 10-8.8 10S3.2 13.6 3.2 8.6A4.6 4.6 0 0 1 12 6.2a4.6 4.6 0 0 1 8.8 2.4Z" />
                </svg>
            );

        case "message":
            return (
                <svg {...common} stroke="currentColor" strokeWidth="1.8">
                    <path d="M21 11.5a8.3 8.3 0 0 1-8.5 8.2 9.4 9.4 0 0 1-4.1-.9L3 20l1.2-4.2A8 8 0 0 1 4 11.5 8.3 8.3 0 0 1 12.5 3 8.3 8.3 0 0 1 21 11.5Z" />
                </svg>
            );

        case "file":
            return (
                <svg {...common} stroke="currentColor" strokeWidth="1.8">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z" />
                    <path d="M14 2v6h6" />
                    <path d="M8 13h8" />
                    <path d="M8 17h6" />
                </svg>
            );

        case "chart":
            return (
                <svg {...common} stroke="currentColor" strokeWidth="1.8">
                    <path d="M4 20V10" />
                    <path d="M10 20V4" />
                    <path d="M16 20v-7" />
                    <path d="M22 20V7" />
                </svg>
            );

        case "refresh":
            return (
                <svg {...common} stroke="currentColor" strokeWidth="1.8">
                    <path d="M20 11a8 8 0 0 0-14.9-4" />
                    <path d="M4 4v4h4" />
                    <path d="M4 13a8 8 0 0 0 14.9 4" />
                    <path d="M20 20v-4h-4" />
                </svg>
            );

        case "arrow":
            return (
                <svg {...common} stroke="currentColor" strokeWidth="1.8">
                    <path d="M5 12h14" />
                    <path d="m13 6 6 6-6 6" />
                </svg>
            );

        default:
            return (
                <svg {...common} stroke="currentColor" strokeWidth="1.8">
                    <circle cx="12" cy="12" r="9" />
                </svg>
            );
    }
}


/* =========================================================
   FACEBOOK MARK
========================================================= */

function FacebookMark({
    size = 20,
    className = "",
}) {
    const box = Math.max(28, size + 10);

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


/* =========================================================
   FORMAT NUMBER
========================================================= */

function formatNumber(value) {
    const number = Number(value || 0);

    return new Intl.NumberFormat("id-ID").format(number);
}


/* =========================================================
   SUMMARY CARD
========================================================= */

function SummaryCard({
    icon,
    label,
    value,
    helper,
}) {
    return (
        <div className="rounded-2xl border border-slate-200 bg-white p-4 shadow-sm">
            <div className="flex items-start justify-between gap-3">

                <div>
                    <p className="text-xs font-medium text-slate-400">
                        {label}
                    </p>

                    <p className="mt-2 text-2xl font-bold text-slate-950">
                        {value}
                    </p>
                </div>

                <div className="rounded-xl bg-slate-100 p-2.5 text-slate-600">
                    {icon}
                </div>
            </div>

            <p className="mt-4 text-xs text-slate-400">
                {helper}
            </p>
        </div>
    );
}


/* =========================================================
   DASHBOARD
========================================================= */

export default function Dashboard() {
    const navigate = useNavigate();

    const [instagram, setInstagram] = useState(null);
    const [facebook, setFacebook] = useState(null);

    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState("");

    /* =====================================================
       FETCH DATA
    ===================================================== */

    const fetchOverview = async (showRefresh = false) => {
        try {
            if (showRefresh) {
                setRefreshing(true);
            } else {
                setLoading(true);
            }

            setError("");

            const [
                instagramResult,
                facebookStatusResult,
                facebookContentsResult,
                facebookInsightsResult,
            ] = await Promise.allSettled([
                /* Instagram */
                api.getDashboard(),

                /* Facebook Status */
                api.get(
                    "/api/facebook/status"
                ),

                /* Facebook Contents */
                api.get(
                    "/api/facebook/contents"
                ),

                /* Facebook Insights */
                api.get(
                    "/api/facebook/insights?metric=page_post_engagements,page_views_total,page_media_view&period=days_28"
                ),
            ]);


            /* =================================================
               INSTAGRAM
            ================================================= */

            if (
                instagramResult.status ===
                "fulfilled"
            ) {
                const payload =
                    instagramResult.value;

                setInstagram(
                    payload?.data ??
                    payload ??
                    null
                );
            }


            /* =================================================
               DEFAULT FACEBOOK
            ================================================= */

            const facebookData = {
                connected: false,
                page: null,
                contents: 0,
                postEngagements: 0,
                pageViews: 0,
                mediaViews: 0,
            };


            /* =================================================
               FACEBOOK STATUS
            ================================================= */

            if (
                facebookStatusResult.status ===
                "fulfilled"
            ) {
                const payload =
                    facebookStatusResult.value;

                const data =
                    payload?.data ??
                    payload ??
                    {};

                facebookData.connected =
                    Boolean(
                        data.connected
                    );

                facebookData.page =
                    data.selected_page ||
                    data.page ||
                    data.pages?.[0] ||
                    null;
            }


            /* =================================================
               FACEBOOK CONTENT
            ================================================= */

            if (
                facebookContentsResult.status ===
                "fulfilled"
            ) {
                const payload =
                    facebookContentsResult.value;

                const data =
                    payload?.data ??
                    payload ??
                    {};

                const contents =
                    data.contents ||
                    data.data ||
                    [];

                if (
                    Array.isArray(contents)
                ) {
                    facebookData.contents =
                        contents.length;
                } else if (
                    typeof data.total ===
                    "number"
                ) {
                    facebookData.contents =
                        data.total;
                }
            }


            /* =================================================
               FACEBOOK INSIGHTS
            ================================================= */

            if (
                facebookInsightsResult.status ===
                "fulfilled"
            ) {
                const payload =
                    facebookInsightsResult.value;

                const data =
                    payload?.data ??
                    payload ??
                    {};

                const insights =
                    data.insights ||
                    data.data ||
                    [];

                if (
                    Array.isArray(insights)
                ) {
                    insights.forEach(
                        (item) => {
                            const values =
                                Array.isArray(
                                    item.values
                                )
                                    ? item.values
                                    : [];

                            const total =
                                values.reduce(
                                    (
                                        sum,
                                        row
                                    ) =>
                                        sum +
                                        Number(
                                            row?.value ||
                                            0
                                        ),
                                    0
                                );

                            if (
                                item.name ===
                                "page_post_engagements"
                            ) {
                                facebookData.postEngagements =
                                    total;
                            }

                            if (
                                item.name ===
                                "page_views_total"
                            ) {
                                facebookData.pageViews =
                                    total;
                            }

                            if (
                                item.name ===
                                "page_media_view"
                            ) {
                                facebookData.mediaViews =
                                    total;
                            }
                        }
                    );
                }
            }


            setFacebook(
                facebookData
            );

        } catch (err) {
            console.error(
                "Dashboard overview error:",
                err
            );

            setError(
                err?.response?.data
                    ?.message ||
                err?.message ||
                "Sebagian data dashboard tidak dapat diambil."
            );
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };


    /* =====================================================
       INITIAL LOAD
    ===================================================== */

    useEffect(() => {
        const timer = setTimeout(() => {
            fetchOverview();
        }, 0);

        return () => clearTimeout(timer);
    }, []);


    /* =====================================================
       INSTAGRAM SUMMARY
    ===================================================== */

    const instagramSummary =
        useMemo(() => {
            const data =
                instagram || {};

            const summary =
                data.summary || {};

            const metrics =
                data.metrics || {};

            return {
                followers:
                    metrics.followers ??
                    summary.followers ??
                    data.followers ??
                    0,

                views:
                    metrics.views ??
                    summary.total_views ??
                    data.views ??
                    0,

                reach:
                    metrics.reach ??
                    summary.total_reach ??
                    data.reach ??
                    0,

                likes:
                    metrics.likes ??
                    summary.total_likes ??
                    data.likes ??
                    0,

                comments:
                    metrics.comments ??
                    summary.total_comments ??
                    data.comments ??
                    0,

                shares:
                    metrics.shares ??
                    summary.total_shares ??
                    data.shares ??
                    0,

                posts:
                    metrics.total_posts ??
                    summary.total_posts ??
                    data.total_posts ??
                    0,

                engagementRate:
                    metrics.engagement_rate ??
                    summary.average_engagement_rate ??
                    data.engagement_rate ??
                    0,

                connected:
                    Boolean(
                        data.connected ??
                        data.instagram_connected ??
                        true
                    ),
            };
        }, [instagram]);


    /* =====================================================
       FACEBOOK SUMMARY
    ===================================================== */

    const facebookSummary =
        facebook || {
            connected: false,
            page: null,
            contents: 0,
            postEngagements: 0,
            pageViews: 0,
            mediaViews: 0,
        };


    /* =====================================================
       RENDER
    ===================================================== */

    return (
        <div className="animate-page-enter pb-8">

            {/* =================================================
                HEADER
            ================================================= */}

            <div className="flex flex-col gap-4 xl:flex-row xl:items-end xl:justify-between">

                <div>
                    <p className="text-sm font-medium text-slate-400">
                        MAVis
                    </p>

                    <h1 className="mt-1 text-3xl font-bold text-slate-950">
                        Dashboard Utama
                    </h1>

                    <p className="mt-2 max-w-2xl text-sm text-slate-500">
                        Rekap performa Instagram
                        dan Facebook dalam
                        satu tampilan.
                    </p>
                </div>


                <button
                    type="button"
                    onClick={() =>
                        fetchOverview(true)
                    }
                    disabled={refreshing}
                    className="inline-flex items-center justify-center gap-2 rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:opacity-60"
                >
                    <Icon
                        type="refresh"
                        size={16}
                        className={
                            refreshing
                                ? "animate-spin"
                                : ""
                        }
                    />

                    Refresh Rekap
                </button>

            </div>


            {/* =================================================
                ERROR
            ================================================= */}

            {error && (
                <div className="mt-5 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
                    {error}
                </div>
            )}


            {/* =================================================
                LOADING
            ================================================= */}

            {loading ? (
                <div className="mt-8 rounded-2xl border border-slate-200 bg-white p-12 text-center text-sm text-slate-400 shadow-sm">
                    Memuat rekap Instagram
                    dan Facebook...
                </div>
            ) : (
                <>
                    {/* ==========================================
                        PLATFORM CARDS
                    ========================================== */}

                    <div className="mt-8 grid grid-cols-1 gap-5 lg:grid-cols-2">

                        {/* ======================================
                            INSTAGRAM
                        ====================================== */}

                        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

                            <div className="flex items-start justify-between gap-4">

                                <div>
                                    <div className="flex items-center gap-3">

                                        <div className="rounded-xl bg-slate-100 p-2.5 text-slate-700">
                                            <Icon
                                                type="instagram"
                                                size={22}
                                            />
                                        </div>

                                        <div>
                                            <h2 className="text-lg font-bold text-slate-950">
                                                Instagram
                                            </h2>

                                            <p className="text-xs text-slate-400">
                                                Ringkasan akun Instagram
                                            </p>
                                        </div>

                                    </div>
                                </div>


                                <span
                                    className={`rounded-full px-2.5 py-1 text-[11px] font-semibold ${
                                        instagramSummary.connected
                                            ? "bg-emerald-50 text-emerald-700"
                                            : "bg-slate-100 text-slate-500"
                                    }`}
                                >
                                    {instagramSummary.connected
                                        ? "Terhubung"
                                        : "Belum terhubung"}
                                </span>

                            </div>


                            {/* INSTAGRAM METRICS */}

                            <div className="mt-5 grid grid-cols-2 gap-3">

                                <SummaryCard
                                    icon={
                                        <Icon
                                            type="users"
                                            size={20}
                                        />
                                    }
                                    label="Followers"
                                    value={formatNumber(
                                        instagramSummary.followers
                                    )}
                                    helper="Jumlah followers"
                                />

                                <SummaryCard
                                    icon={
                                        <Icon
                                            type="eye"
                                            size={20}
                                        />
                                    }
                                    label="Views"
                                    value={formatNumber(
                                        instagramSummary.views
                                    )}
                                    helper="Total views"
                                />

                                <SummaryCard
                                    icon={
                                        <Icon
                                            type="chart"
                                            size={20}
                                        />
                                    }
                                    label="Reach"
                                    value={formatNumber(
                                        instagramSummary.reach
                                    )}
                                    helper="Jangkauan akun"
                                />

                                <SummaryCard
                                    icon={
                                        <Icon
                                            type="heart"
                                            size={20}
                                        />
                                    }
                                    label="Likes"
                                    value={formatNumber(
                                        instagramSummary.likes
                                    )}
                                    helper="Total likes"
                                />

                            </div>


                            {/* BUTTON */}

                            <button
                                type="button"
                                onClick={() =>
                                    navigate(
                                        "/admin/dashboard/instagram"
                                    )
                                }
                                className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
                            >
                                Buka Dashboard Instagram

                                <Icon
                                    type="arrow"
                                    size={16}
                                />
                            </button>

                        </div>


                        {/* ======================================
                            FACEBOOK
                        ====================================== */}

                        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

                            <div className="flex items-start justify-between gap-4">

                                <div>

                                    <div className="flex items-center gap-3">

                                        <div className="rounded-xl bg-slate-100 p-2.5 text-slate-700">
                                            <FacebookMark
                                                size={22}
                                            />
                                        </div>

                                        <div>
                                            <h2 className="text-lg font-bold text-slate-950">
                                                Facebook
                                            </h2>

                                            <p className="text-xs text-slate-400">
                                                Ringkasan Facebook Page
                                            </p>
                                        </div>

                                    </div>


                                    {facebookSummary
                                        .page
                                        ?.name && (
                                        <p className="mt-3 text-xs text-slate-500">
                                            Page:{" "}
                                            <span className="font-semibold text-slate-700">
                                                {
                                                    facebookSummary
                                                        .page
                                                        .name
                                                }
                                            </span>
                                        </p>
                                    )}

                                </div>


                                <span
                                    className={`rounded-full px-2.5 py-1 text-[11px] font-semibold ${
                                        facebookSummary.connected
                                            ? "bg-emerald-50 text-emerald-700"
                                            : "bg-slate-100 text-slate-500"
                                    }`}
                                >
                                    {facebookSummary.connected
                                        ? "Terhubung"
                                        : "Belum terhubung"}
                                </span>

                            </div>


                            {/* FACEBOOK METRICS */}

                            <div className="mt-5 grid grid-cols-2 gap-3">

                                <SummaryCard
                                    icon={
                                        <Icon
                                            type="eye"
                                            size={20}
                                        />
                                    }
                                    label="Page Views"
                                    value={formatNumber(
                                        facebookSummary.pageViews
                                    )}
                                    helper="Periode data tersimpan"
                                />

                                <SummaryCard
                                    icon={
                                        <Icon
                                            type="chart"
                                            size={20}
                                        />
                                    }
                                    label="Media Views"
                                    value={formatNumber(
                                        facebookSummary.mediaViews
                                    )}
                                    helper="Tayangan media Page"
                                />

                                <SummaryCard
                                    icon={
                                        <Icon
                                            type="heart"
                                            size={20}
                                        />
                                    }
                                    label="Post Engagement"
                                    value={formatNumber(
                                        facebookSummary.postEngagements
                                    )}
                                    helper="Engagement posting"
                                />

                                <SummaryCard
                                    icon={
                                        <Icon
                                            type="file"
                                            size={20}
                                        />
                                    }
                                    label="Total Content"
                                    value={formatNumber(
                                        facebookSummary.contents
                                    )}
                                    helper="Posting tersimpan"
                                />

                            </div>


                            {/* BUTTON */}

                            <button
                                type="button"
                                onClick={() =>
                                    navigate(
                                        "/admin/dashboard/facebook"
                                    )
                                }
                                className="mt-5 inline-flex w-full items-center justify-center gap-2 rounded-xl bg-slate-950 px-4 py-3 text-sm font-semibold text-white transition hover:bg-slate-800"
                            >
                                Buka Dashboard Facebook

                                <Icon
                                    type="arrow"
                                    size={16}
                                />
                            </button>

                        </div>

                    </div>


                    {/* =================================================
                        REKAP GABUNGAN
                    ================================================= */}

                    <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

                        <div className="flex items-center gap-2">

                            <Icon
                                type="chart"
                                size={19}
                                className="text-slate-600"
                            />

                            <div>
                                <h2 className="text-base font-bold text-slate-950">
                                    Rekap Gabungan
                                </h2>

                                <p className="text-xs text-slate-400">
                                    Ringkasan cepat dari
                                    dua platform
                                </p>
                            </div>

                        </div>


                        <div className="mt-5 grid grid-cols-2 gap-3 md:grid-cols-3 xl:grid-cols-6">

                            <SummaryCard
                                icon={
                                    <Icon
                                        type="message"
                                        size={20}
                                    />
                                }
                                label="IG Comments"
                                value={formatNumber(
                                    instagramSummary.comments
                                )}
                                helper="Instagram"
                            />

                            <SummaryCard
                                icon={
                                    <Icon
                                        type="chart"
                                        size={20}
                                    />
                                }
                                label="IG Shares"
                                value={formatNumber(
                                    instagramSummary.shares
                                )}
                                helper="Instagram"
                            />

                            <SummaryCard
                                icon={
                                    <Icon
                                        type="file"
                                        size={20}
                                    />
                                }
                                label="IG Content"
                                value={formatNumber(
                                    instagramSummary.posts
                                )}
                                helper={`ER ${Number(
                                    instagramSummary.engagementRate ||
                                    0
                                ).toFixed(2)}%`}
                            />

                            <SummaryCard
                                icon={
                                    <Icon
                                        type="eye"
                                        size={20}
                                    />
                                }
                                label="FB Views"
                                value={formatNumber(
                                    facebookSummary.pageViews
                                )}
                                helper="Facebook Page"
                            />

                            <SummaryCard
                                icon={
                                    <Icon
                                        type="chart"
                                        size={20}
                                    />
                                }
                                label="FB Media"
                                value={formatNumber(
                                    facebookSummary.mediaViews
                                )}
                                helper="Facebook Page"
                            />

                            <SummaryCard
                                icon={
                                    <Icon
                                        type="file"
                                        size={20}
                                    />
                                }
                                label="FB Content"
                                value={formatNumber(
                                    facebookSummary.contents
                                )}
                                helper="Facebook Page"
                            />

                        </div>

                    </div>
                </>
            )}
        </div>
    );
}