import { useEffect, useState } from "react";

import {
    ArrowRight,
    LockKeyhole,
    UserRound,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import { post } from "../services/api";
import { useAuth } from "../context/AuthContext";
import Loading from "../components/Loading/Loading";


export default function Login() {

    const navigate = useNavigate();

    const { login } = useAuth();


    // =====================================================
    // STATE
    // =====================================================

    const [introFinished, setIntroFinished] =
        useState(false);

    const [username, setUsername] =
        useState("");

    const [password, setPassword] =
        useState("");

    const [rememberMe, setRememberMe] =
        useState(false);

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState("");


    // =====================================================
    // INTRO
    // =====================================================

    useEffect(() => {

        const timer = setTimeout(() => {

            setIntroFinished(true);

        }, 2800);


        return () => {

            clearTimeout(timer);

        };

    }, []);


    // =====================================================
    // LOGIN
    // =====================================================

    const handleSubmit = async (e) => {

        e.preventDefault();

        setError("");


        // -------------------------------------------------
        // VALIDASI
        // -------------------------------------------------

        if (!username.trim()) {

            setError(
                "Username wajib diisi"
            );

            return;
        }


        if (!password) {

            setError(
                "Password wajib diisi"
            );

            return;
        }


        try {

            setLoading(true);


            console.log(
                "===================================="
            );

            console.log(
                "LOGIN START"
            );

            console.log(
                "Username:",
                username.trim()
            );

            console.log(
                "API:",
                "http://127.0.0.1:5000/api/auth/login"
            );


            // =================================================
            // REQUEST LOGIN
            // =================================================
            //
            // PENTING:
            // post() dari api.js langsung mengembalikan
            // response JSON backend.
            //
            // JANGAN menggunakan response.data
            // =================================================

            const result = await post(
                "/api/auth/login",
                {
                    username:
                        username.trim(),

                    password:
                        password
                }
            );


            console.log(
                "Response login:",
                result
            );


            // =================================================
            // CEK RESPONSE
            // =================================================

            if (!result) {

                setError(
                    "Response dari server kosong"
                );

                return;
            }


            if (!result.success) {

                setError(
                    result.message ||
                    "Username atau password salah"
                );

                return;
            }


            // =================================================
            // CEK TOKEN
            // =================================================

            if (!result.access_token) {

                console.error(
                    "Login berhasil tetapi access_token tidak ditemukan:",
                    result
                );

                setError(
                    "Login berhasil tetapi token tidak diterima server"
                );

                return;
            }


            // =================================================
            // SIMPAN TOKEN
            // =================================================

            if (rememberMe) {

                localStorage.setItem(
                    "access_token",
                    result.access_token
                );

            } else {

                sessionStorage.setItem(
                    "access_token",
                    result.access_token
                );

            }


            console.log(
                "JWT berhasil diterima"
            );


            console.log(
                "JWT tersedia:",
                !!(
                    localStorage.getItem(
                        "access_token"
                    ) ||
                    sessionStorage.getItem(
                        "access_token"
                    )
                )
            );


            // =================================================
            // USER
            // =================================================

            const user =
                result.user || {};


            console.log(
                "User:",
                user
            );


            // =================================================
            // AUTH CONTEXT
            // =================================================

            login(
                result.access_token,
                user
            );


            // =================================================
            // REDIRECT BERDASARKAN ROLE
            // =================================================

            if (
                user.role ===
                "admin"
            ) {

                console.log(
                    "Redirect ke dashboard admin"
                );

                navigate(
                    "/admin/dashboard"
                );

                return;
            }


            if (
                user.role ===
                "manager"
            ) {

                console.log(
                    "Redirect ke dashboard manager"
                );

                navigate(
                    "/manager/dashboard"
                );

                return;
            }


            // -------------------------------------------------
            // ROLE TIDAK DIKENALI
            // -------------------------------------------------

            setError(
                "Role pengguna tidak dikenali"
            );


        } catch (err) {

            console.error(
                "LOGIN ERROR:",
                err
            );


            // =================================================
            // AMBIL PESAN ERROR BACKEND
            // =================================================

            const message =
                err?.message ||
                "Tidak dapat terhubung ke server";


            setError(
                message
            );


        } finally {

            setLoading(false);

        }

    };


    // =====================================================
    // RENDER
    // =====================================================

    return (

        <div className="login-page">


            {/* =================================================
                LOADING
            ================================================= */}

            {loading && (

                <Loading
                    text="Memproses login..."
                />

            )}


            {/* =================================================
                INTRO
            ================================================= */}

            <div
                className={`
                    login-intro
                    ${
                        introFinished
                            ? "login-intro-finished"
                            : ""
                    }
                `}
            >

                <div className="login-intro-center">


                    {/* LOGO */}

                    <div className="login-logo-area">

                        <div className="login-logo-text">

                            <span
                                className="
                                    login-letter
                                    login-letter-1
                                "
                            >
                                M
                            </span>


                            <span
                                className="
                                    login-letter
                                    login-letter-2
                                "
                            >
                                A
                            </span>


                            <span
                                className="
                                    login-letter
                                    login-letter-3
                                "
                            >
                                V
                            </span>


                            <span
                                className="
                                    login-letter
                                    login-letter-4
                                "
                            >
                                i
                            </span>


                            <span
                                className="
                                    login-letter
                                    login-letter-5
                                "
                            >
                                s
                            </span>

                        </div>

                    </div>


                    {/* SUBTITLE */}

                    <div className="login-logo-subtitle">

                        META ANALYTICAL VISUAL

                    </div>


                    {/* GARIS */}

                    <div className="login-reveal-line">

                        <span />

                    </div>

                </div>

            </div>


            {/* =================================================
                MAIN
            ================================================= */}

            <div
                className={`
                    login-main
                    ${
                        introFinished
                            ? "login-main-visible"
                            : ""
                    }
                `}
            >


                {/* BACKGROUND */}

                <div className="login-background">

                    <div
                        className="
                            login-light
                            login-light-one
                        "
                    />


                    <div
                        className="
                            login-light
                            login-light-two
                        "
                    />


                    <div
                        className="
                            login-background-grid
                        "
                    />

                </div>


                {/* =================================================
                    LAYOUT
                ================================================= */}

                <div className="login-layout">


                    {/* =================================================
                        LEFT
                    ================================================= */}

                    <section className="login-left">

                        <div className="login-left-content">


                            <div className="login-eyebrow">

                                META ANALYTICAL VISUAL

                            </div>


                            <h1>

                                Analisis data.


                                <span>
                                    Temukan insight.
                                </span>


                                <span>
                                    Ambil keputusan.
                                </span>

                            </h1>


                            <p>

                                MAVis membantu menganalisis
                                performa konten media sosial
                                untuk menghasilkan insight
                                berbasis data.

                            </p>


                            <div className="login-stats">


                                <div className="login-stat">

                                    <strong>
                                        AI
                                    </strong>

                                    <span>
                                        Analysis
                                    </span>

                                </div>


                                <div className="login-stat-divider" />


                                <div className="login-stat">

                                    <strong>
                                        RAG
                                    </strong>

                                    <span>
                                        Knowledge
                                    </span>

                                </div>


                                <div className="login-stat-divider" />


                                <div className="login-stat">

                                    <strong>
                                        DATA
                                    </strong>

                                    <span>
                                        Analytics
                                    </span>

                                </div>


                            </div>

                        </div>

                    </section>


                    {/* =================================================
                        RIGHT
                    ================================================= */}

                    <section className="login-right">

                        <div className="login-form-card">


                            {/* MOBILE BRAND */}

                            <div className="login-mobile-brand">

                                <div className="login-mobile-logo">
                                    MAVis
                                </div>

                                <div className="login-mobile-subtitle">
                                    META ANALYTICAL VISUAL
                                </div>

                            </div>


                            {/* =================================================
                                HEADER
                            ================================================= */}

                            <div className="login-form-header">


                                <div className="login-icon-box">

                                    <span>
                                        M A Vis
                                    </span>

                                </div>


                                <h2>
                                    Selamat Datang
                                </h2>


                                <p>
                                    Masuk untuk mengakses
                                    dashboard analitik MAVis.
                                </p>


                            </div>


                            {/* =================================================
                                ERROR
                            ================================================= */}

                            {error && (

                                <div className="login-error">

                                    {error}

                                </div>

                            )}


                            {/* =================================================
                                FORM
                            ================================================= */}

                            <form
                                onSubmit={handleSubmit}
                                className="login-form"
                            >


                                {/* USERNAME */}

                                <div className="login-field">

                                    <label>
                                        Username
                                    </label>


                                    <div className="login-input-wrapper">

                                        <UserRound
                                            size={18}
                                        />


                                        <input
                                            type="text"

                                            value={
                                                username
                                            }

                                            onChange={(e) =>
                                                setUsername(
                                                    e.target.value
                                                )
                                            }

                                            placeholder="Masukkan username"

                                            autoComplete="username"

                                            disabled={
                                                loading
                                            }
                                        />

                                    </div>

                                </div>


                                {/* PASSWORD */}

                                <div className="login-field">

                                    <label>
                                        Password
                                    </label>


                                    <div className="login-input-wrapper">

                                        <LockKeyhole
                                            size={18}
                                        />


                                        <input
                                            type="password"

                                            value={
                                                password
                                            }

                                            onChange={(e) =>
                                                setPassword(
                                                    e.target.value
                                                )
                                            }

                                            placeholder="Masukkan password"

                                            autoComplete="current-password"

                                            disabled={
                                                loading
                                            }
                                        />

                                    </div>

                                </div>


                                {/* OPTIONS */}

                                <div className="login-options">


                                    <label>

                                        <input
                                            type="checkbox"

                                            checked={
                                                rememberMe
                                            }

                                            onChange={(e) =>
                                                setRememberMe(
                                                    e.target.checked
                                                )
                                            }

                                            disabled={
                                                loading
                                            }
                                        />


                                        <span>
                                            Ingat saya
                                        </span>

                                    </label>


                                    <button
                                        type="button"
                                        disabled={loading}
                                    >
                                        Lupa password?
                                    </button>


                                </div>


                                {/* =================================================
                                    SUBMIT
                                ================================================= */}

                                <button
                                    type="submit"

                                    disabled={
                                        loading
                                    }

                                    className="login-submit"
                                >

                                    <span>

                                        {loading
                                            ? "Memproses..."
                                            : "Masuk ke MAVis"
                                        }

                                    </span>


                                    {!loading && (

                                        <ArrowRight
                                            size={18}
                                        />

                                    )}

                                </button>


                            </form>


                            {/* COPYRIGHT */}

                            <div className="login-copyright">

                                © 2026 MAVis · Meta Analytical Visual

                                <p>
                                    Nur Iskandar S
                                </p>

                            </div>


                        </div>

                    </section>


                </div>

            </div>

        </div>

    );

}