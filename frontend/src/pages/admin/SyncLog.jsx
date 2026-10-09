import {
    useCallback,
    useEffect,
    useMemo,
    useRef,
    useState,
} from "react";

import {
    CheckCircle2,
    Clock3,
    Eye,
    FileText,
    RefreshCw,
    XCircle,
} from "lucide-react";

import * as api from "../../services/api";


// =====================================================
// SYNC LOG
// =====================================================

export default function SyncLog() {

    // =================================================
    // STATE
    // =================================================

    const [
        logs,
        setLogs,
    ] = useState([]);

    const [
        pagination,
        setPagination,
    ] = useState({
        page: 1,
        per_page: 10,
        total: 0,
        pages: 0,
    });

    const [
        loading,
        setLoading,
    ] = useState(true);

    const [
        refreshing,
        setRefreshing,
    ] = useState(false);

    const [
        error,
        setError,
    ] = useState("");

    const [
        selectedLog,
        setSelectedLog,
    ] = useState(null);

    const [
        detailLoading,
        setDetailLoading,
    ] = useState(false);

    const initialLoadRef =
        useRef(false);


    // =================================================
    // FETCH LOGS
    // =================================================

    const fetchLogs = useCallback(
        async (
            page = 1,
            showRefresh = false
        ) => {

            try {

                if (showRefresh) {
                    setRefreshing(true);
                } else {
                    setLoading(true);
                }

                setError("");


                const result =
                    await api.get(
                        `/api/sync-log/?page=${page}&per_page=${pagination.per_page}`
                    );


                console.log(
                    "Sync Log response:",
                    result
                );


                if (
                    result?.success === false
                ) {

                    throw new Error(
                        result?.message ||
                        "Gagal mengambil Sync Log."
                    );

                }


                setLogs(
                    Array.isArray(
                        result?.data
                    )
                        ? result.data
                        : []
                );


                setPagination(
                    result?.pagination ||
                    {
                        page,
                        per_page:
                            pagination.per_page,
                        total: 0,
                        pages: 0,
                    }
                );


            } catch (err) {

                console.error(
                    "Sync Log error:",
                    err
                );


                setError(
                    err?.message ||
                    "Gagal mengambil data Sync Log."
                );


            } finally {

                setLoading(false);
                setRefreshing(false);

            }

        },
        [
            pagination.per_page,
        ]
    );


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

        fetchLogs(1);


    }, [
        fetchLogs,
    ]);


    // =================================================
    // DETAIL
    // =================================================

    const handleViewDetail = async (
        id
    ) => {

        try {

            setDetailLoading(true);
            setError("");


            const result =
                await api.get(
                    `/api/sync-log/${id}`
                );


            if (
                result?.success === false
            ) {

                throw new Error(
                    result?.message ||
                    "Detail Sync Log gagal diambil."
                );

            }


            setSelectedLog(
                result?.data ||
                null
            );


        } catch (err) {

            console.error(
                "Sync Log detail error:",
                err
            );


            setError(
                err?.message ||
                "Gagal mengambil detail Sync Log."
            );


        } finally {

            setDetailLoading(false);

        }

    };


    // =================================================
    // PAGINATION
    // =================================================

    const currentPage =
        Number(
            pagination?.page
        ) || 1;

    const totalPages =
        Number(
            pagination?.pages
        ) || 0;


    const canPrevious =
        currentPage > 1;


    const canNext =
        currentPage < totalPages;


    // =================================================
    // STATS
    // =================================================

    const stats = useMemo(
        () => {

            const total =
                Number(
                    pagination?.total
                ) || 0;


            const success =
                logs.filter(
                    (
                        item
                    ) =>
                        normalizeStatus(
                            item?.status
                        ) === "success"
                ).length;


            const failed =
                logs.filter(
                    (
                        item
                    ) =>
                        normalizeStatus(
                            item?.status
                        ) === "failed"
                ).length;


            const totalPosts =
                logs.reduce(
                    (
                        totalValue,
                        item
                    ) =>
                        totalValue +
                        Number(
                            item?.total_posts
                            || 0
                        ),
                    0
                );


            return {

                total,

                success,

                failed,

                totalPosts,

            };

        },
        [
            logs,
            pagination?.total,
        ]
    );


    // =================================================
    // LOADING
    // =================================================

    if (loading) {

        return (

            <div className="sync-log-loading">

                <div className="sync-log-spinner" />

                <span>
                    Memuat riwayat sinkronisasi...
                </span>

            </div>

        );

    }


    // =================================================
    // PAGE
    // =================================================

    return (

        <div className="sync-log-page">


            {/* =============================================
                HEADER
            ============================================= */}

            <div className="sync-log-header">

                <div>

                    <div className="sync-log-breadcrumb">

                        <RefreshCw
                            size={15}
                        />

                        <span>
                            Sync Log
                        </span>

                    </div>


                    <h2>
                        Riwayat Sinkronisasi
                    </h2>


                    <p>
                        Memantau riwayat proses sinkronisasi
                        data dari Meta ke sistem MAVis.
                    </p>

                </div>


                <button
                    type="button"
                    className="sync-log-refresh-button"
                    onClick={() =>
                        fetchLogs(
                            currentPage,
                            true
                        )
                    }
                    disabled={
                        refreshing
                    }
                >

                    <RefreshCw
                        size={15}
                        className={
                            refreshing
                                ? "sync-log-spin"
                                : ""
                        }
                    />

                    {refreshing
                        ? "Memuat..."
                        : "Refresh"}

                </button>

            </div>


            {/* =============================================
                ERROR
            ============================================= */}

            {error && (

                <div className="sync-log-error">

                    <span>
                        {error}
                    </span>


                    <button
                        type="button"
                        onClick={() =>
                            fetchLogs(
                                currentPage,
                                true
                            )
                        }
                    >
                        Coba lagi
                    </button>

                </div>

            )}


            {/* =============================================
                SUMMARY
            ============================================= */}

            <div className="sync-log-summary-grid">

                <SummaryCard
                    icon={
                        FileText
                    }
                    label="Total Sinkronisasi"
                    value={
                        formatNumber(
                            stats.total
                        )
                    }
                />


                <SummaryCard
                    icon={
                        CheckCircle2
                    }
                    label="Berhasil"
                    value={
                        formatNumber(
                            stats.success
                        )
                }
                />


                <SummaryCard
                    icon={
                        XCircle
                    }
                    label="Gagal"
                    value={
                        formatNumber(
                            stats.failed
                        )
                    }
                />


                <SummaryCard
                    icon={
                        FileText
                    }
                    label="Post pada Halaman"
                    value={
                        formatNumber(
                            stats.totalPosts
                        )
                    }
                />

            </div>


            {/* =============================================
                TABLE
            ============================================= */}

            <section className="sync-log-panel">

                <div className="sync-log-panel-header">

                    <div>

                        <span className="sync-log-eyebrow">
                            SYNCHRONIZATION HISTORY
                        </span>

                        <h3>
                            Riwayat Sync
                        </h3>

                    </div>


                    <span className="sync-log-total">
                        {formatNumber(
                            pagination?.total
                        )} data
                    </span>

                </div>


                <div className="sync-log-table-wrapper">

                    {logs.length === 0 ? (

                        <div className="sync-log-empty">

                            <Clock3
                                size={25}
                                strokeWidth={1.6}
                            />

                            <strong>
                                Belum ada riwayat sinkronisasi
                            </strong>

                            <span>
                                Riwayat proses sync Meta akan
                                muncul di halaman ini.
                            </span>

                        </div>

                    ) : (

                        <table className="sync-log-table">

                            <thead>

                                <tr>

                                    <th>
                                        Waktu
                                    </th>

                                    <th>
                                        Status
                                    </th>

                                    <th>
                                        Total Post
                                    </th>

                                    <th>
                                        Pesan
                                    </th>

                                    <th>
                                        Aksi
                                    </th>

                                </tr>

                            </thead>


                            <tbody>

                                {logs.map(
                                    (
                                        item
                                    ) => {

                                        const status =
                                            normalizeStatus(
                                                item?.status
                                            );


                                        return (

                                            <tr
                                                key={
                                                    item?.id_sync
                                                }
                                            >

                                                <td>

                                                    <div className="sync-log-date">

                                                        <strong>
                                                            {
                                                                formatDate(
                                                                    item?.sync_date
                                                                )
                                                            }
                                                        </strong>

                                                        <span>
                                                            {
                                                                formatTime(
                                                                    item?.sync_date
                                                                )
                                                            }
                                                        </span>

                                                    </div>

                                                </td>


                                                <td>

                                                    <StatusBadge
                                                        status={
                                                            status
                                                        }
                                                        value={
                                                            item?.status
                                                        }
                                                    />

                                                </td>


                                                <td>

                                                    <span className="sync-log-post-count">

                                                        {
                                                            formatNumber(
                                                                item?.total_posts
                                                            )
                                                        }

                                                    </span>

                                                </td>


                                                <td>

                                                    <span className="sync-log-message">

                                                        {
                                                            item?.message ||
                                                            "-"
                                                        }

                                                    </span>

                                                </td>


                                                <td>

                                                    <button
                                                        type="button"
                                                        className="sync-log-view-button"
                                                        onClick={() =>
                                                            handleViewDetail(
                                                                item?.id_sync
                                                            )
                                                        }
                                                        disabled={
                                                            detailLoading
                                                        }
                                                    >

                                                        <Eye
                                                            size={14}
                                                        />

                                                        Detail

                                                    </button>

                                                </td>

                                            </tr>

                                        );

                                    }
                                )}

                            </tbody>

                        </table>

                    )}

                </div>


                {/* =============================================
                    PAGINATION
                ============================================= */}

                {totalPages > 1 && (

                    <div className="sync-log-pagination">

                        <span>

                            Halaman{" "}

                            <strong>
                                {currentPage}
                            </strong>

                            {" "}dari{" "}

                            <strong>
                                {totalPages}
                            </strong>

                        </span>


                        <div>

                            <button
                                type="button"
                                onClick={() =>
                                    fetchLogs(
                                        currentPage - 1
                                    )
                                }
                                disabled={
                                    !canPrevious ||
                                    refreshing
                                }
                            >
                                Sebelumnya
                            </button>


                            <button
                                type="button"
                                onClick={() =>
                                    fetchLogs(
                                        currentPage + 1
                                    )
                                }
                                disabled={
                                    !canNext ||
                                    refreshing
                                }
                            >
                                Berikutnya
                            </button>

                        </div>

                    </div>

                )}

            </section>


            {/* =============================================
                DETAIL MODAL
            ============================================= */}

            {selectedLog && (

                <div
                    className="sync-log-modal-backdrop"
                    onMouseDown={() =>
                        setSelectedLog(null)
                    }
                >

                    <div
                        className="sync-log-modal"
                        onMouseDown={(
                            event
                        ) =>
                            event.stopPropagation()
                        }
                    >

                        <div className="sync-log-modal-header">

                            <div>

                                <span className="sync-log-eyebrow">
                                    SYNC DETAIL
                                </span>

                                <h3>
                                    Detail Sinkronisasi
                                </h3>

                            </div>


                            <button
                                type="button"
                                onClick={() =>
                                    setSelectedLog(
                                        null
                                    )
                                }
                                className="sync-log-modal-close"
                            >
                                ×
                            </button>

                        </div>


                        <div className="sync-log-detail-grid">

                            <DetailItem
                                label="ID Sync"
                                value={
                                    formatNumber(
                                        selectedLog?.id_sync
                                    )
                                }
                            />


                            <DetailItem
                                label="Tanggal"
                                value={
                                    formatDateTime(
                                        selectedLog?.sync_date
                                    )
                                }
                            />


                            <DetailItem
                                label="Total Post"
                                value={
                                    formatNumber(
                                        selectedLog?.total_posts
                                    )
                                }
                            />


                            <DetailItem
                                label="Status"
                                value={
                                    selectedLog?.status ||
                                    "-"
                                }
                            />

                        </div>


                        <div className="sync-log-detail-message">

                            <span>
                                Pesan
                            </span>

                            <p>
                                {
                                    selectedLog?.message ||
                                    "-"
                                }
                            </p>

                        </div>

                    </div>

                </div>

            )}

        </div>

    );

}


