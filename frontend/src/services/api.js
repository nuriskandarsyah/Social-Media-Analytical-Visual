// =========================================================
// MAVis API SERVICE
// =========================================================

const API_URL = "http://127.0.0.1:5000";

const META_API_URL =
    "https://stuffed-awoke-enlarging.ngrok-free.dev";


// =========================================================
// TOKEN
// =========================================================

function getToken() {

    return (
        localStorage.getItem("access_token") ||
        localStorage.getItem("token") ||
        sessionStorage.getItem("access_token") ||
        sessionStorage.getItem("token") ||
        null
    );
}


// =========================================================
// HEADER
// =========================================================

function getHeaders(includeJson = false) {

    const headers = {};

    if (includeJson) {

        headers["Content-Type"] =
            "application/json";

    }

    const token = getToken();

    if (token) {

        headers["Authorization"] =
            `Bearer ${token}`;

    }

    return headers;
}


// =========================================================
// PARSE RESPONSE
// =========================================================

async function parseResponse(response) {

    let data;

    try {

        data =
            await response.json();

    } catch {

        data = {
            success: false,
            message:
                "Response server tidak valid."
        };

    }


    if (!response.ok) {

        throw new Error(
            data?.message ||
            data?.error ||
            `Request gagal (${response.status})`
        );

    }

    return data;
}


// =========================================================
// GENERAL REQUEST
// =========================================================

async function request(
    endpoint,
    options = {}
) {

    const url =
        `${API_URL}${endpoint}`;


    console.log(
        "=============================="
    );

    console.log(
        "MAVis API REQUEST"
    );

    console.log(
        "URL:",
        url
    );

    console.log(
        "JWT tersedia:",
        !!getToken()
    );


    const response =
        await fetch(
            url,
            {
                ...options,

                credentials: "include",

                headers: {

                    ...getHeaders(
                        options.body !== undefined
                    ),

                    ...(options.headers || {})

                }
            }
        );


    console.log(
        "STATUS:",
        response.status
    );


    return await parseResponse(
        response
    );
}


// =========================================================
// META REQUEST
// =========================================================

async function metaRequest(
    endpoint,
    options = {}
) {

    const url =
        `${META_API_URL}${endpoint}`;


    console.log(
        "=============================="
    );

    console.log(
        "META API REQUEST"
    );

    console.log(
        "URL:",
        url
    );

    console.log(
        "JWT tersedia:",
        !!getToken()
    );


    const response =
        await fetch(
            url,
            {
                ...options,

                credentials: "include",

                headers: {

                    ...getHeaders(
                        options.body !== undefined
                    ),

                    ...(options.headers || {})

                }
            }
        );


    console.log(
        "STATUS:",
        response.status
    );


    return await parseResponse(
        response
    );
}


// =========================================================
// LOGIN
// =========================================================

export async function login(
    username,
    password
) {

    console.log(
        "================================"
    );

    console.log(
        "LOGIN START"
    );

    console.log(
        "Username:",
        username
    );

    console.log(
        "API:",
        `${API_URL}/api/auth/login`
    );


    const response =
        await fetch(
            `${API_URL}/api/auth/login`,
            {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                credentials: "include",

                body: JSON.stringify({
                    username,
                    password
                })

            }
        );


    const data =
        await parseResponse(
            response
        );


    console.log(
        "LOGIN RESPONSE:",
        data
    );


    if (data?.access_token) {

        localStorage.setItem(
            "access_token",
            data.access_token
        );

        console.log(
            "JWT berhasil disimpan"
        );

    }


    return data;
}


// =========================================================
// LOGOUT
// =========================================================

export async function logout() {

    try {

        await request(
            "/api/auth/logout",
            {
                method: "POST"
            }
        );

    } catch (error) {

        console.warn(
            "Logout backend gagal:",
            error
        );

    } finally {

        localStorage.removeItem(
            "access_token"
        );

        localStorage.removeItem(
            "token"
        );

        sessionStorage.removeItem(
            "access_token"
        );

        sessionStorage.removeItem(
            "token"
        );

    }
}


// =========================================================
// DASHBOARD
// =========================================================

export async function getDashboard(
    params = {}
) {

    let endpoint =
        "/api/dashboard/";

    const searchParams =
        new URLSearchParams();


    if (params.month) {

        searchParams.set(
            "month",
            params.month
        );

    }


    if (params.year) {

        searchParams.set(
            "year",
            params.year
        );

    }


    const query =
        searchParams.toString();


    if (query) {

        endpoint += `?${query}`;

    }


    return await request(
        endpoint
    );
}


// =========================================================
// META STATUS
// =========================================================

export async function getMetaStatus() {

    return await metaRequest(
        "/api/meta/status"
    );
}


// =========================================================
// META CONNECT
// =========================================================

export async function connectMeta() {

    return await metaRequest(
        "/api/meta/connect"
    );
}


// =========================================================
// META AUTHORIZATION URL
// =========================================================

export async function getMetaAuthorizationUrl() {

    const result =
        await connectMeta();


    const authorizationUrl =
        result?.data?.authorization_url ||
        result?.authorization_url ||
        null;


    if (!authorizationUrl) {

        throw new Error(
            result?.message ||
            "Authorization URL tidak ditemukan."
        );

    }


    return authorizationUrl;
}


// =========================================================
// META DISCONNECT
// =========================================================

export async function disconnectMeta() {

    return await metaRequest(
        "/api/meta/disconnect",
        {
            method: "POST"
        }
    );
}


// =========================================================
// META MEDIA
// =========================================================

export async function getMetaMedia() {

    return await metaRequest(
        "/api/meta/media"
    );
}


// =========================================================
// META SYNCHRONIZE
// =========================================================

export async function synchronizeMeta() {

    return await metaRequest(
        "/api/meta/synchronize",
        {
            method: "POST"
        }
    );
}


// =========================================================
// META CONNECTION
// =========================================================

export async function getMetaConnection() {

    return await getMetaStatus();
}


// =========================================================
// GENERIC GET
// =========================================================

export async function get(
    endpoint
) {

    return await request(
        endpoint
    );
}


// =========================================================
// GENERIC POST
// =========================================================

export async function post(
    endpoint,
    body = {}
) {

    return await request(
        endpoint,
        {

            method: "POST",

            body:
                JSON.stringify(body)

        }
    );
}


// =========================================================
// GENERIC PUT
// =========================================================

export async function put(
    endpoint,
    body = {}
) {

    return await request(
        endpoint,
        {

            method: "PUT",

            body:
                JSON.stringify(body)

        }
    );
}


// =========================================================
// GENERIC DELETE
// =========================================================

export async function del(
    endpoint
) {

    return await request(
        endpoint,
        {
            method: "DELETE"
        }
    );
}


// =========================================================
// META GET
// =========================================================

export async function metaGet(
    endpoint
) {

    return await metaRequest(
        endpoint
    );
}


// =========================================================
// META POST
// =========================================================

export async function metaPost(
    endpoint,
    body = {}
) {

    return await metaRequest(
        endpoint,
        {

            method: "POST",

            body:
                JSON.stringify(body)

        }
    );
}


// =========================================================
// EXPORT CONSTANT
// =========================================================

export {
    API_URL,
    META_API_URL,
    getToken
};