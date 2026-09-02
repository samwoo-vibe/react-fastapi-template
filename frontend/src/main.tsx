import React, { useEffect, useState } from "react";
import type { ReactNode } from "react";
import { createRoot } from "react-dom/client";
import {
  Activity,
  ArrowUpRight,
  Boxes,
  CheckCircle2,
  ChevronRight,
  Clock3,
  Code2,
  Database,
  GitBranch,
  LayoutDashboard,
  Plus,
  Rocket,
  Search,
  Server,
  Settings,
  Sparkles,
} from "lucide-react";
import type { LucideIcon } from "lucide-react";
import "./styles.css";

const navItems: Array<[LucideIcon, string]> = [
  [LayoutDashboard, "개요"],
  [Boxes, "서비스"],
  [Rocket, "배포"],
  [Database, "데이터"],
];

const services = [
  {
    name: "현장 점검 리포트",
    owner: "품질혁신팀",
    stack: "React · FastAPI",
    status: "운영 중",
    tone: "lime",
  },
  {
    name: "견적 검토 도우미",
    owner: "영업기획팀",
    stack: "Next.js · PostgreSQL",
    status: "개발 중",
    tone: "blue",
  },
  {
    name: "공정 이슈 보드",
    owner: "생산관리팀",
    stack: "Vue · Python",
    status: "검토 필요",
    tone: "amber",
  },
];

type Health = {
  status: string;
  database: string;
};

type OverviewResponse = {
  database: string;
  visits: number;
};

function App() {
  const [health, setHealth] = useState<Health>({
    status: "확인 중",
    database: "확인 중",
  });
  const [visits, setVisits] = useState(0);

  useEffect(() => {
    fetch("/api/overview")
      .then((response) => response.json())
      .then((data: OverviewResponse) => {
        setHealth({ status: "정상", database: data.database });
        setVisits(data.visits);
      })
      .catch(() => setHealth({ status: "연결 오류", database: "확인 불가" }));
  }, []);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">S</div>
          <div>
            <strong>SAMWOO AX</strong>
            <span>Citizen Portal</span>
          </div>
        </div>

        <nav>
          {navItems.map(([Icon, label], index) => (
            <button className={index === 0 ? "nav-item active" : "nav-item"} key={label}>
              <Icon size={18} />
              <span>{label}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-note">
          <Sparkles size={18} />
          <strong>아이디어가 있나요?</strong>
          <p>작은 문제부터 서비스로 만들어 보세요.</p>
          <button>제작 가이드 보기</button>
        </div>

        <button className="nav-item settings">
          <Settings size={18} />
          <span>설정</span>
        </button>
      </aside>

      <main>
        <header className="topbar">
          <div className="search">
            <Search size={18} />
            <input aria-label="서비스 검색" placeholder="서비스, 팀 또는 담당자 검색" />
            <kbd>⌘ K</kbd>
          </div>
          <div className="profile">
            <div className="avatar">공개</div>
            <div>
              <strong>공개 방문자</strong>
              <span>인증 미구현</span>
            </div>
          </div>
        </header>

        <div className="content">
          <section className="hero">
            <div>
              <span className="eyebrow">WORKSPACE / OVERVIEW</span>
              <h1>좋은 아이디어를<br />작동하는 서비스로.</h1>
              <p>팀에서 만든 도구와 배포 상태를 한곳에서 확인하세요.</p>
            </div>
            <button className="primary">
              <Plus size={19} />
              새 서비스 시작
            </button>
          </section>

          <section className="metrics">
            <Metric icon={Boxes} label="전체 서비스" value="12" meta="+3 이번 달" />
            <Metric icon={Rocket} label="이번 주 배포" value="28" meta="성공률 96.4%" />
            <Metric icon={Activity} label="플랫폼 상태" value={health.status} meta={`DB ${health.database}`} />
            <Metric
              icon={Clock3}
              label="DB 샘플 레코드"
              value={visits}
              meta="공개 화면은 읽기 전용"
            />
          </section>

          <section className="workspace-grid">
            <div className="panel services-panel">
              <div className="panel-head">
                <div>
                  <span className="section-kicker">SERVICES</span>
                  <h2>최근 서비스</h2>
                </div>
                <button className="text-button">모두 보기 <ArrowUpRight size={16} /></button>
              </div>

              <div className="service-list">
                {services.map((service) => (
                  <article className="service-row" key={service.name}>
                    <div className={`service-icon ${service.tone}`}>
                      <Code2 size={20} />
                    </div>
                    <div className="service-main">
                      <strong>{service.name}</strong>
                      <span>{service.owner} · {service.stack}</span>
                    </div>
                    <span className={`status ${service.tone}`}>{service.status}</span>
                    <ChevronRight className="chevron" size={18} />
                  </article>
                ))}
              </div>
            </div>

            <div className="panel deploy-panel">
              <div className="panel-head">
                <div>
                  <span className="section-kicker">LIVE PIPELINE</span>
                  <h2>현재 배포</h2>
                </div>
                <span className="live-dot">LIVE</span>
              </div>

              <div className="deploy-card">
                <div className="deploy-top">
                  <div className="repo-icon"><GitBranch size={20} /></div>
                  <div>
                    <strong>your-service</strong>
                    <span>dev · 자동 배포</span>
                  </div>
                  <CheckCircle2 className="success-icon" size={23} />
                </div>
                <div className="pipeline">
                  {["소스 감지", "이미지 빌드", "헬스 체크", "서비스 전환"].map((step) => (
                    <div className="pipeline-step" key={step}>
                      <span className="step-dot" />
                      <small>{step}</small>
                    </div>
                  ))}
                </div>
                <div className="deploy-meta">
                  <span><Server size={15} /> Coolify localhost</span>
                  <span>방금 전 완료</span>
                </div>
              </div>
            </div>
          </section>

          <footer>
            <span>Samwoo AX Platform</span>
            <span>React + FastAPI + PostgreSQL · Auto Deploy v2</span>
          </footer>
        </div>
      </main>
    </div>
  );
}

type MetricProps = {
  icon: LucideIcon;
  label: string;
  value: ReactNode;
  meta: string;
};

function Metric({ icon: Icon, label, value, meta }: MetricProps) {
  return (
    <article className="metric">
      <div className="metric-icon"><Icon size={19} /></div>
      <span>{label}</span>
      <strong>{value}</strong>
      <small>{meta}</small>
    </article>
  );
}

const rootElement = document.getElementById("root");

if (!rootElement) {
  throw new Error("Root element was not found");
}

createRoot(rootElement).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