// =====================================================
// SUMMARY CARD
// =====================================================

function SummaryCard({
    icon: Icon,
    label,
    value,
}) {

    return (

        <div className="sync-log-summary-card">

            <div className="sync-log-summary-icon">

                <Icon
                    size={18}
                    strokeWidth={1.8}
                />

            </div>


            <span>
                {label}
            </span>


            <strong>
                {value}
            </strong>

        </div>

    );

}


// =====================================================
// STATUS BADGE
// =====================================================

function StatusBadge({
    status,
    value,
}) {

    const normalized =
        normalizeStatus(
            status
        );


    const isSuccess =
        normalized === "success";


    const isFailed =
        normalized === "failed";


    return (

        <span
            className={
                isSuccess
                    ? "sync-log-status success"
                    : isFailed
                        ? "sync-log-status failed"
                        : "sync-log-status running"
            }
        >

            {isSuccess ? (

                <CheckCircle2
                    size={13}
                />

            ) : isFailed ? (

                <XCircle
                    size={13}
                />

            ) : (

                <Clock3
                    size={13}
                />

            )}


            {
                value ||
                (
                    isSuccess
                        ? "Berhasil"
                        : isFailed
                            ? "Gagal"
                            : "Berjalan"
                )
            }

        </span>

    );

}


