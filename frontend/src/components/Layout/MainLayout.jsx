import {
    BarChart3,
    Brain,
    Database,
    FileClock,
    LayoutDashboard,
    Link2,
    LogOut,
    Sparkles,
} from "lucide-react";

import {
    NavLink,
    Outlet,
    useNavigate,
} from "react-router-dom";

import {
    useAuth,
} from "../../context/AuthContext";

import LLMChat from "../../pages/admin/LLMChat";


export default function MainLayout() {

    const navigate = useNavigate();

    const {
        user,
        logout,
    } = useAuth();


    // =====================================================
    // MENU ITEMS
    // =====================================================

    const menuItems = [
        {
            label: "Dashboard",
            path: "/admin/dashboard",
            icon: LayoutDashboard,
        },
        {
            label: "Meta Connection",
            path: "/admin/meta-connection",
            icon: Link2,
        },
        {
            label: "Meta Insight",
            path: "/admin/meta-insight",
            icon: BarChart3,
        },
        {
            label: "Analisis AI",
            path: "/admin/ai-analysis",
            icon: Brain,
        },
        {
            label: "AI Content Planner",
            path: "/admin/ai-content-planner",
            icon: Sparkles,
        },
        {
            label: "Knowledge Base",
            path: "/admin/knowledge-base",
            icon: Database,
        },
        {
            label: "Sync Log",
            path: "/admin/sync-log",
            icon: FileClock,
        },
    ];


    // =====================================================
    // LOGOUT
    // =====================================================

    const handleLogout = () => {

        logout();

        navigate("/");

    };


    // =====================================================
    // USER DATA
    // =====================================================

    const username =
        user?.username || "admin";


    const role =
        user?.role
            ? user.role.charAt(0).toUpperCase() +
              user.role.slice(1)
            : "Admin";


    const avatar =
        username
            .charAt(0)
            .toUpperCase();


    // =====================================================
    // RENDER
    // =====================================================

    return (

        <div className="main-layout">

            {/* =================================================
                SIDEBAR
            ================================================= */}

            <aside className="main-sidebar">

                {/* =================================================
                    BRAND
                ================================================= */}

                <div className="main-sidebar-brand">

                    <div className="main-sidebar-logo">
                        MAVis
                    </div>

                    <div className="main-sidebar-subtitle">
                        META ANALYTICAL VISUAL
                    </div>

                </div>


                {/* =================================================
                    MENU TITLE
                ================================================= */}

                <div className="main-sidebar-menu-title">
                    MENU UTAMA
                </div>


                {/* =================================================
                    MENU
                ================================================= */}

                <nav className="main-sidebar-nav">

                    {menuItems.map(
                        (item) => {

                            const Icon =
                                item.icon;


                            return (

                                <NavLink
                                    key={
                                        item.path
                                    }
                                    to={
                                        item.path
                                    }
                                    className={({
                                        isActive,
                                    }) =>
                                        `main-sidebar-link ${
                                            isActive
                                                ? "active"
                                                : ""
                                        }`
                                    }
                                >

                                    <Icon
                                        size={19}
                                        strokeWidth={1.8}
                                    />

                                    <span>
                                        {
                                            item.label
                                        }
                                    </span>

                                </NavLink>

                            );

                        }
                    )}

                </nav>


                {/* =================================================
                    SIDEBAR BOTTOM
                ================================================= */}

                <div className="main-sidebar-bottom">

                    <button
                        type="button"
                        className="main-sidebar-logout"
                        onClick={
                            handleLogout
                        }
                    >

                        <LogOut
                            size={19}
                            strokeWidth={1.8}
                        />

                        <span>
                            Keluar
                        </span>

                    </button>

                </div>

            </aside>


            {/* =================================================
                MAIN CONTENT WRAPPER
            ================================================= */}

            <div className="main-content-wrapper">

                {/* =================================================
                    HEADER
                ================================================= */}

                <header className="main-header">

                    <div className="main-header-title">

                        <h1>
                            Sistem Analisis MAVis
                        </h1>

                        <p>
                            Meta Analytical Visual
                        </p>

                    </div>


                    {/* =================================================
                        USER
                    ================================================= */}

                    <div className="main-header-user">

                        <div className="main-header-user-info">

                            <strong>
                                {username}
                            </strong>

                            <span>
                                {role}
                            </span>

                        </div>


                        <div className="main-header-avatar">
                            {avatar}
                        </div>

                    </div>

                </header>


                {/* =================================================
                    PAGE CONTENT
                ================================================= */}

                <main className="main-content">

                    <Outlet />

                </main>

            </div>


            {/* =================================================
                FLOATING LLM CHAT
            ================================================= */}

            <LLMChat />

        </div>

    );

}