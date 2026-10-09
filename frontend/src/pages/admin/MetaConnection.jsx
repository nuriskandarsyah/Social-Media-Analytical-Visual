import { useCallback, useEffect, useRef, useState } from "react";
import * as api from "../../services/api";

// =====================================================
// CONFIG
// =====================================================

const META_API_URL =
    "https://stuffed-awoke-enlarging.ngrok-free.dev";

const LOCAL_API_URL =
    "http://127.0.0.1:5000";


// =====================================================
// TOKEN
// =====================================================

const getAccessToken = () =>
    localStorage.getItem("access_token") ||
    localStorage.getItem("token") ||
    sessionStorage.getItem("access_token") ||
    sessionStorage.getItem("token") ||
    "";


// =====================================================
// META / INSTAGRAM REQUEST
// =====================================================

const metaFetch = async (path, options = {}) => {

    const token = getAccessToken();

    const response = await fetch(
        `${META_API_URL}${path}`,
        {
            ...options,
            headers: {
                ...(options.headers || {}),
                ...(token
                    ? {
                        Authorization:
                            `Bearer ${token}`,
                    }
                    : {}
                ),
                "ngrok-skip-browser-warning": "1",
            },
            credentials: "include",
        }
    );

    const contentType =
        response.headers.get("content-type") || "";

    const data =
        contentType.includes("application/json")
            ? await response.json()
            : await response.text();

    if (!response.ok) {

        const message =
            typeof data === "object"
                ? data?.message || data?.error
                : data;

        throw new Error(
            message ||
            `Request gagal (${response.status})`
        );

    }

    return data;
};


// =====================================================
// LOCAL FACEBOOK REQUEST
// =====================================================

const facebookGet = async (path) => {

    const token = getAccessToken();

    const response = await fetch(
        `${LOCAL_API_URL}${path}`,
        {
            method: "GET",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                ...(token
                    ? {
                        Authorization:
                            `Bearer ${token}`,
                    }
                    : {}
                ),
            },
        }
    );

    const contentType =
        response.headers.get("content-type") || "";

    const data =
        contentType.includes("application/json")
            ? await response.json()
            : await response.text();

    if (!response.ok) {

        const message =
            typeof data === "object"
                ? data?.message || data?.error
                : data;

        throw new Error(
            message ||
            `Request Facebook gagal (${response.status})`
        );

    }

    return data;
};


// =====================================================
// LOCAL FACEBOOK POST
// =====================================================

const facebookPost = async (
    path,
    body = {}
) => {

    const token = getAccessToken();

    const response = await fetch(
        `${LOCAL_API_URL}${path}`,
        {
            method: "POST",
            credentials: "include",
            headers: {
                "Content-Type": "application/json",
                ...(token
                    ? {
                        Authorization:
                            `Bearer ${token}`,
                    }
                    : {}
                ),
            },
            body: JSON.stringify(body),
        }
    );

    const contentType =
        response.headers.get("content-type") || "";

    const data =
        contentType.includes("application/json")
            ? await response.json()
            : await response.text();

    if (!response.ok) {

        const message =
            typeof data === "object"
                ? data?.message || data?.error
                : data;

        throw new Error(
            message ||
            `Request Facebook gagal (${response.status})`
        );

    }

    return data;
};


// =====================================================
// COMPONENT
// =====================================================

