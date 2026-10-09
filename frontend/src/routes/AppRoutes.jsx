import {
    Navigate,
    Route,
    Routes,
} from "react-router-dom";

import Login from "../pages/Login";

import Dashboard from "../pages/admin/Dashboard";
import InstagramDashboard from "../pages/admin/InstagramDashboard";
import FacebookDashboard from "../pages/admin/FacebookDashboard";
import MetaInsight from "../pages/admin/MetaInsight";
import MetaConnection
    from "../pages/admin/MetaConnection";
import AIAnalysis from "../pages/admin/AIAnalysis";
import AIContentPlanner
    from "../pages/admin/AIContentPlanner";
import KnowledgeBase
    from "../pages/admin/KnowledgeBase";
import SyncLog
    from "../pages/admin/SyncLog";

import MainLayout
    from "../components/Layout/MainLayout";

import {
    useAuth,
} from "../context/AuthContext";


// =====================================================
// PROTECTED ROUTE
// =====================================================

function ProtectedRoute({
    children,
}) {

    const {
        isAuthenticated,
    } = useAuth();

    if (!isAuthenticated) {

        return (
            <Navigate
                to="/login"
                replace
            />
        );

    }

    return children;

}


// =====================================================
// ROLE ROUTE
// =====================================================

function RoleRoute({
    children,
    role,
}) {

    const {
        user,
    } = useAuth();

    if (!user) {

        return (
            <Navigate
                to="/login"
                replace
            />
        );

    }

    if (user.role !== role) {

        return (
            <Navigate
                to="/"
                replace
            />
        );

    }

    return children;

}


// =====================================================
// APP ROUTES
// =====================================================

export default function AppRoutes() {

    return (

        <Routes>

            {/* =================================================
                LOGIN
            ================================================= */}

            <Route
                path="/login"
                element={
                    <Login />
                }
            />


            {/* =================================================
                ADMIN LAYOUT

                MainLayout hanya satu kali di parent.
                Semua halaman admin menjadi child route.
            ================================================= */}

            <Route
                path="/admin"
                element={

                    <ProtectedRoute>

                        <RoleRoute
                            role="admin"
                        >

                            <MainLayout />

                        </RoleRoute>

                    </ProtectedRoute>

                }
            >

                {/* =================================================
                    DASHBOARD
                ================================================= */}

                <Route
                    path="dashboard"
                    element={
                        <Dashboard />
                    }
                />


                <Route
                    path="dashboard/instagram"
                    element={
                        <InstagramDashboard />
                    }
                />


                <Route
                    path="dashboard/facebook"
                    element={
                        <FacebookDashboard />
                    }
                />


                {/* =================================================
                    META CONNECTION
                ================================================= */}

                <Route
                    path="meta-connection"
                    element={
                        <MetaConnection />
                    }
                />


                {/* =================================================
                    META INSIGHT
                ================================================= */}

                <Route
                    path="meta-insight"
                    element={
                        <MetaInsight />
                    }
                />


                {/* =================================================
                    AI ANALYSIS
                ================================================= */}

                <Route
                    path="ai-analysis"
                    element={
                        <AIAnalysis />
                    }
                />


                {/* =================================================
                    AI CONTENT PLANNER
                ================================================= */}

                <Route
                    path="ai-content-planner"
                    element={
                        <AIContentPlanner />
                    }
                />



                {/* =================================================
                    KNOWLEDGE BASE
                ================================================= */}

                <Route
                    path="knowledge-base"
                    element={
                        <KnowledgeBase />
                    }
                />


                {/* =================================================
                    SYNC LOG
                ================================================= */}

                <Route
                    path="sync-log"
                    element={
                        <SyncLog />
                    }
                />

            </Route>


            {/* =================================================
                ROOT
            ================================================= */}

            <Route
                path="/"
                element={
                    <Navigate
                        to="/login"
                        replace
                    />
                }
            />


            {/* =================================================
                404
            ================================================= */}

            <Route
                path="*"
                element={
                    <Navigate
                        to="/login"
                        replace
                    />
                }
            />

        </Routes>

    );

}