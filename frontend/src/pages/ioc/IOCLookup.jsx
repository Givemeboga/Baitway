import { useState, useEffect } from "react";
import { useSearchParams, useNavigate } from "react-router-dom";
import api from "../../api/client";

const verdictColors = {
    clean: "#2e7d32",
    suspicious: "#e65100",
    malicious: "#c62828",
};

function VerdictBadge({ verdict }) {
    const color = verdictColors[verdict] || "#616161";
    return (
        <span
            style={{
                display: "inline-block",
                padding: "4px 12px",
                borderRadius: 6,
                background: color,
                color: "#fff",
                fontWeight: 600,
                fontSize: 13,
                textTransform: "uppercase",
            }}
        >
            {verdict}
        </span>
    );
}

export default function IOCLookup() {
    const [params] = useSearchParams();
    const navigate = useNavigate();

    const indicatorParam = params.get("indicator");
    const from = params.get("from");

    const [inputValue, setInputValue] = useState(indicatorParam || "");
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    async function runLookup(indicator) {
        setLoading(true);
        setError(null);
        setResult(null);

        try {
            const response = await api.post("/ioc/lookup", { indicator });
            setResult(response.data);
        } catch (err) {
            const message =
                err.response?.data?.detail || err.message || "Lookup failed";
            setError(message);
        } finally {
            setLoading(false);
        }
    }

    useEffect(() => {
        if (indicatorParam) {
            runLookup(indicatorParam);
        }
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [indicatorParam]);

    function handleSubmit(e) {
        e.preventDefault();
        if (inputValue.trim()) {
            runLookup(inputValue.trim());
        }
    }

    const cardStyle = {
        background: "#fff",
        border: "1px solid #e0e0e0",
        borderRadius: 8,
        padding: 20,
        marginTop: 16,
    };

    return (
        <div style={{ padding: 40, maxWidth: 720 }}>
            {from && (
                <div style={{ marginBottom: 16 }}>
                    <button
                        onClick={() => navigate(`/phishing/${from}`)}
                        style={{
                            background: "none",
                            border: "none",
                            color: "#16233f",
                            cursor: "pointer",
                            fontSize: 14,
                        }}
                    >
                        ← Back to analysis
                    </button>
                </div>
            )}

            <h1 style={{ marginBottom: 4 }}>IOC Lookup</h1>
            <p style={{ color: "#666", marginBottom: 20 }}>
                Investigate an IP, domain, URL or hash
            </p>

            <form onSubmit={handleSubmit} style={{ display: "flex", gap: 8 }}>
                <input
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    placeholder="Enter IOC (IP, domain, URL, or hash)"
                    style={{
                        flex: 1,
                        padding: "10px 12px",
                        border: "1px solid #ccc",
                        borderRadius: 6,
                        fontSize: 14,
                    }}
                />
                <button
                    type="submit"
                    disabled={loading}
                    style={{
                        padding: "10px 20px",
                        background: "#16233f",
                        color: "#fff",
                        border: "none",
                        borderRadius: 6,
                        cursor: loading ? "not-allowed" : "pointer",
                        opacity: loading ? 0.6 : 1,
                    }}
                >
                    {loading ? "Looking up..." : "Lookup"}
                </button>
            </form>

            {loading && <p style={{ marginTop: 16 }}>Loading...</p>}

            {error && (
                <div style={{ ...cardStyle, borderColor: "#c62828", color: "#c62828" }}>
                    {error}
                </div>
            )}

            {!loading && !error && !result && (
                <p style={{ marginTop: 16, color: "#999" }}>
                    Enter an indicator above to begin
                </p>
            )}

            {result && (
                <>
                    <div style={cardStyle}>
                        <p style={{ color: "#666", margin: 0 }}>Indicator</p>
                        <h3 style={{ margin: "4px 0 12px" }}>{result.indicator}</h3>

                        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                            <span style={{ fontSize: 32, fontWeight: 700 }}>
                                {result.risk_score}
                            </span>
                            <VerdictBadge verdict={result.verdict} />
                        </div>
                    </div>

                    <div style={cardStyle}>
                        <h4 style={{ marginTop: 0, marginBottom: 8 }}>Sources</h4>
                        {result.sources.length === 0 && (
                            <p style={{ color: "#999" }}>No sources returned data.</p>
                        )}
                        {result.sources.map((s, idx) => (
                            <div
                                key={idx}
                                style={{
                                    display: "flex",
                                    justifyContent: "space-between",
                                    alignItems: "center",
                                    padding: "8px 0",
                                    borderBottom:
                                        idx < result.sources.length - 1
                                            ? "1px solid #eee"
                                            : "none",
                                }}
                            >
                                <span>{s.name}</span>
                                <VerdictBadge verdict={s.result} />
                            </div>
                        ))}
                    </div>

                    <div style={cardStyle}>
                        <h4 style={{ marginTop: 0, marginBottom: 8 }}>Enrichment</h4>
                        {result.enrichment.geolocation && (
                            <p>Geolocation: {result.enrichment.geolocation}</p>
                        )}
                        {result.enrichment.asn && <p>ASN: {result.enrichment.asn}</p>}
                        {result.enrichment.domain_age_days != null && (
                            <p>Domain age: {result.enrichment.domain_age_days} days</p>
                        )}
                        {result.enrichment.registrar && (
                            <p>Registrar: {result.enrichment.registrar}</p>
                        )}
                        <p>Blacklisted: {result.enrichment.blacklisted ? "Yes" : "No"}</p>
                    </div>
                </>
            )}
        </div>
    );
}