const MetaConnection = () => {

    // =================================================
    // INSTAGRAM STATE
    // =================================================

    const [instagram, setInstagram] = useState({
        connected: false,
        account: null,
        expires_at: null,
    });


    // =================================================
    // FACEBOOK STATE
    // =================================================

    const [facebook, setFacebook] = useState({
        connected: false,
        facebook_user_id: null,
        facebook_user_name: null,
        expires_in: null,
        pages: [],
        selected_page: null,
    });


    // =================================================
    // UI STATE
    // =================================================

    const [loading, setLoading] = useState(true);

    const [activeAction, setActiveAction] =
        useState("");

    const [error, setError] = useState("");

    const [successMessage, setSuccessMessage] =
        useState("");


    // =================================================
    // POPUP REFS
    // =================================================

    const popupRef = useRef(null);


    // =================================================
    // CLEAR MESSAGE
    // =================================================

    const clearMessages = () => {

        setError("");

        setSuccessMessage("");

    };


    // =================================================
    // NORMALIZE INSTAGRAM
    // =================================================

    const normalizeInstagram = (
        response
    ) => {

        const data =
            response?.data?.data ||
            response?.data ||
            response ||
            {};

        return {
            connected:
                data?.connected === true ||
                data?.is_connected === true ||
                data?.instagram_connected === true,

            account:
                data?.account ||
                data?.instagram_account ||
                data?.profile ||
                data?.user ||
                null,

            expires_at:
                data?.expires_at ||
                null,
        };

    };


    // =================================================
    // LOAD INSTAGRAM STATUS
    // =================================================

    const loadInstagramStatus = useCallback(
        async () => {

            try {

                console.log(
                    "===================================="
                );

                console.log(
                    "CEK STATUS INSTAGRAM"
                );

                console.log(
                    "===================================="
                );


                const response =
                    await metaFetch(
                        "/api/meta/status"
                    );


                const normalized =
                    normalizeInstagram(
                        response
                    );


                console.log(
                    "INSTAGRAM STATUS:",
                    normalized
                );


                setInstagram(
                    normalized
                );

            } catch (err) {

                console.error(
                    "Instagram status error:",
                    err
                );

                // Jangan menghapus state koneksi hanya karena
                // request status gagal.

                throw err;

            }

        },
        []
    );


    // =================================================
    // LOAD FACEBOOK STATUS
    // =================================================

    const loadFacebookStatus = useCallback(
        async () => {

            try {

                console.log(
                    "===================================="
                );

                console.log(
                    "CEK STATUS FACEBOOK"
                );

                console.log(
                    "===================================="
                );


                const response =
                    await facebookGet(
                        "/api/facebook/status"
                    );


                const data =
                    response?.data ||
                    response ||
                    {};


                const normalized = {

                    connected:
                        data?.connected === true,

                    facebook_user_id:
                        data?.facebook_user_id ||
                        null,

                    facebook_user_name:
                        data?.facebook_user_name ||
                        null,

                    expires_in:
                        data?.expires_in ||
                        null,

                    pages:
                        Array.isArray(data?.pages)
                            ? data.pages
                            : [],

                    selected_page:
                        data?.selected_page ||
                        null,

                };


                console.log(
                    "FACEBOOK STATUS:",
                    normalized
                );


                setFacebook(
                    normalized
                );

            } catch (err) {

                console.error(
                    "Facebook status error:",
                    err
                );

                throw err;

            }

        },
        []
    );


    // =================================================
    // LOAD ALL STATUS
    // =================================================

    const loadAllStatus = useCallback(
        async () => {

            setLoading(true);

            clearMessages();


            const results =
                await Promise.allSettled([
                    loadInstagramStatus(),
                    loadFacebookStatus(),
                ]);


            const failed =
                results.filter(
                    (item) =>
                        item.status === "rejected"
                );


            // Tampilkan error hanya jika memang ada request
            // yang gagal. State koneksi sebelumnya tidak dihapus.
            if (failed.length > 0) {

                console.warn(
                    "Sebagian status koneksi gagal diperiksa.",
                    failed
                );

                setError(
                    "Sebagian status koneksi tidak dapat diperiksa. " +
                    "Status koneksi sebelumnya tetap dipertahankan."
                );

            }


            setLoading(false);

        },
        [
            loadInstagramStatus,
            loadFacebookStatus,
        ]
    );


    // =================================================
    // INITIAL LOAD
    // =================================================

    useEffect(() => {

        const timeoutId = setTimeout(() => {
            loadAllStatus();
        }, 0);

        return () => clearTimeout(timeoutId);

    }, [loadAllStatus]);


    // =================================================
    // OAUTH MESSAGE HANDLER
    // =================================================

    useEffect(() => {

        const handleMessage = async (
            event
        ) => {

            const allowedOrigins = [
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                META_API_URL,
            ];


            if (
                !allowedOrigins.includes(
                    event.origin
                )
            ) {
                return;
            }


            const message =
                event.data || {};


            if (
                message.type ===
                "INSTAGRAM_OAUTH_SUCCESS"
            ) {

                setActiveAction("");

                clearMessages();

                setInstagram((current) => ({
                    ...current,
                    connected: true,
                    account:
                        message?.data?.account ||
                        current.account,
                }));


                try {

                    await loadInstagramStatus();

                } catch (err) {

                    console.warn(
                        "Reload Instagram status gagal:",
                        err
                    );

                }


                setSuccessMessage(
                    "Koneksi Instagram berhasil."
                );

                return;
            }


            if (
                message.type ===
                "INSTAGRAM_OAUTH_ERROR"
            ) {

                setActiveAction("");

                setError(
                    message?.error ||
                    message?.message ||
                    "Koneksi Instagram gagal."
                );

                return;
            }


            if (
                message.type ===
                "FACEBOOK_OAUTH_SUCCESS"
            ) {

                setActiveAction("");

                clearMessages();

                setFacebook((current) => ({
                    ...current,
                    connected: true,
                    facebook_user_id:
                        message?.data?.facebook_user_id ||
                        current.facebook_user_id,
                    facebook_user_name:
                        message?.data?.facebook_user_name ||
                        current.facebook_user_name,
                    pages:
                        Array.isArray(
                            message?.data?.pages
                        )
                            ? message.data.pages
                            : current.pages,
                    selected_page:
                        message?.data?.selected_page ||
                        current.selected_page,
                }));


                try {

                    await loadFacebookStatus();

                } catch (err) {

                    console.warn(
                        "Reload Facebook status gagal:",
                        err
                    );

                }


                setSuccessMessage(
                    "Koneksi Facebook berhasil."
                );

                return;
            }


            if (
                message.type ===
                "FACEBOOK_OAUTH_ERROR"
            ) {

                setActiveAction("");

                setError(
                    message?.error ||
                    message?.message ||
                    "Koneksi Facebook gagal."
                );

            }

        };


        window.addEventListener(
            "message",
            handleMessage
        );


        return () => {

            window.removeEventListener(
                "message",
                handleMessage
            );

        };

    }, [
        loadInstagramStatus,
        loadFacebookStatus,
    ]);


    // =================================================
    // OPEN OAUTH POPUP
    // =================================================

    const openOAuthPopup = async ({
        platform,
        getAuthorizationUrl,
        providerUrlPrefix,
    }) => {

        clearMessages();

        setActiveAction(
            `${platform}-connect`
        );


        // Popup dibuka langsung dari event klik supaya tidak
        // terkena popup blocker browser.
        const popup = window.open(
            "",
            `mavis_${platform}_oauth`,
            [
                "width=600",
                "height=720",
                "left=200",
                "top=80",
                "resizable=yes",
                "scrollbars=yes",
            ].join(",")
        );


        if (!popup) {

            setActiveAction("");

            setError(
                "Popup diblokir browser. Izinkan popup untuk MAVis."
            );

            return;

        }


        popupRef.current =
            popup;


        try {

            popup.document.write(`
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>MAVis - ${platform}</title>
                    <style>
                        body {
                            margin: 0;
                            height: 100vh;
                            display: flex;
                            align-items: center;
                            justify-content: center;
                            font-family: Arial, sans-serif;
                            background: #f8fafc;
                        }
                        .container {
                            text-align: center;
                        }
                        .spinner {
                            width: 42px;
                            height: 42px;
                            border: 4px solid #e5e7eb;
                            border-top-color: #111827;
                            border-radius: 50%;
                            animation: spin 1s linear infinite;
                            margin: 0 auto 20px;
                        }
                        @keyframes spin {
                            to { transform: rotate(360deg); }
                        }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="spinner"></div>
                        <h3>Menghubungkan ${platform}...</h3>
                        <p style="color:#64748b;font-size:14px;">
                            Menyiapkan halaman login ${platform}
                        </p>
                    </div>
                </body>
                </html>
            `);

            popup.document.close();

        } catch (err) {

            console.warn(
                "Popup loading gagal ditulis:",
                err
            );

        }


        try {

            const response =
                await getAuthorizationUrl();

            const authorizationUrl =
                response?.data?.authorization_url ||
                response?.authorization_url ||
                response?.data?.data?.authorization_url ||
                null;


            if (!authorizationUrl) {

                throw new Error(
                    response?.message ||
                    "Authorization URL tidak ditemukan."
                );

            }


            if (
                !authorizationUrl.startsWith(
                    providerUrlPrefix
                )
            ) {

                throw new Error(
                    `Authorization URL ${platform} tidak valid.`
                );

            }


            popup.location.href =
                authorizationUrl;

            popup.focus();

        } catch (err) {

            console.error(
                `${platform} OAuth error:`,
                err
            );

            try {

                if (
                    popup &&
                    !popup.closed
                ) {
                    popup.close();
                }

            } catch (closeError) {

                console.warn(
                    "Popup close error:",
                    closeError
                );

            }

            setActiveAction("");

            setError(
                err?.message ||
                `Gagal membuka koneksi ${platform}.`
            );

        }

    };


    // =================================================
    // CONNECT INSTAGRAM
    // =================================================

    const handleInstagramConnect = () => {

        return openOAuthPopup({
            platform: "Instagram",

            getAuthorizationUrl:
                () =>
                    api.metaGet(
                        "/api/meta/connect"
                    ),

            providerUrlPrefix:
                "https://www.instagram.com/",
        });

    };


    // =================================================
    // CONNECT FACEBOOK
    // =================================================

    const handleFacebookConnect = () => {

        return openOAuthPopup({
            platform: "Facebook",

            getAuthorizationUrl:
                () =>
                    facebookGet(
                        "/api/facebook/connect"
                    ),

            providerUrlPrefix:
                "https://www.facebook.com/",
        });

    };


    // =================================================
    // DISCONNECT INSTAGRAM
    // =================================================

    const handleInstagramDisconnect = async () => {

        const confirmed = window.confirm(
            "Putuskan koneksi Instagram dari MAVis?"
        );

        if (!confirmed) {
            return;
        }


        try {

            clearMessages();

            setActiveAction(
                "instagram-disconnect"
            );


            await api.metaPost(
                "/api/meta/disconnect"
            );


            setInstagram({
                connected: false,
                account: null,
                expires_at: null,
            });


            setSuccessMessage(
                "Koneksi Instagram berhasil diputuskan."
            );

        } catch (err) {

            console.error(
                "Instagram disconnect error:",
                err
            );

            setError(
                err?.message ||
                "Gagal memutuskan koneksi Instagram."
            );

        } finally {

            setActiveAction("");

        }

    };


    // =================================================
    // SYNCHRONIZE INSTAGRAM
    // =================================================

    const handleInstagramSynchronize = async () => {

        try {

            clearMessages();

            setActiveAction(
                "instagram-sync"
            );


            await api.metaPost(
                "/api/meta/synchronize"
            );


            await loadInstagramStatus();


            setSuccessMessage(
                "Sinkronisasi Instagram berhasil."
            );

        } catch (err) {

            console.error(
                "Instagram sync error:",
                err
            );

            setError(
                err?.message ||
                "Sinkronisasi Instagram gagal."
            );

        } finally {

            setActiveAction("");

        }

    };


    // =================================================
    // SYNCHRONIZE FACEBOOK
    // =================================================

    const handleFacebookSynchronize = async () => {

        try {

            clearMessages();

            setActiveAction(
                "facebook-sync"
            );


            await facebookPost(
                "/api/facebook/sync",
                {}
            );


            await loadFacebookStatus();


            setSuccessMessage(
                "Sinkronisasi Facebook berhasil."
            );

        } catch (err) {

            console.error(
                "Facebook sync error:",
                err
            );

            setError(
                err?.message ||
                "Sinkronisasi Facebook gagal."
            );

        } finally {

            setActiveAction("");

        }

    };


    // =================================================
    // SELECT FACEBOOK PAGE
    // =================================================

    const handleSelectFacebookPage = async (
        event
    ) => {

        const pageId =
            event.target.value;


        if (!pageId) {
            return;
        }


        try {

            clearMessages();

            setActiveAction(
                "facebook-select-page"
            );


            const response =
                await facebookPost(
                    "/api/facebook/select-page",
                    {
                        page_id: pageId,
                    }
                );


            const selected =
                response?.data ||
                null;


            setFacebook((current) => ({
                ...current,
                selected_page:
                    selected ||
                    current.pages.find(
                        (page) =>
                            String(page.id) ===
                            String(pageId)
                    ) ||
                    current.selected_page,
            }));


            setSuccessMessage(
                "Facebook Page berhasil dipilih."
            );

        } catch (err) {

            console.error(
                "Facebook select page error:",
                err
            );

            setError(
                err?.message ||
                "Gagal memilih Facebook Page."
            );

        } finally {

            setActiveAction("");

        }

    };


    // =================================================
    // FORMAT
    // =================================================

    const formatNumber = (
        value
    ) => {

        if (
            value === null ||
            value === undefined ||
            value === ""
        ) {
            return "-";
        }

        return new Intl.NumberFormat(
            "id-ID"
        ).format(
            Number(value)
        );

    };


    const formatExpires = (
        value
    ) => {

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

    };


    const isBusy =
        activeAction !== "";


    // =================================================
    // RENDER
    // =================================================

    return (

        <div
            className="
                p-6
            "
        >

            <div
                className="
                    mx-auto
                    max-w-6xl
                "
            >

                {/* =================================================
                    HEADER
                ================================================= */}

                <div
                    className="
                        mb-6
                        flex
                        flex-col
                        gap-3
                        md:flex-row
                        md:items-end
                        md:justify-between
                    "
                >

                    <div>

                        <div
                            className="
                                text-sm
                                font-medium
                                text-gray-400
                            "
                        >
                            MAVis
                        </div>

                        <h1
                            className="
                                mt-1
                                text-3xl
                                font-bold
                                text-gray-950
                            "
                        >
                            Meta Connection
                        </h1>

                        <p
                            className="
                                mt-2
                                max-w-2xl
                                text-sm
                                leading-6
                                text-gray-500
                            "
                        >
                            Kelola koneksi Instagram dan Facebook
                            pada akun MAVis yang sedang login.
                        </p>

                    </div>


                    <button
                        type="button"
                        onClick={loadAllStatus}
                        disabled={loading || isBusy}
                        className="
                            inline-flex
                            items-center
                            justify-center
                            rounded-xl
                            border
                            border-gray-200
                            bg-white
                            px-4
                            py-2.5
                            text-sm
                            font-semibold
                            text-gray-700
                            shadow-sm
                            hover:bg-gray-50
                            disabled:cursor-not-allowed
                            disabled:opacity-50
                        "
                    >
                        {loading
                            ? "Memuat..."
                            : "Refresh Status"
                        }
                    </button>

                </div>


                {/* =================================================
                    GLOBAL MESSAGE
                ================================================= */}

                {successMessage && (

                    <div
                        className="
                            mb-5
                            rounded-xl
                            border
                            border-green-200
                            bg-green-50
                            p-4
                            text-sm
                            text-green-700
                        "
                    >
                        {successMessage}
                    </div>

                )}


                {error && (

                    <div
                        className="
                            mb-5
                            rounded-xl
                            border
                            border-red-200
                            bg-red-50
                            p-4
                            text-sm
                            text-red-700
                        "
                    >

                        <div className="font-semibold">
                            Koneksi tidak dapat diproses
                        </div>

                        <div className="mt-1">
                            {error}
                        </div>

                    </div>

                )}


                {/* =================================================
                    CONNECTION CARDS
                ================================================= */}

                <div
                    className="
                        grid
                        gap-6
                        lg:grid-cols-2
                    "
                >

                    {/* =================================================
                        INSTAGRAM
                    ================================================= */}

                    <div
                        className="
                            overflow-hidden
                            rounded-2xl
                            border
                            border-gray-200
                            bg-white
                            shadow-sm
                        "
                    >

                        <div
                            className="
                                flex
                                items-center
                                justify-between
                                border-b
                                border-gray-100
                                p-6
                            "
                        >

                            <div
                                className="
                                    flex
                                    items-center
                                    gap-4
                                "
                            >

                                <div
                                    className="
                                        flex
                                        h-14
                                        w-14
                                        items-center
                                        justify-center
                                        rounded-2xl
                                        bg-gradient-to-br
                                        from-purple-600
                                        via-pink-500
                                        to-orange-400
                                        text-lg
                                        font-bold
                                        text-white
                                    "
                                >
                                    IG
                                </div>

                                <div>

                                    <h2
                                        className="
                                            text-lg
                                            font-bold
                                            text-gray-900
                                        "
                                    >
                                        Instagram
                                    </h2>

                                    <p
                                        className="
                                            text-sm
                                            text-gray-500
                                        "
                                    >
                                        Instagram Business
                                    </p>

                                </div>

                            </div>


                            <div
                                className={
                                    `
                                    rounded-full
                                    px-3
                                    py-1
                                    text-xs
                                    font-semibold
                                    ${
                                        instagram.connected
                                            ? "bg-green-100 text-green-700"
                                            : "bg-gray-100 text-gray-500"
                                    }
                                    `
                                }
                            >
                                {instagram.connected
                                    ? "Terhubung"
                                    : "Belum terhubung"
                                }
                            </div>

                        </div>


                        <div className="p-6">

                            {!instagram.connected ? (

                                <div>

                                    <div
                                        className="
                                            rounded-xl
                                            bg-gray-50
                                            p-5
                                        "
                                    >

                                        <h3
                                            className="
                                                font-semibold
                                                text-gray-900
                                            "
                                        >
                                            Instagram belum terhubung
                                        </h3>

                                        <p
                                            className="
                                                mt-2
                                                text-sm
                                                leading-6
                                                text-gray-600
                                            "
                                        >
                                            Hubungkan akun Instagram Business
                                            untuk mengambil data insight,
                                            konten, dan analisis MAVis.
                                        </p>

                                    </div>


                                    <button
                                        type="button"
                                        onClick={
                                            handleInstagramConnect
                                        }
                                        disabled={
                                            isBusy
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
                                            disabled:cursor-not-allowed
                                            disabled:opacity-50
                                        "
                                    >
                                        {activeAction ===
                                            "Instagram-connect"
                                            ? "Menghubungkan..."
                                            : "Hubungkan Instagram"
                                        }
                                    </button>

                                </div>

                            ) : (

                                <div>

                                    <div
                                        className="
                                            rounded-xl
                                            border
                                            border-green-200
                                            bg-green-50
                                            p-5
                                        "
                                    >

                                        <div
                                            className="
                                                flex
                                                items-center
                                                gap-3
                                            "
                                        >

                                            <div
                                                className="
                                                    flex
                                                    h-10
                                                    w-10
                                                    items-center
                                                    justify-center
                                                    rounded-full
                                                    bg-green-500
                                                    font-bold
                                                    text-white
                                                "
                                            >
                                                ✓
                                            </div>

                                            <div>
                                                <div
                                                    className="
                                                        font-semibold
                                                        text-green-800
                                                    "
                                                >
                                                    Instagram terhubung
                                                </div>

                                                <div
                                                    className="
                                                        mt-1
                                                        text-sm
                                                        text-green-700
                                                    "
                                                >
                                                    {instagram.account?.username
                                                        ? `@${instagram.account.username}`
                                                        : "Akun Instagram Business"
                                                    }
                                                </div>
                                            </div>

                                        </div>

                                    </div>


                                    <div
                                        className="
                                            mt-5
                                            grid
                                            grid-cols-2
                                            gap-4
                                            md:grid-cols-4
                                        "
                                    >

                                        <div
                                            className="
                                                rounded-xl
                                                border
                                                p-4
                                            "
                                        >
                                            <div
                                                className="text-xs text-gray-500"
                                            >
                                                Followers
                                            </div>
                                            <div
                                                className="mt-1 font-semibold text-gray-900"
                                            >
                                                {formatNumber(
                                                    instagram.account?.followers_count
                                                )}
                                            </div>
                                        </div>

                                        <div
                                            className="
                                                rounded-xl
                                                border
                                                p-4
                                            "
                                        >
                                            <div
                                                className="text-xs text-gray-500"
                                            >
                                                Following
                                            </div>
                                            <div
                                                className="mt-1 font-semibold text-gray-900"
                                            >
                                                {formatNumber(
                                                    instagram.account?.follows_count
                                                )}
                                            </div>
                                        </div>

                                        <div
                                            className="
                                                rounded-xl
                                                border
                                                p-4
                                            "
                                        >
                                            <div
                                                className="text-xs text-gray-500"
                                            >
                                                Media
                                            </div>
                                            <div
                                                className="mt-1 font-semibold text-gray-900"
                                            >
                                                {formatNumber(
                                                    instagram.account?.media_count
                                                )}
                                            </div>
                                        </div>

                                        <div
                                            className="
                                                rounded-xl
                                                border
                                                p-4
                                            "
                                        >
                                            <div
                                                className="text-xs text-gray-500"
                                            >
                                                Token sampai
                                            </div>
                                            <div
                                                className="mt-1 font-semibold text-gray-900"
                                            >
                                                {formatExpires(
                                                    instagram.expires_at
                                                )}
                                            </div>
                                        </div>

                                    </div>


                                    <div
                                        className="
                                            mt-6
                                            flex
                                            flex-wrap
                                            gap-3
                                        "
                                    >

                                        <button
                                            type="button"
                                            onClick={
                                                handleInstagramSynchronize
                                            }
                                            disabled={
                                                isBusy
                                            }
                                            className="
                                                rounded-xl
                                                bg-gray-900
                                                px-5
                                                py-3
                                                text-sm
                                                font-semibold
                                                text-white
                                                hover:bg-gray-800
                                                disabled:opacity-50
                                            "
                                        >
                                            {activeAction ===
                                                "instagram-sync"
                                                ? "Menyinkronkan..."
                                                : "Sinkronisasi Data"
                                            }
                                        </button>


                                        <button
                                            type="button"
                                            onClick={
                                                handleInstagramDisconnect
                                            }
                                            disabled={
                                                isBusy
                                            }
                                            className="
                                                rounded-xl
                                                border
                                                border-red-200
                                                px-5
                                                py-3
                                                text-sm
                                                font-semibold
                                                text-red-600
                                                hover:bg-red-50
                                                disabled:opacity-50
                                            "
                                        >
                                            {activeAction ===
                                                "instagram-disconnect"
                                                ? "Memutuskan..."
                                                : "Putuskan Instagram"
                                            }
                                        </button>

                                    </div>

                                </div>

                            )}

                        </div>

                    </div>


                    {/* =================================================
                        FACEBOOK
                    ================================================= */}

                    <div
                        className="
                            overflow-hidden
                            rounded-2xl
                            border
                            border-gray-200
                            bg-white
                            shadow-sm
                        "
                    >

                        <div
                            className="
                                flex
                                items-center
                                justify-between
                                border-b
                                border-gray-100
                                p-6
                            "
                        >

                            <div
                                className="
                                    flex
                                    items-center
                                    gap-4
                                "
                            >

                                <div
                                    className="
                                        flex
                                        h-14
                                        w-14
                                        items-center
                                        justify-center
                                        rounded-2xl
                                        bg-[#1877F2]
                                        text-lg
                                        font-bold
                                        text-white
                                    "
                                >
                                    f
                                </div>

                                <div>

                                    <h2
                                        className="
                                            text-lg
                                            font-bold
                                            text-gray-900
                                        "
                                    >
                                        Facebook
                                    </h2>

                                    <p
                                        className="
                                            text-sm
                                            text-gray-500
                                        "
                                    >
                                        Facebook Page
                                    </p>

                                </div>

                            </div>


                            <div
                                className={
                                    `
                                    rounded-full
                                    px-3
                                    py-1
                                    text-xs
                                    font-semibold
                                    ${
                                        facebook.connected
                                            ? "bg-green-100 text-green-700"
                                            : "bg-gray-100 text-gray-500"
                                    }
                                    `
                                }
                            >
                                {facebook.connected
                                    ? "Terhubung"
                                    : "Belum terhubung"
                                }
                            </div>

                        </div>


                        <div className="p-6">

                            {!facebook.connected ? (

                                <div>

                                    <div
                                        className="
                                            rounded-xl
                                            bg-gray-50
                                            p-5
                                        "
                                    >

                                        <h3
                                            className="
                                                font-semibold
                                                text-gray-900
                                            "
                                        >
                                            Facebook belum terhubung
                                        </h3>

                                        <p
                                            className="
                                                mt-2
                                                text-sm
                                                leading-6
                                                text-gray-600
                                            "
                                        >
                                            Hubungkan akun Facebook untuk
                                            memilih Page dan mengambil data
                                            Page Insights serta content.
                                        </p>

                                    </div>


                                    <button
                                        type="button"
                                        onClick={
                                            handleFacebookConnect
                                        }
                                        disabled={
                                            isBusy
                                        }
                                        className="
                                            mt-5
                                            inline-flex
                                            items-center
                                            gap-2
                                            rounded-xl
                                            bg-[#1877F2]
                                            px-5
                                            py-3
                                            text-sm
                                            font-semibold
                                            text-white
                                            hover:opacity-90
                                            disabled:cursor-not-allowed
                                            disabled:opacity-50
                                        "
                                    >
                                        {activeAction ===
                                            "Facebook-connect"
                                            ? "Menghubungkan..."
                                            : "Hubungkan Facebook"
                                        }
                                    </button>

                                </div>

                            ) : (

                                <div>

                                    <div
                                        className="
                                            rounded-xl
                                            border
                                            border-green-200
                                            bg-green-50
                                            p-5
                                        "
                                    >

                                        <div
                                            className="
                                                flex
                                                items-center
                                                gap-3
                                            "
                                        >

                                            <div
                                                className="
                                                    flex
                                                    h-10
                                                    w-10
                                                    items-center
                                                    justify-center
                                                    rounded-full
                                                    bg-green-500
                                                    font-bold
                                                    text-white
                                                "
                                            >
                                                ✓
                                            </div>

                                            <div>

                                                <div
                                                    className="
                                                        font-semibold
                                                        text-green-800
                                                    "
                                                >
                                                    Facebook terhubung
                                                </div>

                                                <div
                                                    className="
                                                        mt-1
                                                        text-sm
                                                        text-green-700
                                                    "
                                                >
                                                    {facebook.facebook_user_name ||
                                                        "Akun Facebook"
                                                    }
                                                </div>

                                            </div>

                                        </div>

                                    </div>


                                    {/* =================================================
                                        PAGE SELECTOR
                                    ================================================= */}

                                    <div
                                        className="
                                            mt-5
                                            rounded-xl
                                            border
                                            border-gray-200
                                            p-4
                                        "
                                    >

                                        <label
                                            className="
                                                block
                                                text-xs
                                                font-semibold
                                                uppercase
                                                tracking-wide
                                                text-gray-500
                                            "
                                        >
                                            Facebook Page
                                        </label>

                                        {facebook.pages.length > 0 ? (

                                            <select
                                                value={
                                                    facebook.selected_page?.id ||
                                                    ""
                                                }
                                                onChange={
                                                    handleSelectFacebookPage
                                                }
                                                disabled={
                                                    isBusy
                                                }
                                                className="
                                                    mt-2
                                                    w-full
                                                    rounded-xl
                                                    border
                                                    border-gray-200
                                                    bg-white
                                                    px-4
                                                    py-3
                                                    text-sm
                                                    font-medium
                                                    text-gray-800
                                                    outline-none
                                                    focus:border-blue-400
                                                "
                                            >
                                                <option value="">
                                                    Pilih Facebook Page
                                                </option>

                                                {facebook.pages.map(
                                                    (page) => (
                                                        <option
                                                            key={page.id}
                                                            value={page.id}
                                                        >
                                                            {page.name}
                                                        </option>
                                                    )
                                                )}
                                            </select>

                                        ) : (

                                            <div
                                                className="
                                                    mt-2
                                                    text-sm
                                                    text-gray-500
                                                "
                                            >
                                                Belum ada Facebook Page.
                                            </div>

                                        )}

                                    </div>


                                    <div
                                        className="
                                            mt-5
                                            grid
                                            grid-cols-2
                                            gap-4
                                        "
                                    >

                                        <div
                                            className="
                                                rounded-xl
                                                border
                                                p-4
                                            "
                                        >
                                            <div
                                                className="text-xs text-gray-500"
                                            >
                                                Page aktif
                                            </div>
                                            <div
                                                className="mt-1 font-semibold text-gray-900"
                                            >
                                                {facebook.selected_page?.name ||
                                                    "-"
                                                }
                                            </div>
                                        </div>

                                        <div
                                            className="
                                                rounded-xl
                                                border
                                                p-4
                                            "
                                        >
                                            <div
                                                className="text-xs text-gray-500"
                                            >
                                                Jumlah Page
                                            </div>
                                            <div
                                                className="mt-1 font-semibold text-gray-900"
                                            >
                                                {formatNumber(
                                                    facebook.pages.length
                                                )}
                                            </div>
                                        </div>

                                    </div>


                                    <div
                                        className="
                                            mt-6
                                            flex
                                            flex-wrap
                                            gap-3
                                        "
                                    >

                                        <button
                                            type="button"
                                            onClick={
                                                handleFacebookSynchronize
                                            }
                                            disabled={
                                                isBusy ||
                                                !facebook.connected
                                            }
                                            className="
                                                rounded-xl
                                                bg-[#1877F2]
                                                px-5
                                                py-3
                                                text-sm
                                                font-semibold
                                                text-white
                                                hover:opacity-90
                                                disabled:opacity-50
                                            "
                                        >
                                            {activeAction ===
                                                "facebook-sync"
                                                ? "Menyinkronkan..."
                                                : "Sinkronisasi Data"
                                            }
                                        </button>

                                        <div
                                            className="
                                                rounded-xl
                                                border
                                                border-gray-200
                                                px-4
                                                py-3
                                                text-xs
                                                text-gray-500
                                            "
                                        >
                                            Koneksi Facebook tersimpan
                                            berdasarkan akun MAVis.
                                        </div>

                                    </div>

                                </div>

                            )}

                        </div>

                    </div>

                </div>


                {/* =================================================
                    PERSISTENCE NOTE
                ================================================= */}

                <div
                    className="
                        mt-6
                        rounded-2xl
                        border
                        border-gray-200
                        bg-gray-50
                        p-5
                    "
                >

                    <div
                        className="
                            text-sm
                            font-semibold
                            text-gray-900
                        "
                    >
                        Status koneksi MAVis
                    </div>

                    <p
                        className="
                            mt-2
                            text-sm
                            leading-6
                            text-gray-600
                        "
                    >
                        Koneksi Instagram dan Facebook tidak disimpan
                        hanya di state halaman. Status dibaca kembali dari
                        backend berdasarkan akun MAVis yang sedang login.
                        Karena itu, login ulang dengan akun MAVis yang sama
                        tidak perlu otomatis memutus koneksi social media
                        sebelumnya.
                    </p>

                </div>

            </div>

        </div>

    );

};


export default MetaConnection;
