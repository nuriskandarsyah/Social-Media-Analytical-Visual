import {
    useCallback,
    useEffect,
    useMemo,
    useState,
} from "react";

import {
    BookOpen,
    CheckCircle2,
    FileText,
    Plus,
    Pencil,
    RefreshCw,
    Search,
    Trash2,
    X,
    Brain,
    Clock3,
    Database,
    Eye,
} from "lucide-react";

import * as api from "../../services/api";


// =========================================================
// KNOWLEDGE BASE
// =========================================================

export default function KnowledgeBase() {

    const [
        documents,
        setDocuments,
    ] = useState([]);

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
        searchTerm,
        setSearchTerm,
    ] = useState("");

    const [
        searchResults,
        setSearchResults,
    ] = useState([]);

    const [
        searching,
        setSearching,
    ] = useState(false);

    const [
        showCreate,
        setShowCreate,
    ] = useState(false);

    const [
        creating,
        setCreating,
    ] = useState(false);

    const [
        editing,
        setEditing,
    ] = useState(false);

    const [
        editingId,
        setEditingId,
    ] = useState(null);

    const [
        deletingId,
        setDeletingId,
    ] = useState(null);

    const [
        selectedDocument,
        setSelectedDocument,
    ] = useState(null);

    const [
        activeMeta,
        setActiveMeta,
    ] = useState(null);

    const [
        form,
        setForm,
    ] = useState({
        title: "",
        content: "",
        source_type: "manual",
    });


    // =====================================================
    // FETCH
    // =====================================================

    const fetchDocuments = useCallback(
        async (
            showRefresh = false
        ) => {

            try {

                if (showRefresh) {
                    setRefreshing(true);
                } else {
                    setLoading(true);
                }

                setError("");

                const metaResult =
                    await api.get("/api/meta/status");

                const metaData =
                    metaResult?.data || {};

                const instagramUserId =
                    metaData?.instagram_user_id ||
                    metaData?.account?.user_id ||
                    null;

                if (
                    !metaResult?.success ||
                    !instagramUserId
                ) {
                    throw new Error(
                        metaResult?.message ||
                        "Akun Instagram aktif tidak ditemukan."
                    );
                }

                setActiveMeta({
                    instagram_user_id:
                        String(instagramUserId),
                    username:
                        metaData?.account?.username ||
                        "-",
                    name:
                        metaData?.account?.name ||
                        metaData?.account?.username ||
                        "-",
                });

                const result =
                    await api.get(
                        `/api/knowledge-base/?instagram_user_id=${encodeURIComponent(
                            instagramUserId
                        )}`
                    );

                if (
                    result?.success === false
                ) {
                    throw new Error(
                        result.message ||
                        "Data Knowledge Base gagal diambil."
                    );
                }

                setDocuments(
                    Array.isArray(result?.data)
                        ? result.data
                        : []
                );

            } catch (err) {

                console.error(
                    "Knowledge Base error:",
                    err
                );

                setError(
                    err?.message ||
                    "Gagal mengambil data Knowledge Base."
                );

            } finally {

                setLoading(false);
                setRefreshing(false);

            }

        },
        []
    )


    useEffect(() => {

        const timer = setTimeout(() => {

            fetchDocuments();

        }, 0);

        return () => clearTimeout(timer);

    }, [
        fetchDocuments,
    ]);


    // =====================================================
    // STATS
    // =====================================================

    const stats = useMemo(
        () => {

            const totalDocuments =
                documents.length;

            const totalEmbeddings =
                documents.filter(
                    (
                        item
                    ) =>
                        Boolean(
                            item?.embedding
                        )
                ).length;

            const totalCharacters =
                documents.reduce(
                    (
                        total,
                        item
                    ) =>
                        total +
                        String(
                            item?.content ||
                            ""
                        ).length,
                    0
                );

            const latest =
                documents.length
                    ? documents
                        .map(
                            (
                                item
                            ) =>
                                item?.created_at
                                    ? new Date(
                                        item.created_at
                                    )
                                    : null
                        )
                        .filter(Boolean)
                        .sort(
                            (
                                a,
                                b
                            ) =>
                                b.getTime() -
                                a.getTime()
                        )[0]
                    : null;

            return {
                totalDocuments,
                totalEmbeddings,
                totalCharacters,
                latest,
            };

        },
        [
            documents,
        ]
    );


    // =====================================================
    // SEARCH
    // =====================================================

    const runSearch = async () => {

        const query =
            searchTerm.trim();

        if (!query) {

            setSearchResults([]);

            return;

        }

        try {

            setSearching(true);
            setError("");

            const metaResult =
                await api.get("/api/meta/status");

            const metaData =
                metaResult?.data || {};

            const instagramUserId =
                metaData?.instagram_user_id ||
                metaData?.account?.user_id ||
                null;

            if (
                !metaResult?.success ||
                !instagramUserId
            ) {
                throw new Error(
                    metaResult?.message ||
                    "Akun Instagram aktif tidak ditemukan."
                );
            }

            setActiveMeta({
                instagram_user_id:
                    String(instagramUserId),
                username:
                    metaData?.account?.username ||
                    "-",
                name:
                    metaData?.account?.name ||
                    metaData?.account?.username ||
                    "-",
            });

            const result =
                await api.post(
                    "/api/knowledge-base/search",
                    {
                        query,
                        top_k: 5,
                        instagram_user_id:
                            String(instagramUserId),
                    }
                );

            if (
                result?.success === false
            ) {
                throw new Error(
                    result.message ||
                    "Pencarian gagal."
                );
            }

            setSearchResults(
                Array.isArray(result?.data)
                    ? result.data
                    : []
            );

        } catch (err) {

            console.error(
                "Knowledge Base search error:",
                err
            );

            setError(
                err?.message ||
                "Pencarian Knowledge Base gagal."
            );

        } finally {

            setSearching(false);

        }

    }


    // =====================================================
    // CREATE
    // =====================================================

    const createDocument = async (
        event
    ) => {

        event.preventDefault();

        if (
            !form.title.trim() ||
            !form.content.trim()
        ) {

            setError(
                "Judul dan isi dokumen wajib diisi."
            );

            return;

        }

        try {

            setCreating(true);
            setError("");

            const metaResult =
                await api.get("/api/meta/status");

            const metaData =
                metaResult?.data || {};

            const instagramUserId =
                metaData?.instagram_user_id ||
                metaData?.account?.user_id ||
                null;

            if (
                !metaResult?.success ||
                !instagramUserId
            ) {
                throw new Error(
                    metaResult?.message ||
                    "Akun Instagram aktif tidak ditemukan."
                );
            }

            const result =
                await api.post(
                    "/api/knowledge-base/create",
                    {
                        title:
                            form.title.trim(),

                        content:
                            form.content.trim(),

                        source_type:
                            form.source_type ||
                            "manual",

                        instagram_user_id:
                            String(instagramUserId),
                    }
                );

            if (
                result?.success === false
            ) {
                throw new Error(
                    result.message ||
                    "Dokumen gagal dibuat."
                );
            }

            setForm({
                title: "",
                content: "",
                source_type: "manual",
            });

            setShowCreate(false);
            setSearchResults([]);

            await fetchDocuments(true);

        } catch (err) {

            console.error(
                "Knowledge Base create error:",
                err
            );

            setError(
                err?.message ||
                "Gagal membuat Knowledge Base."
            );

        } finally {

            setCreating(false);

        }

    }
    // =====================================================
    // EDIT
    // =====================================================

    const openEdit = (
        item
    ) => {

        setSelectedDocument(
            item
        );

        setEditingId(
            item.id_kb
        );

        setForm({
            title:
                item.title || "",

            content:
                item.content || "",

            source_type:
                item.source_type ||
                "manual",
        });

        setError("");

    };


    const editDocument = async (
        event
    ) => {

        event.preventDefault();

        if (!selectedDocument?.id_kb) {
            return;
        }

        if (
            !form.title.trim() ||
            !form.content.trim()
        ) {

            setError(
                "Judul dan isi dokumen wajib diisi."
            );

            return;

        }

        try {

            setEditing(true);
            setError("");

            const metaResult =
                await api.get("/api/meta/status");

            const metaData =
                metaResult?.data || {};

            const instagramUserId =
                metaData?.instagram_user_id ||
                metaData?.account?.user_id ||
                null;

            if (
                !metaResult?.success ||
                !instagramUserId
            ) {

                throw new Error(
                    metaResult?.message ||
                    "Akun Instagram aktif tidak ditemukan."
                );

            }

            const result =
                await api.put(
                    `/api/knowledge-base/${selectedDocument.id_kb}`,
                    {
                        title:
                            form.title.trim(),

                        content:
                            form.content.trim(),

                        source_type:
                            form.source_type ||
                            "manual",

                        instagram_user_id:
                            String(
                                instagramUserId
                            ),
                    }
                );

            if (
                result?.success === false
            ) {

                throw new Error(
                    result.message ||
                    "Dokumen gagal diperbarui."
                );

            }

            setEditingId(
                null
            );

            setSelectedDocument(
                null
            );

            setForm({
                title: "",
                content: "",
                source_type: "manual",
            });

            setSearchResults([]);

            await fetchDocuments(
                true
            );

        } catch (err) {

            console.error(
                "Knowledge Base edit error:",
                err
            );

            setError(
                err?.message ||
                "Gagal memperbarui Knowledge Base."
            );

        } finally {

            setEditing(false);

        }

    };



    // =====================================================
    // DELETE
    // =====================================================

    const deleteDocument = async (
        id
    ) => {

        const confirmed =
            window.confirm(
                "Hapus dokumen Knowledge Base ini?"
            );

        if (!confirmed) {
            return;
        }

        try {

            setDeletingId(id);
            setError("");

            const metaResult =
                await api.get("/api/meta/status");

            const metaData =
                metaResult?.data || {};

            const instagramUserId =
                metaData?.instagram_user_id ||
                metaData?.account?.user_id ||
                null;

            if (
                !metaResult?.success ||
                !instagramUserId
            ) {
                throw new Error(
                    metaResult?.message ||
                    "Akun Instagram aktif tidak ditemukan."
                );
            }

            const result =
                await api.del(
                    `/api/knowledge-base/${id}?instagram_user_id=${encodeURIComponent(
                        instagramUserId
                    )}`
                );

            if (
                result?.success === false
            ) {
                throw new Error(
                    result.message ||
                    "Dokumen gagal dihapus."
                );
            }

            if (
                selectedDocument?.id_kb === id
            ) {
                setSelectedDocument(null);
            }

            await fetchDocuments(true);

        } catch (err) {

            console.error(
                "Knowledge Base delete error:",
                err
            );

            setError(
                err?.message ||
                "Gagal menghapus dokumen."
            );

        } finally {

            setDeletingId(null);

        }

    }


    // =====================================================
    // HELPERS
    // =====================================================

    const formatDate = (
        value
    ) => {

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
                dateStyle: "medium",
                timeStyle: "short",
            }
        );

    };


    const formatNumber = (
        value
    ) =>
        new Intl.NumberFormat(
            "id-ID"
        ).format(
            Number(value) || 0
        );


    // =====================================================
    // LOADING
    // =====================================================

    if (loading) {

        return (
            <div className="knowledge-base-loading">

                <div className="knowledge-base-spinner" />

                <span>
                    Memuat Knowledge Base...
                </span>

            </div>
        );

    }


    // =====================================================
    // PAGE
    // =====================================================

    return (

        <div className="knowledge-base-page">

            {/* =================================================
                HEADER
            ================================================= */}

            <div className="knowledge-base-header">

                <div className="knowledge-base-heading">

                    <div className="knowledge-base-breadcrumb">

                        <BookOpen
                            size={15}
                        />

                        <span>
                            Knowledge Base
                        </span>

                    </div>

                    <h2>
                        Knowledge Base Perusahaan
                    </h2>

                    <p>
                        Kelola dokumen pengetahuan yang digunakan
                        sistem AI sebagai sumber context untuk RAG.
                    </p>

                    {activeMeta && (

                        <div className="knowledge-base-active-account">

                            <span>
                                Akun aktif
                            </span>

                            <strong>
                                {activeMeta.name ||
                                    activeMeta.username ||
                                    "-"}
                            </strong>

                            <small>
                                @{activeMeta.username ||
                                    "-"}
                            </small>

                        </div>

                    )}

                </div>

                <div className="knowledge-base-actions">

                    <button
                        type="button"
                        className="knowledge-base-refresh"
                        onClick={() =>
                            fetchDocuments(true)
                        }
                        disabled={refreshing}
                    >

                        <RefreshCw
                            size={14}
                            className={
                                refreshing
                                    ? "knowledge-base-spin"
                                    : ""
                            }
                        />

                        {refreshing
                            ? "Memuat..."
                            : "Refresh"}

                    </button>

                    <button
                        type="button"
                        className="knowledge-base-primary"
                        onClick={() =>
                            setShowCreate(true)
                        }
                    >

                        <Plus
                            size={15}
                        />

                        Tambah Dokumen

                    </button>

                </div>

            </div>


            {/* =================================================
                ERROR
            ================================================= */}

            {error && (

                <div className="knowledge-base-error">

                    <span>
                        {error}
                    </span>

                    <button
                        type="button"
                        onClick={() =>
                            setError("")
                        }
                    >
                        <X
                            size={15}
                        />
                    </button>

                </div>

            )}


            {/* =================================================
                STATS
            ================================================= */}

            <div className="knowledge-base-stat-grid">

                <StatCard
                    icon={FileText}
                    label="Total Dokumen"
                    value={
                        formatNumber(
                            stats.totalDocuments
                        )
                    }
                    description="Dokumen akun aktif"
                />

                <StatCard
                    icon={Brain}
                    label="Total Embedding"
                    value={
                        formatNumber(
                            stats.totalEmbeddings
                        )
                    }
                    description="Dokumen dengan embedding"
                />

                <StatCard
                    icon={Database}
                    label="Total Karakter"
                    value={
                        formatNumber(
                            stats.totalCharacters
                        )
                    }
                    description="Konten tersimpan"
                />

                <StatCard
                    icon={Clock3}
                    label="Pembaruan Terakhir"
                    value={
                        stats.latest
                            ? stats.latest.toLocaleDateString(
                                "id-ID",
                                {
                                    day: "2-digit",
                                    month: "short",
                                    year: "numeric",
                                }
                            )
                            : "-"
                    }
                    description={
                        stats.latest
                            ? stats.latest.toLocaleTimeString(
                                "id-ID",
                                {
                                    hour: "2-digit",
                                    minute: "2-digit",
                                }
                            )
                            : "Belum ada dokumen"
                    }
                    compact
                />

            </div>


            {/* =================================================
                SEARCH
            ================================================= */}

            <section className="knowledge-base-search-panel">

                <div className="knowledge-base-section-heading">

                    <div>

                        <span className="knowledge-base-eyebrow">
                            SEMANTIC SEARCH
                        </span>

                        <h3>
                            Uji Pencarian Knowledge Base
                        </h3>

                    </div>

                    <div className="knowledge-base-search-badge">

                        <Brain
                            size={14}
                        />

                        Sentence Transformer

                    </div>

                </div>

                <div className="knowledge-base-search-form">

                    <div className="knowledge-base-search-input">

                        <Search
                            size={16}
                        />

                        <input
                            value={searchTerm}
                            onChange={(event) =>
                                setSearchTerm(
                                    event.target.value
                                )
                            }
                            onKeyDown={(event) => {

                                if (
                                    event.key === "Enter"
                                ) {
                                    runSearch();
                                }

                            }}
                            placeholder="Cari informasi dari dokumen..."
                        />

                    </div>

                    <button
                        type="button"
                        className="knowledge-base-search-button"
                        onClick={runSearch}
                        disabled={
                            searching ||
                            !searchTerm.trim()
                        }
                    >

                        <Search
                            size={14}
                        />

                        {searching
                            ? "Mencari..."
                            : "Cari"}

                    </button>

                </div>

                {searchResults.length > 0 && (

                    <div className="knowledge-base-search-results">

                        {searchResults.map(
                            (
                                item,
                                index
                            ) => (

                                <div
                                    className="knowledge-base-search-result"
                                    key={
                                        `${item.id_kb}-${index}`
                                    }
                                >

                                    <div className="knowledge-base-search-result-top">

                                        <div>

                                            <strong>
                                                {
                                                    item.title ||
                                                    "-"
                                                }
                                            </strong>

                                            <span>
                                                Similarity{" "}
                                                {
                                                    (
                                                        Number(
                                                            item.similarity
                                                        ) *
                                                        100
                                                    ).toFixed(2)
                                                }%
                                            </span>

                                        </div>

                                        <span className="knowledge-base-result-number">
                                            #{index + 1}
                                        </span>

                                    </div>

                                    <p>
                                        {
                                            item.content ||
                                            "-"
                                        }
                                    </p>

                                </div>

                            )
                        )}

                    </div>

                )}

                {searchTerm.trim() &&
                    !searching &&
                    searchResults.length === 0 && (

                        <div className="knowledge-base-no-results">
                            Tidak ditemukan dokumen yang relevan.
                        </div>

                    )}

            </section>


            {/* =================================================
                DOCUMENTS
            ================================================= */}

            <section className="knowledge-base-panel">

                <div className="knowledge-base-section-heading">

                    <div>

                        <span className="knowledge-base-eyebrow">
                            DOCUMENT LIBRARY
                        </span>

                        <h3>
                            Dokumen Pengetahuan
                        </h3>

                    </div>

                    <span className="knowledge-base-count">
                        {documents.length} dokumen
                    </span>

                </div>

                {documents.length === 0 ? (

                    <div className="knowledge-base-empty">

                        <div className="knowledge-base-empty-icon">

                            <FileText
                                size={21}
                            />

                        </div>

                        <h4>
                            Belum ada dokumen
                        </h4>

                        <p>
                            Tambahkan dokumen perusahaan untuk
                            menjadi sumber pengetahuan AI.
                        </p>

                        <button
                            type="button"
                            className="knowledge-base-primary"
                            onClick={() =>
                                setShowCreate(true)
                            }
                        >
                            <Plus
                                size={14}
                            />
                            Tambah Dokumen
                        </button>

                    </div>

                ) : (

                    <div className="knowledge-base-table-wrapper">

                        <table className="knowledge-base-table">

                            <thead>

                                <tr>

                                    <th>
                                        Dokumen
                                    </th>

                                    <th>
                                        Sumber
                                    </th>

                                    <th>
                                        Embedding
                                    </th>

                                    <th>
                                        Dibuat
                                    </th>

                                    <th>
                                        Aksi
                                    </th>

                                </tr>

                            </thead>

                            <tbody>

                                {documents.map(
                                    (
                                        item
                                    ) => (

                                        <tr
                                            key={
                                                item.id_kb
                                            }
                                        >

                                            <td>

                                                <div className="knowledge-base-document-cell">

                                                    <div className="knowledge-base-document-icon">

                                                        <FileText
                                                            size={15}
                                                        />

                                                    </div>

                                                    <div>

                                                        <strong>
                                                            {
                                                                item.title ||
                                                                "-"
                                                            }
                                                        </strong>

                                                        <span>
                                                            {String(
                                                                item.content ||
                                                                ""
                                                            ).length
                                                                ? `${formatNumber(
                                                                    String(
                                                                        item.content
                                                                    ).length
                                                                )} karakter`
                                                                : "Konten kosong"}
                                                        </span>

                                                    </div>

                                                </div>

                                            </td>

                                            <td>

                                                <span className="knowledge-base-source-badge">

                                                    {
                                                        item.source_type ||
                                                        "manual"
                                                    }

                                                </span>

                                            </td>

                                            <td>

                                                {item.embedding ? (

                                                    <span className="knowledge-base-status success">

                                                        <CheckCircle2
                                                            size={12}
                                                        />

                                                        Ter-embed

                                                    </span>

                                                ) : (

                                                    <span className="knowledge-base-status pending">

                                                        Belum

                                                    </span>

                                                )}

                                            </td>

                                            <td>
                                                {
                                                    formatDate(
                                                        item.created_at
                                                    )
                                                }
                                            </td>

                                            <td>

                                                <div className="knowledge-base-row-actions">

                                                    <button
                                                        type="button"
                                                        className="knowledge-base-icon-button"
                                                        title="Edit dokumen"
                                                        onClick={() =>
                                                            openEdit(
                                                                item
                                                            )
                                                        }
                                                    >
                                                        <Pencil
                                                            size={14}
                                                        />
                                                    </button>

                                                    <button
                                                        type="button"
                                                        className="knowledge-base-icon-button"
                                                        title="Lihat detail"
                                                        onClick={() =>
                                                            setSelectedDocument(
                                                                item
                                                            )
                                                        }
                                                    >
                                                        <Eye
                                                            size={14}
                                                        />
                                                    </button>

                                                    <button
                                                        type="button"
                                                        className="knowledge-base-icon-button danger"
                                                        title="Hapus"
                                                        onClick={() =>
                                                            deleteDocument(
                                                                item.id_kb
                                                            )
                                                        }
                                                        disabled={
                                                            deletingId ===
                                                            item.id_kb
                                                        }
                                                    >
                                                        <Trash2
                                                            size={14}
                                                        />
                                                    </button>

                                                </div>

                                            </td>

                                        </tr>

                                    )
                                )}

                            </tbody>

                        </table>

                    </div>

                )}

            </section>


            {/* =================================================
                DETAIL MODAL
            ================================================= */}

            {selectedDocument && (

                <Modal
                    title="Detail Dokumen"
                    onClose={() =>
                        setSelectedDocument(
                            null
                        )
                    }
                >

                    <div className="knowledge-base-detail">

                        <div className="knowledge-base-detail-row">

                            <span>
                                Judul
                            </span>

                            <strong>
                                {
                                    selectedDocument.title ||
                                    "-"
                                }
                            </strong>

                        </div>

                        <div className="knowledge-base-detail-row">

                            <span>
                                Sumber
                            </span>

                            <strong>
                                {
                                    selectedDocument.source_type ||
                                    "manual"
                                }
                            </strong>

                        </div>

                        <div className="knowledge-base-detail-row">

                            <span>
                                Akun Instagram
                            </span>

                            <strong>
                                {
                                    selectedDocument.instagram_user_id ||
                                    "-"
                                }
                            </strong>

                        </div>

                        <div className="knowledge-base-detail-row">

                            <span>
                                Embedding
                            </span>

                            <strong>

                                {selectedDocument.embedding
                                    ? `${selectedDocument.embedding.model_name || "Model"}`
                                    : "Belum tersedia"}

                            </strong>

                        </div>

                        <div>

                            <span className="knowledge-base-detail-label">
                                Isi Dokumen
                            </span>

                            <div className="knowledge-base-detail-content">
                                {
                                    selectedDocument.content ||
                                    "-"
                                }
                            </div>

                        </div>

                    </div>

                </Modal>

            )}


            {/* =================================================
                EDIT MODAL
            ================================================= */}

            {editingId &&
                selectedDocument && (

                    <Modal
                        title="Edit Dokumen Knowledge Base"
                        onClose={() => {

                            if (!editing) {

                                setEditingId(null);
                                setSelectedDocument(null);

                                setForm({
                                    title: "",
                                    content: "",
                                    source_type: "manual",
                                });

                            }

                        }}
                    >

                        <form
                            className="knowledge-base-form"
                            onSubmit={editDocument}
                        >

                            <div className="knowledge-base-field">

                                <label>
                                    Judul Dokumen
                                </label>

                                <input
                                    value={
                                        form.title
                                    }
                                    onChange={(event) =>
                                        setForm(
                                            (current) => ({
                                                ...current,
                                                title:
                                                    event.target.value,
                                            })
                                        )
                                    }
                                    maxLength={255}
                                    autoFocus
                                />

                            </div>

                            <div className="knowledge-base-field">

                                <label>
                                    Jenis Sumber
                                </label>

                                <select
                                    value={
                                        form.source_type
                                    }
                                    onChange={(event) =>
                                        setForm(
                                            (current) => ({
                                                ...current,
                                                source_type:
                                                    event.target.value,
                                            })
                                        )
                                    }
                                >

                                    <option value="manual">
                                        Manual
                                    </option>

                                    <option value="company_profile">
                                        Company Profile
                                    </option>

                                    <option value="product">
                                        Produk
                                    </option>

                                    <option value="service">
                                        Layanan
                                    </option>

                                    <option value="brand">
                                        Brand Guideline
                                    </option>

                                    <option value="content_strategy">
                                        Content Strategy
                                    </option>

                                    <option value="target_market">
                                        Target Market
                                    </option>

                                    <option value="faq">
                                        FAQ
                                    </option>

                                </select>

                            </div>

                            <div className="knowledge-base-field">

                                <label>
                                    Isi Dokumen
                                </label>

                                <textarea
                                    value={
                                        form.content
                                    }
                                    onChange={(event) =>
                                        setForm(
                                            (current) => ({
                                                ...current,
                                                content:
                                                    event.target.value,
                                            })
                                        )
                                    }
                                    rows={10}
                                />

                                <span className="knowledge-base-field-hint">
                                    Setelah diperbarui, embedding lama akan diganti dengan embedding baru agar pencarian AI sesuai dengan isi terbaru.
                                </span>

                            </div>

                            <div className="knowledge-base-modal-actions">

                                <button
                                    type="button"
                                    className="knowledge-base-secondary"
                                    onClick={() => {

                                        if (!editing) {

                                            setEditingId(null);
                                            setSelectedDocument(null);

                                        }

                                    }}
                                    disabled={editing}
                                >
                                    Batal
                                </button>

                                <button
                                    type="submit"
                                    className="knowledge-base-primary"
                                    disabled={editing}
                                >

                                    {editing ? (
                                        <>
                                            <RefreshCw
                                                size={14}
                                                className="knowledge-base-spin"
                                            />
                                            Memperbarui...
                                        </>
                                    ) : (
                                        <>
                                            <Pencil
                                                size={14}
                                            />
                                            Simpan Perubahan
                                        </>
                                    )}

                                </button>

                            </div>

                        </form>

                    </Modal>

                )}

            {/* =================================================
                CREATE MODAL
            ================================================= */}

            {showCreate && (

                <Modal
                    title="Tambah Dokumen Knowledge Base"
                    onClose={() => {

                        if (!creating) {
                            setShowCreate(false);
                        }

                    }}
                >

                    <form
                        className="knowledge-base-form"
                        onSubmit={
                            createDocument
                        }
                    >

                        <div className="knowledge-base-field">

                            <label>
                                Judul Dokumen
                            </label>

                            <input
                                value={
                                    form.title
                                }
                                onChange={(
                                    event
                                ) =>
                                    setForm(
                                        (
                                            current
                                        ) => ({
                                            ...current,
                                            title:
                                                event
                                                    .target
                                                    .value,
                                        })
                                    )
                                }
                                placeholder="Contoh: Profil Perusahaan"
                                maxLength={255}
                                autoFocus
                            />

                        </div>

                        <div className="knowledge-base-field">

                            <label>
                                Jenis Sumber
                            </label>

                            <select
                                value={
                                    form.source_type
                                }
                                onChange={(
                                    event
                                ) =>
                                    setForm(
                                        (
                                            current
                                        ) => ({
                                            ...current,
                                            source_type:
                                                event
                                                    .target
                                                    .value,
                                        })
                                    )
                                }
                            >

                                <option value="manual">
                                    Manual
                                </option>

                                <option value="company_profile">
                                    Company Profile
                                </option>

                                <option value="product">
                                    Produk
                                </option>

                                <option value="service">
                                    Layanan
                                </option>

                                <option value="brand">
                                    Brand Guideline
                                </option>

                            </select>

                        </div>

                        <div className="knowledge-base-field">

                            <label>
                                Isi Dokumen
                            </label>

                            <textarea
                                value={
                                    form.content
                                }
                                onChange={(
                                    event
                                ) =>
                                    setForm(
                                        (
                                            current
                                        ) => ({
                                            ...current,
                                            content:
                                                event
                                                    .target
                                                    .value,
                                        })
                                    )
                                }
                                placeholder="Masukkan informasi perusahaan yang akan digunakan AI sebagai sumber pengetahuan..."
                                rows={10}
                            />

                            <span className="knowledge-base-field-hint">
                                Setelah disimpan, sistem otomatis membuat embedding dengan Sentence Transformer.
                            </span>

                        </div>

                        <div className="knowledge-base-modal-actions">

                            <button
                                type="button"
                                className="knowledge-base-secondary"
                                onClick={() =>
                                    setShowCreate(false)
                                }
                                disabled={creating}
                            >
                                Batal
                            </button>

                            <button
                                type="submit"
                                className="knowledge-base-primary"
                                disabled={creating}
                            >

                                {creating ? (
                                    <>
                                        <RefreshCw
                                            size={14}
                                            className="knowledge-base-spin"
                                        />
                                        Memproses...
                                    </>
                                ) : (
                                    <>
                                        <Plus
                                            size={14}
                                        />
                                        Simpan & Embed
                                    </>
                                )}

                            </button>

                        </div>

                    </form>

                </Modal>

            )}

        </div>

    );

}


