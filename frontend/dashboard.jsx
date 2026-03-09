import { useState, useEffect } from "react";

const MOCK_DATA = [
  { id: 1, vertical: "leilao", titulo: "Apartamento 3 quartos, 87m2", bairro: "Boa Viagem", cidade: "Recife", preco: 185000, mercado: 380000, desconto: 51.3, score: 97, motivo: "Leilao 51% abaixo da avaliacao oficial", fonte: "Caixa", novo: true },
  { id: 2, vertical: "imovel", titulo: "Cobertura Duplex 4 suites, 210m2", bairro: "Meireles", cidade: "Fortaleza", preco: 620000, mercado: 980000, desconto: 36.7, score: 89, motivo: "36% abaixo da mediana do bairro | R$2.952/m2 vs R$4.667/m2", fonte: "OLX", novo: true },
  { id: 3, vertical: "veiculo", titulo: "Toyota Corolla 2021 XEi Automatico", bairro: "", cidade: "Sao Paulo", preco: 82000, mercado: 118000, desconto: 30.5, score: 83, motivo: "30% abaixo da FIPE | 45.000 km rodados", fonte: "OLX", novo: false },
  { id: 4, vertical: "leilao", titulo: "Sala Comercial 42m2, Centro Historico", bairro: "Centro", cidade: "Recife", preco: 42000, mercado: 85000, desconto: 50.6, score: 91, motivo: "Leilao 50% abaixo da avaliacao | 2a praca", fonte: "Mega Leiloes", novo: false },
  { id: 5, vertical: "imovel", titulo: "Casa 4 quartos, 180m2, Condominio", bairro: "Alphaville", cidade: "Recife", preco: 450000, mercado: 650000, desconto: 30.8, score: 78, motivo: "31% abaixo do mercado local", fonte: "ZAP", novo: false },
];

const VC = {
  imovel:  { border: "#10b981", label: "IMOVEL",  dot: "#10b981" },
  leilao:  { border: "#f59e0b", label: "LEILAO",  dot: "#f59e0b" },
  veiculo: { border: "#6366f1", label: "VEICULO", dot: "#6366f1" },
};

function ScoreRing({ score }) {
  const r = 18, circ = 2 * Math.PI * r;
  const color = score >= 85 ? "#f59e0b" : score >= 70 ? "#10b981" : "#6366f1";
  return (
    <svg width="48" height="48" viewBox="0 0 48 48">
      <circle cx="24" cy="24" r={r} fill="none" stroke="rgba(255,255,255,0.06)" strokeWidth="3" />
      <circle cx="24" cy="24" r={r} fill="none" stroke={color} strokeWidth="3"
        strokeDasharray={circ} strokeDashoffset={circ * (1 - score / 100)}
        strokeLinecap="round" transform="rotate(-90 24 24)"
        style={{ transition: "stroke-dashoffset 1s ease" }} />
      <text x="24" y="28" textAnchor="middle" fill={color} fontSize="11"
        fontFamily="monospace" fontWeight="700">{score}</text>
    </svg>
  );
}

export default function App() {
  const [filtro, setFiltro] = useState("todos");
  const [hora, setHora] = useState(new Date());

  useEffect(() => {
    const t = setInterval(() => setHora(new Date()), 1000);
    return () => clearInterval(t);
  }, []);

  const filtrados = MOCK_DATA.filter(i => filtro === "todos" || i.vertical === filtro);

  return (
    <div style={{ minHeight: "100vh", background: "#070b14", color: "#e2e8f0", fontFamily: "system-ui", padding: "24px 20px", maxWidth: 860, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 28 }}>
        <div>
          <div style={{ fontSize: 20, fontFamily: "monospace", fontWeight: 800, letterSpacing: 3, color: "#e2e8f0" }}>DATA_HUNTER</div>
          <div style={{ fontSize: 11, color: "#475569", fontFamily: "monospace" }}>DETECCAO DE ANOMALIAS DE PRECO</div>
        </div>
        <div style={{ fontSize: 13, fontFamily: "monospace", color: "#334155", alignSelf: "center" }}>
          {hora.toLocaleTimeString("pt-BR")}
        </div>
      </div>
      <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
        {[["todos","Todos"],["imovel","Imoveis"],["leilao","Leiloes"],["veiculo","Veiculos"]].map(([v,l]) => (
          <button key={v} onClick={() => setFiltro(v)} style={{
            background: filtro===v ? "rgba(16,185,129,0.15)" : "rgba(255,255,255,0.02)",
            border: "1px solid " + (filtro===v ? "rgba(16,185,129,0.4)" : "rgba(255,255,255,0.07)"),
            color: filtro===v ? "#10b981" : "#475569",
            borderRadius: 6, padding: "6px 14px", cursor: "pointer", fontSize: 12, fontFamily: "monospace"
          }}>{l}</button>
        ))}
      </div>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        {filtrados.map(item => {
          const vc = VC[item.vertical];
          return (
            <div key={item.id} style={{
              background: "rgba(255,255,255,0.02)", border: "1px solid " + vc.border + "22",
              borderLeft: "3px solid " + vc.border, borderRadius: 8, padding: "16px 18px",
              display: "flex", gap: 14, alignItems: "flex-start",
            }}>
              <ScoreRing score={item.score} />
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                  <span style={{ fontSize: 9, fontFamily: "monospace", color: vc.dot, background: vc.dot + "18", padding: "2px 8px", borderRadius: 3 }}>{vc.label}</span>
                  <span style={{ fontSize: 10, color: "#ffffff33", fontFamily: "monospace" }}>{item.fonte} - {item.cidade}</span>
                  {item.novo && <span style={{ fontSize: 9, color: "#f59e0b", fontFamily: "monospace" }}>NOVO</span>}
                </div>
                <div style={{ fontSize: 14, color: "#e2e8f0", fontWeight: 600, marginBottom: 4 }}>{item.titulo}</div>
                <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 8 }}>{item.motivo}</div>
                <div style={{ display: "flex", gap: 20, alignItems: "center" }}>
                  <div>
                    <div style={{ fontSize: 10, color: "#ffffff33", fontFamily: "monospace" }}>PRECO</div>
                    <div style={{ fontSize: 16, fontFamily: "monospace", fontWeight: 700 }}>R${item.preco.toLocaleString("pt-BR")}</div>
                  </div>
                  <span style={{ color: "#ffffff22" }}>vs</span>
                  <div>
                    <div style={{ fontSize: 10, color: "#ffffff33", fontFamily: "monospace" }}>MERCADO</div>
                    <div style={{ fontSize: 13, fontFamily: "monospace", color: "#64748b", textDecoration: "line-through" }}>R${item.mercado.toLocaleString("pt-BR")}</div>
                  </div>
                  <div style={{ marginLeft: "auto", background: "rgba(239,68,68,0.12)", border: "1px solid rgba(239,68,68,0.3)", borderRadius: 6, padding: "6px 12px" }}>
                    <div style={{ fontSize: 18, fontFamily: "monospace", fontWeight: 800, color: "#f87171" }}>-{item.desconto}%</div>
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}