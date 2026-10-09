import {
    useEffect,
    useState,
} from "react";

import {
    BarChart3,
    CalendarDays,
    Eye,
    FileText,
    Heart,
    RefreshCw,
} from "lucide-react";

import {
    useNavigate,
} from "react-router-dom";

import * as api from "../../services/api";


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


function formatNumber(value) {
    return new Intl.NumberFormat(
        "id-ID"
    ).format(
        Number(value || 0)
    );
}


function formatDate(value) {

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


export default function FacebookDashboard() {

    const navigate =
        useNavigate();


    const [data, setData] =
        useState({
            connected: false,
            page: null,
            insights: [],
            contents: [],
        });


    const [loading, setLoading] =
        useState(true);


    const [refreshing, setRefreshing] =
        useState(false);


    const [error, setError] =
        useState("");


    const fetchData =
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


                const [
                    statusResult,
                    contentResult,
                    insightResult,
                ] =
                    await Promise.allSettled([

                        api.get(
                            "/api/facebook/status"
                        ),

                        api.get(
                            "/api/facebook/contents"
                        ),

                        api.get(
                            "/api/facebook/insights?metric=page_post_engagements,page_views_total,page_media_view&period=days_28"
                        ),

                    ]);


                const result = {

                    connected:
                        false,

                    page:
                        null,

                    insights:
                        [],

                    contents:
                        [],

                };


                // =================================================
                // FACEBOOK STATUS
                // =================================================

                if (
                    statusResult.status ===
                    "fulfilled"
                ) {

                    const payload =
                        statusResult.value;

                    const status =
                        payload?.data ??
                        payload ??
                        {};

                    result.connected =
                        Boolean(
                            status.connected
                        );

                    result.page =
                        status.selected_page ||
                        status.pages?.[0] ||
                        status.page ||
                        null;

                }


                // =================================================
                // FACEBOOK CONTENT
                // =================================================

                if (
                    contentResult.status ===
                    "fulfilled"
                ) {

                    const payload =
                        contentResult.value;

                    const contentData =
                        payload?.data ??
                        payload ??
                        {};

                    result.contents =
                        contentData.contents ||
                        contentData.data ||
                        [];

                }


                // =================================================
                // FACEBOOK INSIGHT
                // =================================================

                if (
                    insightResult.status ===
                    "fulfilled"
                ) {

                    const payload =
                        insightResult.value;

                    const insightData =
                        payload?.data ??
                        payload ??
                        {};

                    result.insights =
                        insightData.insights ||
                        insightData.data ||
                        [];

                }


                setData(
                    result
                );

            } catch (err) {

                console.error(
                    "Facebook dashboard error:",
                    err
                );

                setError(

                    err?.response
                        ?.data
                        ?.message ||

                    err?.message ||

                    "Gagal mengambil data Facebook."

                );

            } finally {

                setLoading(
                    false
                );

                setRefreshing(
                    false
                );

            }
        };


    // =========================================================
    // INITIAL LOAD
    // =========================================================

    useEffect(() => {

        const timer =
            setTimeout(() => {
                fetchData();
            }, 0);


        return () => {
            clearTimeout(timer);
        };

    }, []);


    // =========================================================
    // METRIC TOTAL
    // =========================================================

    const metricTotal =
        (name) => {

            const metric =
                data.insights.find(
                    (item) =>
                        item?.name ===
                        name
                );


            return (
                metric?.values || []
            ).reduce(

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

        };


    const pageViews =
        metricTotal(
            "page_views_total"
        );


    const mediaViews =
        metricTotal(
            "page_media_view"
        );


    const postEngagements =
        metricTotal(
            "page_post_engagements"
        );


    const contentList =
        Array.isArray(
            data.contents
        )
            ? data.contents
            : [];


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
                        Dashboard Facebook
                    </h1>


                    <p className="mt-2 text-sm text-slate-500">
                        Rekap data Facebook Page yang tersimpan di MAVis.
                    </p>

                </div>


                <div className="flex flex-wrap gap-2">

                    {/* DASHBOARD INSTAGRAM */}

                    <button
                        type="button"
                        onClick={() =>
                            navigate(
                                "/admin/dashboard/instagram"
                            )
                        }
                        className="
                            inline-flex
                            items-center
                            gap-2
                            rounded-xl
                            border
                            border-slate-200
                            bg-white
                            px-4
                            py-2.5
                            text-sm
                            font-semibold
                            text-slate-700
                            shadow-sm
                            hover:bg-slate-50
                        "
                    >

                        <BarChart3
                            size={16}
                        />

                        Dashboard Instagram

                    </button>


                    {/* REFRESH */}

                    <button
                        type="button"
                        onClick={() =>
                            fetchData(true)
                        }
                        disabled={
                            refreshing
                        }
                        className="
                            inline-flex
                            items-center
                            gap-2
                            rounded-xl
                            bg-slate-950
                            px-4
                            py-2.5
                            text-sm
                            font-semibold
                            text-white
                            hover:bg-slate-800
                            disabled:opacity-60
                        "
                    >

                        <RefreshCw
                            size={16}
                            className={
                                refreshing
                                    ? "animate-spin"
                                    : ""
                            }
                        />

                        Refresh

                    </button>

                </div>

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

                    Memuat data Facebook...

                </div>

            ) : (

                <>

                    {/* =================================================
                        FACEBOOK PAGE
                    ================================================= */}

                    <div className="mt-8 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

                        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

                            <div className="flex items-center gap-3">

                                <div className="rounded-xl bg-slate-100 p-3 text-slate-700">

                                    <FacebookMark
                                        size={24}
                                    />

                                </div>


                                <div>

                                    <h2 className="text-lg font-bold text-slate-950">

                                        {data.page?.name ||
                                            "Facebook Page"}

                                    </h2>


                                    <p className="text-xs text-slate-400">

                                        {data.connected
                                            ? "Terhubung ke MAVis"
                                            : "Belum terhubung"}

                                    </p>

                                </div>

                            </div>


                            <div className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-600">

                                <CalendarDays
                                    size={14}
                                />

                                Periode 28 hari

                            </div>

                        </div>

                    </div>


                    {/* =================================================
                        KPI
                    ================================================= */}

                    <div className="mt-5 grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">

                        {/* PAGE VIEWS */}

                        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

                            <div className="flex items-center justify-between">

                                <span className="text-xs font-medium text-slate-400">
                                    Page Views
                                </span>

                                <Eye
                                    size={18}
                                    className="text-slate-500"
                                />

                            </div>


                            <p className="mt-2 text-2xl font-bold text-slate-950">

                                {formatNumber(
                                    pageViews
                                )}

                            </p>

                        </div>


                        {/* MEDIA VIEWS */}

                        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

                            <div className="flex items-center justify-between">

                                <span className="text-xs font-medium text-slate-400">
                                    Media Views
                                </span>

                                <BarChart3
                                    size={18}
                                    className="text-slate-500"
                                />

                            </div>


                            <p className="mt-2 text-2xl font-bold text-slate-950">

                                {formatNumber(
                                    mediaViews
                                )}

                            </p>

                        </div>


                        {/* POST ENGAGEMENT */}

                        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

                            <div className="flex items-center justify-between">

                                <span className="text-xs font-medium text-slate-400">
                                    Post Engagements
                                </span>

                                <Heart
                                    size={18}
                                    className="text-slate-500"
                                />

                            </div>


                            <p className="mt-2 text-2xl font-bold text-slate-950">

                                {formatNumber(
                                    postEngagements
                                )}

                            </p>

                        </div>


                        {/* TOTAL CONTENT */}

                        <div className="rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

                            <div className="flex items-center justify-between">

                                <span className="text-xs font-medium text-slate-400">
                                    Total Content
                                </span>

                                <FileText
                                    size={18}
                                    className="text-slate-500"
                                />

                            </div>


                            <p className="mt-2 text-2xl font-bold text-slate-950">

                                {formatNumber(
                                    contentList.length
                                )}

                            </p>

                        </div>

                    </div>


                    {/* =================================================
                        CONTENT TABLE
                    ================================================= */}

                    <div className="mt-6 rounded-2xl border border-slate-200 bg-white p-5 shadow-sm">

                        <div className="mb-4 flex items-center gap-2">

                            <FileText
                                size={18}
                                className="text-slate-600"
                            />

                            <div>

                                <h2 className="text-base font-bold text-slate-950">
                                    Daftar Content Facebook
                                </h2>

                                <p className="text-xs text-slate-400">
                                    Data posting yang berhasil disimpan
                                </p>

                            </div>

                        </div>


                        <div className="overflow-x-auto">

                            <table className="min-w-full text-left text-sm">

                                <thead>

                                    <tr className="border-b border-slate-200 text-xs text-slate-400">

                                        <th className="px-3 py-3 font-medium">
                                            Tanggal
                                        </th>

                                        <th className="px-3 py-3 font-medium">
                                            Tipe
                                        </th>

                                        <th className="px-3 py-3 font-medium">
                                            Content
                                        </th>

                                        <th className="px-3 py-3 font-medium">
                                            Likes
                                        </th>

                                        <th className="px-3 py-3 font-medium">
                                            Comments
                                        </th>

                                        <th className="px-3 py-3 font-medium">
                                            Shares
                                        </th>

                                    </tr>

                                </thead>


                                <tbody>

                                    {contentList
                                        .slice(
                                            0,
                                            25
                                        )
                                        .map(
                                            (
                                                item
                                            ) => (

                                                <tr
                                                    key={
                                                        item.post_id ||
                                                        item.id
                                                    }
                                                    className="border-b border-slate-100 last:border-0"
                                                >

                                                    <td className="px-3 py-3 text-slate-500">

                                                        {formatDate(
                                                            item.created_time
                                                        )}

                                                    </td>


                                                    <td className="px-3 py-3">

                                                        <span className="rounded-full bg-slate-100 px-2.5 py-1 text-[11px] font-semibold text-slate-600">

                                                            {item.content_type ||
                                                                "-"}

                                                        </span>

                                                    </td>


                                                    <td className="max-w-md px-3 py-3 text-slate-700">

                                                        <div className="line-clamp-2">

                                                            {item.message ||
                                                                "Tidak ada caption"}

                                                        </div>

                                                    </td>


                                                    <td className="px-3 py-3 text-slate-600">

                                                        {formatNumber(
                                                            item.likes
                                                        )}

                                                    </td>


                                                    <td className="px-3 py-3 text-slate-600">

                                                        {formatNumber(
                                                            item.comments
                                                        )}

                                                    </td>


                                                    <td className="px-3 py-3 text-slate-600">

                                                        {formatNumber(
                                                            item.shares
                                                        )}

                                                    </td>

                                                </tr>

                                            )
                                        )}

                                </tbody>

                            </table>

                        </div>

                    </div>


                    {/* =================================================
                        NOTE
                    ================================================= */}

                    <div className="mt-5 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-500">

                        Catatan: metric per-post
                        (likes, comments, shares,
                        views, impressions,
                        engagement) yang tampil
                        di tabel masih mengikuti
                        data yang tersimpan pada
                        tahap sinkronisasi saat ini.

                    </div>

                </>

            )}

        </div>
    );
}