import {
    useEffect,
    useRef,
    useState,
} from "react";

import * as api from "../../services/api";

import {
    Bot,
    ChevronDown,
    MessageCircle,
    Send,
    X,
} from "lucide-react";


// =====================================================
// MESSAGE HELPER
// =====================================================

const createMessage = (
    role,
    content,
    sources = []
) => ({
    id: `${Date.now()}-${Math.random()
        .toString(36)
        .slice(2)}`,
    role,
    content,
    sources,
});


// =====================================================
// LLM CHAT WIDGET
// =====================================================

export default function LLMChat() {

    const [isOpen, setIsOpen] = useState(false);

    const [messages, setMessages] = useState(() => [
        createMessage(
            "assistant",
            "Halo! Saya MAVisupport 👋\n\nSaya dapat membantu menjelaskan sistem MAVis, Knowledge Base, analisis, K-Means++, performa konten, dan informasi lain yang tersedia di sistem."
        ),
    ]);

    const [input, setInput] = useState("");

    const [loading, setLoading] = useState(false);

    const [error, setError] = useState("");

    const messagesEndRef = useRef(null);

    const inputRef = useRef(null);


    // =====================================================
    // AUTO SCROLL
    // =====================================================

    useEffect(() => {

        if (!isOpen) {
            return;
        }

        messagesEndRef.current?.scrollIntoView({
            behavior: "smooth",
        });

    }, [
        messages,
        loading,
        isOpen,
    ]);


    // =====================================================
    // AUTO FOCUS
    // =====================================================

    useEffect(() => {

        if (isOpen) {

            setTimeout(() => {

                inputRef.current?.focus();

            }, 100);

        }

    }, [isOpen]);


    // =====================================================
    // SEND MESSAGE
    // =====================================================

    const handleSend = async () => {

        const message = input.trim();

        if (!message || loading) {
            return;
        }


        // clear error
        setError("");


        // add user message
        setMessages((current) => [
            ...current,
            createMessage(
                "user",
                message
            ),
        ]);


        setInput("");

        setLoading(true);


        try {

            // =================================================
            // AMBIL AKUN INSTAGRAM AKTIF
            // Gunakan request API lokal agar tidak terkena
            // CORS dari endpoint ngrok.
            // =================================================
            const metaResult =
                await api.get(
                    "/api/meta/status"
                );

            if (metaResult?.success === false) {
                throw new Error(
                    metaResult?.message ||
                    "Akun Instagram belum terhubung."
                );
            }

            const metaData =
                metaResult?.data?.data ||
                metaResult?.data ||
                metaResult || {};

            const instagramUserId =
                metaData?.instagram_user_id ||
                metaData?.account?.user_id ||
                metaData?.account?.id ||
                null;

            if (!instagramUserId) {
                throw new Error(
                    "Akun Instagram aktif tidak ditemukan. Hubungkan akun Instagram terlebih dahulu."
                );
            }

            console.log(
                "LLM Chat Instagram User ID:",
                instagramUserId
            );

            // =================================================
            // KIRIM PESAN + INSTAGRAM USER ID
            // =================================================
            const result =
                await api.post(
                    "/api/llm-chat/",
                    {
                        message,
                        instagram_user_id:
                            String(instagramUserId),
                    }
                );


            if (!result?.success) {

                throw new Error(
                    result?.message ||
                    result?.error ||
                    "LLM Chat gagal."
                );

            }


            const data =
                result?.data;


            if (!data?.answer) {

                throw new Error(
                    "LLM tidak mengembalikan jawaban."
                );

            }


            // add assistant message
            setMessages((current) => [
                ...current,
                createMessage(
                    "assistant",
                    data.answer,
                    Array.isArray(
                        data.sources
                    )
                        ? data.sources
                        : []
                ),
            ]);

        } catch (err) {

            console.error(
                "LLM Chat Error:",
                err
            );


            setError(
                err?.message ||
                "Terjadi kesalahan saat menghubungi MAVisupport."
            );

        } finally {

            setLoading(false);


            setTimeout(() => {

                inputRef.current?.focus();

            }, 100);

        }

    };


    // =====================================================
    // ENTER TO SEND
    // =====================================================

    const handleKeyDown = (
        event
    ) => {

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            handleSend();

        }

    };


    // =====================================================
    // CLEAR CHAT
    // =====================================================

    const handleClear = () => {

        if (loading) {
            return;
        }


        setMessages([
            createMessage(
                "assistant",
                "Chat dibersihkan. Silakan tanyakan sesuatu kepada saya."
            ),
        ]);

        setError("");

    };


    // =====================================================
    // TITLE
    // =====================================================

    const title = (
        <span
            className="
                inline-flex
                items-baseline
                tracking-tight
            "
        >

            <span className="text-gray-700">
                M
            </span>

            <span className="text-[#1877F2]">
                A
            </span>

            <span className="text-gray-700">
                V
            </span>

            <span className="text-[#1877F2]">
                I
            </span>

            <span className="text-gray-700">
                support
            </span>

        </span>
    );


    // =====================================================
    // RENDER
    // =====================================================

    return (
        <>
            {/* =================================================
                FLOATING CHAT ROOM
            ================================================= */}

            {isOpen && (

                <div
                    className="
                        fixed
                        bottom-24
                        right-6
                        z-[9999]
                        flex
                        h-[600px]
                        w-[390px]
                        max-w-[calc(100vw-32px)]
                        flex-col
                        overflow-hidden
                        rounded-3xl
                        border
                        border-gray-200
                        bg-white
                        shadow-2xl
                    "
                >

                    {/* =================================================
                        HEADER
                    ================================================= */}

                    <div
                        className="
                            flex
                            items-center
                            justify-between
                            border-b
                            border-gray-200
                            bg-white
                            px-5
                            py-4
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
                                    rounded-2xl
                                    bg-gray-900
                                    text-white
                                "
                            >

                                <Bot
                                    size={20}
                                    strokeWidth={1.8}
                                />

                            </div>


                            <div>

                                <h3
                                    className="
                                        text-sm
                                        font-bold
                                    "
                                >
                                    {title}
                                </h3>

                                <p
                                    className="
                                        mt-0.5
                                        text-[11px]
                                        text-gray-400
                                    "
                                >
                                    AI Assistant MAVis
                                </p>

                            </div>

                        </div>


                        <div
                            className="
                                flex
                                items-center
                                gap-1
                            "
                        >

                            <button
                                type="button"
                                onClick={
                                    handleClear
                                }
                                disabled={loading}
                                title="Bersihkan chat"
                                className="
                                    flex
                                    h-9
                                    w-9
                                    items-center
                                    justify-center
                                    rounded-xl
                                    text-gray-400
                                    hover:bg-gray-100
                                    hover:text-gray-700
                                    disabled:opacity-40
                                "
                            >
                                <span
                                    className="
                                        text-xs
                                        font-semibold
                                    "
                                >
                                    ↻
                                </span>
                            </button>


                            <button
                                type="button"
                                onClick={() =>
                                    setIsOpen(
                                        false
                                    )
                                }
                                title="Tutup"
                                className="
                                    flex
                                    h-9
                                    w-9
                                    items-center
                                    justify-center
                                    rounded-xl
                                    text-gray-400
                                    hover:bg-gray-100
                                    hover:text-gray-700
                                "
                            >

                                <X
                                    size={18}
                                />

                            </button>

                        </div>

                    </div>


                    {/* =================================================
                        MESSAGES
                    ================================================= */}

                    <div
                        className="
                            flex-1
                            overflow-y-auto
                            bg-gray-50
                            px-4
                            py-4
                        "
                    >

                        <div
                            className="
                                flex
                                flex-col
                                gap-4
                            "
                        >

                            {messages.map(
                                (message) => (

                                    <div
                                        key={
                                            message.id
                                        }
                                        className={`
                                            flex
                                            ${
                                                message.role ===
                                                "user"
                                                    ? "justify-end"
                                                    : "justify-start"
                                            }
                                        `}
                                    >

                                        <div
                                            className={`
                                                max-w-[88%]
                                                px-4
                                                py-3
                                                ${
                                                    message.role ===
                                                    "user"
                                                        ? `
                                                            rounded-2xl
                                                            rounded-br-md
                                                            bg-gray-900
                                                            text-white
                                                        `
                                                        : `
                                                            rounded-2xl
                                                            rounded-bl-md
                                                            border
                                                            border-gray-200
                                                            bg-white
                                                            text-gray-800
                                                        `
                                            }
                                        `}

                                        >

                                            {message.role ===
                                                "assistant" && (

                                                <div
                                                    className="
                                                        mb-1.5
                                                        text-[11px]
                                                        font-semibold
                                                    "
                                                >
                                                    {title}
                                                </div>

                                            )}


                                            <div
                                                className="
                                                    whitespace-pre-wrap
                                                    text-sm
                                                    leading-6
                                                "
                                            >
                                                {
                                                    message.content
                                                }
                                            </div>


                                            {/* SOURCES */}

                                            {message.role ===
                                                "assistant" &&
                                                Array.isArray(
                                                    message.sources
                                                ) &&
                                                message.sources
                                                    .length >
                                                    0 && (

                                                <div
                                                    className="
                                                        mt-3
                                                        border-t
                                                        border-gray-100
                                                        pt-2
                                                    "
                                                >

                                                    <p
                                                        className="
                                                            mb-1.5
                                                            text-[10px]
                                                            font-semibold
                                                            text-gray-400
                                                        "
                                                    >
                                                        Sumber
                                                        Knowledge Base
                                                    </p>


                                                    {message.sources.map(
                                                        (
                                                            source,
                                                            index
                                                        ) => (

                                                            <div
                                                                key={
                                                                    source?.id_kb ||
                                                                    index
                                                                }
                                                                className="
                                                                    mb-1.5
                                                                    rounded-lg
                                                                    bg-gray-50
                                                                    px-2.5
                                                                    py-2
                                                                "
                                                            >

                                                                <p
                                                                    className="
                                                                        text-[11px]
                                                                        font-medium
                                                                        text-gray-700
                                                                    "
                                                                >
                                                                    {
                                                                        source?.title ||
                                                                        `Sumber ${
                                                                            index +
                                                                            1
                                                                        }`
                                                                    }
                                                                </p>


                                                                {source?.similarity !==
                                                                    undefined && (

                                                                    <p
                                                                        className="
                                                                            mt-0.5
                                                                            text-[10px]
                                                                            text-gray-400
                                                                        "
                                                                    >
                                                                        Similarity:{" "}
                                                                        {Number(
                                                                            source.similarity
                                                                        ).toFixed(
                                                                            3
                                                                        )}
                                                                    </p>

                                                                )}

                                                            </div>

                                                        )
                                                    )}

                                                </div>

                                            )}

                                        </div>

                                    </div>

                                )
                            )}


                            {/* LOADING */}

                            {loading && (

                                <div
                                    className="
                                        flex
                                        justify-start
                                    "
                                >

                                    <div
                                        className="
                                            rounded-2xl
                                            rounded-bl-md
                                            border
                                            border-gray-200
                                            bg-white
                                            px-4
                                            py-3
                                        "
                                    >

                                        <div
                                            className="
                                                flex
                                                items-center
                                                gap-2
                                            "
                                        >

                                            <span
                                                className="
                                                    h-1.5
                                                    w-1.5
                                                    animate-bounce
                                                    rounded-full
                                                    bg-gray-400
                                                "
                                            />

                                            <span
                                                className="
                                                    h-1.5
                                                    w-1.5
                                                    animate-bounce
                                                    rounded-full
                                                    bg-gray-400
                                                    [animation-delay:120ms]
                                                "
                                            />

                                            <span
                                                className="
                                                    h-1.5
                                                    w-1.5
                                                    animate-bounce
                                                    rounded-full
                                                    bg-gray-400
                                                    [animation-delay:240ms]
                                                "
                                            />

                                            <span
                                                className="
                                                    ml-1
                                                    text-xs
                                                    text-gray-500
                                                "
                                            >
                                                MAVisupport
                                                sedang
                                                berpikir...
                                            </span>

                                        </div>

                                    </div>

                                </div>

                            )}


                            <div
                                ref={
                                    messagesEndRef
                                }
                            />

                        </div>

                    </div>


                    {/* =================================================
                        ERROR
                    ================================================= */}

                    {error && (

                        <div
                            className="
                                border-t
                                border-red-100
                                bg-red-50
                                px-4
                                py-2
                            "
                        >

                            <p
                                className="
                                    text-xs
                                    text-red-600
                                "
                            >
                                {error}
                            </p>

                        </div>

                    )}


                    {/* =================================================
                        INPUT
                    ================================================= */}

                    <div
                        className="
                            border-t
                            border-gray-200
                            bg-white
                            p-3
                        "
                    >

                        <div
                            className="
                                flex
                                items-end
                                gap-2
                                rounded-2xl
                                border
                                border-gray-200
                                bg-gray-50
                                p-1.5
                            "
                        >

                            <textarea
                                ref={
                                    inputRef
                                }
                                value={
                                    input
                                }
                                onChange={(
                                    event
                                ) =>
                                    setInput(
                                        event.target.value
                                    )
                                }
                                onKeyDown={
                                    handleKeyDown
                                }
                                disabled={
                                    loading
                                }
                                rows={1}
                                placeholder="Tulis pesan..."
                                className="
                                    min-h-[42px]
                                    max-h-[110px]
                                    flex-1
                                    resize-none
                                    border-0
                                    bg-transparent
                                    px-3
                                    py-2.5
                                    text-sm
                                    text-gray-800
                                    outline-none
                                    placeholder:text-gray-400
                                "
                            />


                            <button
                                type="button"
                                onClick={
                                    handleSend
                                }
                                disabled={
                                    loading ||
                                    !input.trim()
                                }
                                className="
                                    flex
                                    h-10
                                    w-10
                                    flex-shrink-0
                                    items-center
                                    justify-center
                                    rounded-xl
                                    bg-gray-900
                                    text-white
                                    hover:bg-gray-800
                                    disabled:cursor-not-allowed
                                    disabled:opacity-40
                                "
                            >

                                <Send
                                    size={16}
                                    strokeWidth={2}
                                />

                            </button>

                        </div>


                        <p
                            className="
                                mt-1.5
                                text-center
                                text-[10px]
                                text-gray-400
                            "
                        >
                            Enter untuk mengirim
                        </p>

                    </div>

                </div>

            )}


            {/* =================================================
                FLOATING BUTTON
            ================================================= */}

            <button
                type="button"
                onClick={() =>
                    setIsOpen(
                        (current) =>
                            !current
                    )
                }
                className="
                    fixed
                    bottom-6
                    right-6
                    z-[10000]
                    flex
                    h-16
                    w-16
                    items-center
                    justify-center
                    rounded-full
                    bg-gray-900
                    text-white
                    shadow-2xl
                    transition-all
                    duration-200
                    hover:scale-105
                    hover:bg-gray-800
                "
                title="Buka MAVisupport"
            >

                {isOpen ? (

                    <ChevronDown
                        size={25}
                        strokeWidth={2}
                    />

                ) : (

                    <MessageCircle
                        size={27}
                        strokeWidth={1.8}
                    />

                )}

            </button>

        </>
    );
}