// =========================================================
// STAT CARD
// =========================================================

function StatCard({
    icon: Icon,
    label,
    value,
    description,
    compact = false,
}) {

    return (

        <div className="knowledge-base-stat-card">

            <div className="knowledge-base-stat-top">

                <div className="knowledge-base-stat-icon">

                    <Icon
                        size={17}
                    />

                </div>

            </div>

            <span className="knowledge-base-stat-label">
                {label}
            </span>

            <strong
                className={
                    compact
                        ? "knowledge-base-stat-value compact"
                        : "knowledge-base-stat-value"
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


// =========================================================
// MODAL
// =========================================================

function Modal({
    title,
    children,
    onClose,
}) {

    return (

        <div className="knowledge-base-modal-backdrop">

            <div className="knowledge-base-modal">

                <div className="knowledge-base-modal-header">

                    <div>

                        <span className="knowledge-base-eyebrow">
                            KNOWLEDGE BASE
                        </span>

                        <h3>
                            {title}
                        </h3>

                    </div>

                    <button
                        type="button"
                        className="knowledge-base-modal-close"
                        onClick={
                            onClose
                        }
                    >
                        <X
                            size={17}
                        />
                    </button>

                </div>

                <div className="knowledge-base-modal-body">
                    {children}
                </div>

            </div>

        </div>

    );

}
