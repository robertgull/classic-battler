import { useEffect, useState } from "react";



const petTypes = [
    "Aquatic", "Beast", "Critter", "Dragonkin", "Elemental",
    "Flying", "Humanoid", "Magic", "Mechanical", "Undead"
];
const DISCORD_CLIENT_ID = "1439358085104664737";
const DISCORD_REDIRECT_URI = "http://localhost:5173/discord-callback";
const DISCORD_SCOPE = "identify email";
const DISCORD_TOKEN_URL = "https://discord.com/api/oauth2/token";
const DISCORD_OAUTH_URL =
    "https://discord.com/oauth2/authorize?client_id=1439358085104664737&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A5173%2Fdiscord-callback&scope=identify+email";

// =================================================== PKCE helpers ====================================================

function generateRandomString(length = 43): string {
    const charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-._~";
    const randomValues = new Uint8Array(length);
    window.crypto.getRandomValues(randomValues);
    return Array.from(randomValues, v => charset[v % charset.length]).join("");
}

function base64UrlEncode(buffer: ArrayBuffer): string {
    const bytes = new Uint8Array(buffer);
    let binary = "";
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary)
        .replace(/\+/g, "-")
        .replace(/\//g, "_")
        .replace(/=+$/, "");
}

async function sha256(message: string): Promise<ArrayBuffer> {
    const encoder = new TextEncoder();
    const data = encoder.encode(message);
    return crypto.subtle.digest("SHA-256", data);
}

async function createPkcePair(): Promise<{ verifier: string; challenge: string }> {
    const verifier = generateRandomString(64); // 43–128 chars "secret"
    const hash = await sha256(verifier);
    const challenge = base64UrlEncode(hash);
    return { verifier, challenge };
}