// =====================================================
// DETAIL ITEM
// =====================================================

function DetailItem({
    label,
    value,
}) {

    return (

        <div className="sync-log-detail-item">

            <span>
                {label}
            </span>

            <strong>
                {value}
            </strong>

        </div>

    );

}


// =====================================================
// HELPERS
// =====================================================

function normalizeStatus(
    value
) {

    const status =
        String(
            value ||
            ""
        )
        .trim()
        .toLowerCase();


    if (
        [
            "success",
            "successful",
            "berhasil",
            "completed",
            "complete",
            "ok",
        ].includes(
            status
        )
    ) {
        return "success";
    }


    if (
        [
            "failed",
            "failure",
            "gagal",
            "error",
        ].includes(
            status
        )
    ) {
        return "failed";
    }


    return "running";

}


function formatNumber(
    value
) {

    const number =
        Number(
            value
        );


    if (
        Number.isNaN(
            number
        )
    ) {
        return "0";
    }


    return new Intl.NumberFormat(
        "id-ID"
    ).format(
        number
    );

}


function formatDate(
    value
) {

    if (!value) {
        return "-";
    }


    const date =
        new Date(
            value
        );


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
        return "-";
    }


    return date.toLocaleDateString(
        "id-ID",
        {
            day: "2-digit",
            month: "2-digit",
            year: "numeric",
        }
    );

}


function formatTime(
    value
) {

    if (!value) {
        return "-";
    }


    const date =
        new Date(
            value
        );


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
        return "-";
    }


    return date.toLocaleTimeString(
        "id-ID",
        {
            hour: "2-digit",
            minute: "2-digit",
        }
    );

}


function formatDateTime(
    value
) {

    if (!value) {
        return "-";
    }


    const date =
        new Date(
            value
        );


    if (
        Number.isNaN(
            date.getTime()
        )
    ) {
        return "-";
    }


    return date.toLocaleString(
        "id-ID",
        {
            day: "2-digit",
            month: "long",
            year: "numeric",
            hour: "2-digit",
            minute: "2-digit",
        }
    );

}