function App() {
    // auth state native login
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [token, setToken] = useState<string | null>(null);
    const [authError, setAuthError] = useState("");
    // visual for user if logged in
    const [loggedInUser, setLoggedInUser] = useState<string | null>(null);

    // just state
    const [petId, setPetId] = useState("");
    const [pet, setPet] = useState<any>(null);

    const [petType, setPetType] = useState(petTypes[0]);
    const [results, setResults] = useState<any[]>([]);

    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const [collectionMessage, setCollectionMessage] = useState<string | null>(null);
    const [currentUser, setCurrentUser] = useState<any | null>(null);

    // serach bar
    const [abilityQuery, setAbilityQuery] = useState("");
    const [abilityResults, setAbilityResults] = useState<any[]>([]);


    // ============================================== DISCORD PKCE =====================================================
    async function startDiscordLogin() {
        try {
            const { verifier, challenge } = await createPkcePair(); // 2. “generate code_verifier and from this a code_challenge.”
            const state = generateRandomString(32);

            sessionStorage.setItem("discord_pkce_verifier", verifier);
            sessionStorage.setItem("discord_oauth_state", state);

            const params = new URLSearchParams({ // https://discord.com/oauth2/authorize?
                client_id: DISCORD_CLIENT_ID,  // client_id=1439358085104664737
                response_type: "code", // response_type=code
                redirect_uri: DISCORD_REDIRECT_URI, // redirect_uri=http%3A%2F%2Flocalhost%3A5173%2Fdiscord-callback
                scope: DISCORD_SCOPE, // &scope=identify+email
                state, // state=Q4NNTNez.4WP5a-4uEP8YT6w5%7EnbURpr extra protection
                code_challenge: challenge, // code_challenge=op1f-En4v35xZOQbHu1p6G_pjxZpjN643KZginHa64c
                code_challenge_method: "S256", // code_challenge_method=S256
            });

            window.location.href = `https://discord.com/oauth2/authorize?${params.toString()}`; // 3. “Authorize Code Request + Code challenge to /authorize.”
        } catch (e) {                                                                                                   // 4. 5. User is redirected and Authenticates
            console.error(e);
            setAuthError("Failed to start Discord login");
        }
    }


    // ============================================== DISCORD PKCE =====================================================
    // function getDiscordAuthUrl() {
    //     const params = new URLSearchParams({
    //         client_id: DISCORD_CLIENT_ID,
    //         response_type: "code",
    //         redirect_uri: DISCORD_REDIRECT_URI, //generated from discord https://discord.com/oauth2/authorize?client_id=1439358085104664737&response_type=code&redirect_uri=http%3A%2F%2Flocalhost%3A5173&scope=identify+email
    //         scope: DISCORD_SCOPE,
    //         prompt: "consent",
    //     });
    //
    //     return `https://discord.com/oauth2/authorize?${params.toString()}`;
    // }

    async function addPetToCollection(petId: number) {
        if (!token) {
            setCollectionMessage("You must be logged in to add pets.");
            return;
        }

        setCollectionMessage(null);
        try {
            const res = await fetch("http://127.0.0.1:8000/users/me/collection", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({ pet_id: petId }),
            });

            if (!res.ok) {
                throw new Error(`Failed to add pet (status ${res.status})`);
            }

            setCollectionMessage(`Pet ${petId} added to your collection!`);
        } catch (err: any) {
            setCollectionMessage(err.message || "Failed to add pet to collection.");
        }
    }

    // helper to add Authorization header if logged in
    function authHeaders(): HeadersInit {
        return token ? { Authorization: `Bearer ${token}` } : {};
    }

    // login native
    async function handleLogin() {
        setAuthError("");
        try {
            const body = new URLSearchParams();
            body.append("username", username);
            body.append("password", password); // plaintext, OK on https?
            body.append("grant_type", "password"); // matches OAuth2PasswordRequestForm

            const response = await fetch("http://127.0.0.1:8000/token", {
                method: "POST",
                headers: {
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body,
            });

            if (!response.ok) {
                throw new Error(`Login failed (status ${response.status})`);
            }

            const data = await response.json();
            setToken(data.access_token);
            setLoggedInUser(data.email);
        } catch (e: any) {
            setAuthError(e.message || "Login failed");
            setToken(null);
        }
    }

    function handleLogout() {
        setToken(null);
    }


    async function handleGoogleCredentialResponse(response: any) {
        try {
            const googleIdToken = response.credential; // <-- ID token from Google

            const res = await fetch("http://127.0.0.1:8000/auth/google", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ token: googleIdToken }),
            });

            if (!res.ok) {
                throw new Error(`Google login failed (${res.status})`);
            }

            const data = await res.json();
            setToken(data.access_token);
            setLoggedInUser(data.username);
            setAuthError("");
        } catch (e: any) {
            setAuthError(e.message || "Google login failed");
        }
    }

    useEffect(() => {
        // Load Google Identity Services script
        const script = document.createElement("script");
        script.src = "https://accounts.google.com/gsi/client";
        script.async = true;
        script.defer = true;
        script.onload = () => {
            if (!window.google) return;

            window.google.accounts.id.initialize({
                client_id: "519877391908-vnpc3e9h84bo4a7ma6so08fus09gvsle.apps.googleusercontent.com",
                callback: handleGoogleCredentialResponse,
            });

            window.google.accounts.id.renderButton(
                document.getElementById("google-signin-button"),
                {
                    theme: "outline",
                    size: "large",
                }
            );
        };

        document.body.appendChild(script);
        return () => {
            document.body.removeChild(script);
        };
    }, []);

    useEffect(() => {
        const url = new URL(window.location.href);
        const code = url.searchParams.get("code"); // 6. “Auth server stores code_challenge and redirects back with an authorization code.”
        const state = url.searchParams.get("state");         //part of callback
        const path = url.pathname;

        if (path === "/discord-callback" && code) {
            const storedVerifier = sessionStorage.getItem("discord_pkce_verifier");
            const storedState = sessionStorage.getItem("discord_oauth_state");

            if (!storedVerifier || !storedState || state !== storedState) { // check state extra protection
                  setAuthError("Discord login failed: invalid state or PKCE verifier");
                sessionStorage.removeItem("discord_pkce_verifier");
                sessionStorage.removeItem("discord_oauth_state");
                window.history.replaceState({}, "", "/");
                return;
            }

            (async () => {
                try {
                    // FE -> Discord: exchange code for Discord access token
                    const body = new URLSearchParams({
                        client_id: DISCORD_CLIENT_ID,
                        grant_type: "authorization_code",
                        code,
                        redirect_uri: DISCORD_REDIRECT_URI,
                        code_verifier: storedVerifier,
                    });

                    const tokenRes = await fetch(DISCORD_TOKEN_URL, { // 7. “Send Auth code + code_verifier to /oauth/token.” ->
                        method: "POST",                                                                                                                    // (Discord) 8. Validate Code Verifier and Challenge
                        headers: {                                               // 9. “get back ID Token and Access token”
                            "Content-Type": "application/x-www-form-urlencoded",
                        },
                        body: body.toString(),
                    });


                    const tokenJson = await tokenRes.json();
                    const discordAccessToken = tokenJson.access_token as string | undefined;


                    // send token to backend
                    const backendRes = await fetch( //10. Send token to backend to request user data
                        "http://127.0.0.1:8000/auth/discord",
                        {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: JSON.stringify({ access_token: discordAccessToken }),
                        },
                    );


                    const data = await backendRes.json();
                    setToken(data.access_token); // JWT
                    setLoggedInUser(data.username);
                    setAuthError("");
                } catch (e: any) {
                    console.error(e);
                    setAuthError(e.message || "Discord login failed");
                } finally {
                    sessionStorage.removeItem("discord_pkce_verifier");
                    sessionStorage.removeItem("discord_oauth_state");
                    window.history.replaceState({}, "", "/");
                }
            })();
        }
    }, []);

    useEffect(() => {
        const q = abilityQuery.trim();
        if (!q) {
            setAbilityResults([]);
            return;
        }

        const timeout = setTimeout(async () => {
            const res = await fetch(
                `http://127.0.0.1:8000/abilities/search/rapid?q=${encodeURIComponent(q)}`
            );
            const data = await res.json();
            setAbilityResults(data);
        }, 250);

        return () => clearTimeout(timeout);
    }, [abilityQuery]);



    async function fetchCurrentUser() {
        if (!token) return;

        try {
            const res = await fetch("http://127.0.0.1:8000/users/me", {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            if (!res.ok) {
                throw new Error(`Failed to fetch user (status ${res.status})`);
            }

            const user = await res.json();
            setCurrentUser(user);
            setCollectionMessage(null);
        } catch (e: any) {
            setCollectionMessage(e.message || "Failed to fetch user");
        }
    }

    // Fetch single pet by ID
    async function fetchPetById() {
        setLoading(true);
        setError("");
        setPet(null);
        try {
            const response = await fetch(
                `http://127.0.0.1:8000/battle_pets/get_by_id?_id=${encodeURIComponent(
                    petId
                )}`,
                {
                    headers: {
                        ...authHeaders(),
                    },
                }
            );
            if (!response.ok) throw new Error(`Status ${response.status}`);
            const data = await response.json();
            setPet(data);
        } catch (e: any) {
            setError(e.message || "Unknown error");
        } finally {
            setLoading(false);
        }
    }

    async function fetchDoubleCounters() {    // double counter with auth
        setLoading(true);
        setError("");
        setResults([]);
        try {
            const response = await fetch(
                `http://127.0.0.1:8000/battle_pets/list_double_counters?_type=${encodeURIComponent(
                    petType
                )}`,
                {
                    headers: {
                        ...authHeaders(),
                    },
                }
            );
            if (!response.ok) throw new Error(`Status ${response.status}`);
            const data = await response.json();
            setResults(data);
        } catch (e: any) {
            setError(e.message || "Unknown error");
        } finally {
            setLoading(false);
        }
    }

    return (
        <div style={{ padding: 32 }}>
            <h1>Battle Pet Lookup</h1>

            {/* Login box */}
            <div
                style={{
                    border: "1px solid #ccc",
                    padding: 16,
                    marginBottom: 24,
                    maxWidth: 400,
                }}
            >
                <h2>Login</h2>
                <div style={{ marginBottom: 8 }}>
                    <input
                        type="text"
                        placeholder="username"
                        value={username}
                        onChange={e => setUsername(e.target.value)}
                    />
                </div>
                <div style={{ marginBottom: 8 }}>
                    <input
                        type="password"
                        placeholder="password"
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                    />
                </div>
                <div style={{ display: "flex", gap: 8 }}>
                    <button onClick={handleLogin} disabled={!username || !password}>
                        Login
                    </button>
                    {token && (
                        <button onClick={handleLogout}>
                            Logout
                        </button>
                    )}
                </div>
                {token && (
                    <div style={{ marginTop: 8, color: "green" }}>
                        {loggedInUser && (
                            <div style={{ marginTop: 8, color: "green" }}>
                                Logged in as <strong>{loggedInUser}</strong>
                            </div>
                        )}
                    </div>
                )}
                {authError && (
                    <div style={{ marginTop: 8, color: "red" }}>
                        {authError}
                    </div>
                )}

                <div
                    style={{
                        border: "1px solid #ccc",
                        padding: 16,
                        marginBottom: 24,
                        maxWidth: 400,
                    }}
                >

                    <div style={{ marginTop: 16 }}>
                        <div id="google-signin-button" />
                    </div>

                    {authError && (
                        <div style={{ marginTop: 8, color: "red" }}>{authError}</div>
                    )}
                    <button
                        type="button"
                        onClick={() => {
                            startDiscordLogin(); // 1. “Click login link.”
                        }}
                    >
                        Login with Discord
                    </button>
                </div>

            </div>

            {/* Lookup by ID */}
            <div style={{ marginBottom: 24 }}>
                <input
                    type="number"
                    value={petId}
                    onChange={e => setPetId(e.target.value)}
                    placeholder="Enter pet ID"
                />
                <button
                    onClick={fetchPetById}
                    disabled={loading || !petId || !token}
                    title={!token ? "Please log in first" : undefined}
                >
                    {loading ? "Loading..." : "Get Pet By ID"}
                </button>
                <button
                    onClick={fetchCurrentUser}
                    disabled={!token}
                    style={{ marginLeft: 8 }}
                >
                    User
                </button>
            </div>

            {pet && (
                <div style={{ marginTop: 16 }}>
                    <h2>Pet Details</h2>
                    <pre>{JSON.stringify(pet, null, 2)}</pre>
                </div>
            )}

            {currentUser && (
                <div style={{ marginTop: 16 }}>
                    <h2>Current User</h2>
                    <pre>{JSON.stringify(currentUser, null, 2)}</pre>
                </div>
            )}

            <hr style={{ margin: "32px 0" }} />


            {/* Ability Fuzzy Search */}
            <hr />

            <h3>Ability Search</h3>

            <input
                type="text"
                value={abilityQuery}
                onChange={(e) => setAbilityQuery(e.target.value)}
                style={{ width: 300 }}
            />

            <ul>
                {abilityResults.map((a) => (
                    <li key={a.id}>
                        <strong>{a.name}</strong> ({a.type})
                        {a.description}
                    </li>
                ))}
            </ul>

            <hr style={{ margin: "32px 0" }} />

            {/* Double Counter Search */}
            <div style={{ marginBottom: 24 }}>
                <label>
                    Pet Type:{" "}
                    <select value={petType} onChange={e => setPetType(e.target.value)}>
                        {petTypes.map(pt => (
                            <option key={pt} value={pt}>
                                {pt}
                            </option>
                        ))}
                    </select>
                </label>
                <button
                    onClick={fetchDoubleCounters}
                    disabled={loading || !token}
                    title={!token ? "Please log in first" : undefined}
                >
                    {loading ? "Loading..." : "Find Double Counters"}
                </button>
            </div>
            {results.length > 0 && (
                <div style={{ marginTop: 16 }}>
                    <h2>Double Counter Pets</h2>
                    <ul>
                        {results.map((pet) => (
                            <li key={pet.id} style={{ marginBottom: 8 }}>
                                <a
                                    href={`https://www.wowhead.com/mop-classic/npc=${pet.id}`}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                >
                                    <strong>{pet.name}</strong> ({pet.type})
                                </a>

                                <button
                                    style={{ marginLeft: 8 }}
                                    onClick={() => addPetToCollection(pet.id)}
                                    disabled={!token}
                                    title={!token ? "Please log in to add pets" : undefined}
                                >
                                    Add to collection
                                </button>
                            </li>
                        ))}
                    </ul>

                    {collectionMessage && (
                        <div style={{ marginTop: 8, color: "green" }}>
                            {collectionMessage}
                        </div>
                    )}
                </div>
            )}

            {error && (
                <div style={{ color: "red", marginTop: 16 }}>Error: {error}</div>
            )}
        </div>
    );
}

export default App;
