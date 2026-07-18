import streamlit as st

st.set_page_config(
    page_title="Industrial Energy Modeling | Berkeley Lab",
    page_icon="⚙️",
    layout="wide",
)

contributors = [
    {
        "name": "Akash Patil",
        "profile": "https://energyanalysis.lbl.gov/people/akash-kailas-patil",
        "title": "Postdoctoral Researcher, Energy Analysis Division",
        "email": "apatil2@lbl.gov",
        "photo": "https://raw.githubusercontent.com/apatil210/LDRD4/main/Akashpic2.jpg",
    },
    {
        "name": "Jibran Zuberi",
        "profile": "https://eta.lbl.gov/people/jibran-zuberi",
        "title": "Energy/Environmental Policy Research Scientist/Engineer, Energy Analysis Division",
        "email": "mjszuberi@lbl.gov",
        "photo": "https://raw.githubusercontent.com/apatil210/LDRD4/main/Jibran.jpg",
    },
    {
        "name": "Prakash Rao",
        "profile": "https://eta.lbl.gov/people/prakash-rao",
        "title": "Head · Building & Industrial Applications Department",
        "email": "prao@lbl.gov",
        "photo": "https://raw.githubusercontent.com/apatil210/LDRD4/main/Prakash.jpg",
    },
    {
        "name": "Unique Karki",
        "profile": "https://eta.lbl.gov/people/unique-karki",
        "title": "Technology Researcher II · Building & Industrial Energy Systems Division",
        "email": "ukarki@lbl.gov",
        "photo": "https://raw.githubusercontent.com/apatil210/LDRD4/main/Unique.jpg",
    },
]

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Libre+Franklin:wght@400;500;600;700;800&family=Source+Serif+4:opsz,wght@8..60,400;8..60,500;8..60,600&display=swap');

    :root {
        --lbl-blue: #00313c;
        --lbl-teal: #007681;
        --lbl-dark-gray: #63666a;
        --lbl-orange: #d57800;
        --bg: #f7f9f9;
        --surface: #ffffff;
        --surface-soft: #eef4f4;
        --text: #0b1f27;
        --muted: #4e5f66;
        --border: rgba(0, 49, 60, 0.12);
        --shadow-sm: 0 8px 24px rgba(0, 49, 60, 0.06);
        --shadow-lg: 0 22px 50px rgba(0, 49, 60, 0.10);
        --max-width: 1240px;
    }

    .stApp {
        background: linear-gradient(180deg, #fbfcfc 0%, #f3f7f7 45%, #eef3f4 100%);
        color: var(--text);
    }

    .block-container {
        max-width: var(--max-width);
        padding-top: 1.2rem;
        padding-bottom: 3rem;
        padding-left: 1.5rem;
        padding-right: 1.5rem;
    }

    .topbar {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        border-bottom: 1px solid rgba(0, 49, 60, 0.10);
        padding: 0.3rem 0 1rem 0;
        margin-bottom: 1.3rem;
    }

    .brand-lockup {
        display: flex;
        align-items: center;
        gap: 0.95rem;
    }

    .brand-mark {
        width: 52px;
        height: 52px;
        background: linear-gradient(180deg, var(--lbl-blue) 0%, #0a4854 100%);
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: var(--shadow-sm);
        flex: 0 0 52px;
        border-radius: 0;
    }

    .brand-svg {
        width: 30px;
        height: 30px;
        color: white;
    }

    .brand-text-top {
        font: 700 0.78rem/1 'Libre Franklin', sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--lbl-teal);
        margin-bottom: 0.28rem;
    }

    .brand-text-main {
        font: 800 1.08rem/1.1 'Libre Franklin', sans-serif;
        color: var(--lbl-blue);
        letter-spacing: -0.02em;
    }

    .brand-meta {
        font: 600 0.82rem/1.35 'Libre Franklin', sans-serif;
        color: var(--lbl-dark-gray);
        text-align: right;
    }

    .hero {
        background: #ffffff;
        border: 1px solid var(--border);
        border-top: 4px solid var(--lbl-teal);
        border-radius: 0;
        padding: 2.5rem 2.5rem 2.2rem 2.5rem;
        box-shadow: var(--shadow-lg);
        margin-bottom: 1.5rem;
    }

    .hero-grid {
        display: grid;
        grid-template-columns: minmax(0, 1.7fr) minmax(280px, 0.8fr);
        gap: 2.5rem;
        align-items: start;
    }

    .hero-main {
        max-width: 760px;
    }

    .kicker {
        display: inline-block;
        font: 700 0.78rem/1 'Libre Franklin', sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--lbl-teal);
        margin-bottom: 1rem;
    }

    .hero-title {
        font-family: 'Libre Franklin', sans-serif;
        font-size: clamp(2.5rem, 2rem + 1.6vw, 4.25rem);
        font-weight: 800;
        line-height: 0.98;
        letter-spacing: -0.05em;
        color: var(--lbl-blue);
        max-width: none;
        margin: 0 0 1.2rem 0;
    }

    .hero-copy {
        font-family: 'Source Serif 4', serif;
        font-size: 1.08rem;
        line-height: 1.78;
        color: #334952;
        max-width: 60ch;
        margin: 0;
    }

    .hero-panel {
        background: #f6f9f9;
        border: 1px solid rgba(0, 49, 60, 0.10);
        padding: 1.35rem 1.35rem 1.2rem 1.35rem;
        box-shadow: var(--shadow-sm);
        border-radius: 0;
    }

    .hero-panel-label {
        font: 700 0.75rem/1 'Libre Franklin', sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--lbl-teal);
        margin-bottom: 0.8rem;
    }

    .hero-panel h3 {
        font: 800 1.2rem/1.2 'Libre Franklin', sans-serif;
        color: var(--lbl-blue);
        margin: 0 0 0.9rem 0;
        letter-spacing: -0.02em;
    }

    .focus-list {
        margin: 0;
        padding: 0;
        list-style: none;
        display: grid;
        gap: 0.8rem;
    }

    .focus-item {
        position: relative;
        padding-left: 1rem;
        font: 500 0.92rem/1.55 'Libre Franklin', sans-serif;
        color: #35505a;
    }

    .focus-item::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0.52rem;
        width: 6px;
        height: 6px;
        background: var(--lbl-orange);
    }

    .section {
        background: #ffffff;
        border: 1px solid var(--border);
        border-radius: 0;
        padding: 1.8rem;
        box-shadow: var(--shadow-sm);
        margin-top: 1.3rem;
    }

    .section-title {
        font: 800 clamp(1.35rem, 1.1rem + 0.75vw, 1.95rem)/1.1 'Libre Franklin', sans-serif;
        color: var(--lbl-blue);
        margin: 0 0 0.75rem 0;
        letter-spacing: -0.03em;
    }

    .section-copy {
        font: 400 1.06rem/1.78 'Source Serif 4', serif;
        color: #334952;
        margin: 0;
    }

    .resource-intro {
        margin-top: 0.3rem;
        margin-bottom: 0.3rem;
        font: 500 0.96rem/1.55 'Libre Franklin', sans-serif;
        color: var(--muted);
    }

    .resource-intro a {
        color: var(--lbl-teal);
        font-weight: 700;
        text-decoration: none;
    }

    .resource-intro a:hover {
        text-decoration: underline;
    }

    .nav-link {
        text-decoration: none;
        display: block;
        width: 100%;
    }

    .nav-card {
        background: #ffffff;
        border: 1px solid rgba(0, 49, 60, 0.12);
        border-top: 4px solid var(--lbl-teal);
        color: var(--text);
        min-height: 215px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 1.35rem;
        box-shadow: var(--shadow-sm);
        margin: 0.2rem 0 0.6rem 0;
        border-radius: 0;
        transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease;
    }

    .nav-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 18px 36px rgba(0, 49, 60, 0.11);
        border-color: rgba(0, 118, 129, 0.28);
    }

    .nav-kicker {
        font: 700 0.76rem/1 'Libre Franklin', sans-serif;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--lbl-teal);
        margin-bottom: 0.95rem;
    }

    .nav-title {
        font: 800 1.38rem/1.12 'Libre Franklin', sans-serif;
        color: var(--lbl-blue);
        margin-bottom: 0.65rem;
        letter-spacing: -0.03em;
    }

    .nav-copy {
        font: 400 1rem/1.7 'Source Serif 4', serif;
        color: #35505a;
        margin: 0 0 1.1rem 0;
    }

    .nav-footer {
        font: 700 0.92rem/1 'Libre Franklin', sans-serif;
        color: var(--lbl-blue);
    }

    .team-grid {
        display: grid;
        grid-template-columns: repeat(4, minmax(0, 1fr));
        gap: 1rem;
        margin-top: 1.2rem;
    }

    .person-card {
        background: #ffffff;
        border: 1px solid rgba(0, 49, 60, 0.10);
        border-radius: 0;
        overflow: hidden;
        box-shadow: var(--shadow-sm);
        height: 100%;
        display: flex;
        flex-direction: column;
    }

    .person-photo-wrap {
        background: #e7eff1;
        padding: 0;
    }

    .person-photo-frame {
        width: 100%;
        height: 285px;
        border-bottom: 1px solid rgba(0, 49, 60, 0.10);
        background-color: #dfe8ea;
        background-repeat: no-repeat;
        background-position: center center;
        background-size: cover;
    }

    .person-body {
        padding: 1rem 1rem 1.15rem 1rem;
    }

    .person-name {
        font: 800 1.02rem/1.2 'Libre Franklin', sans-serif;
        color: var(--lbl-blue);
        margin: 0 0 0.45rem 0;
    }

    .person-name a {
        color: var(--lbl-blue);
        text-decoration: none;
    }

    .person-name a:hover {
        color: var(--lbl-teal);
        text-decoration: underline;
    }

    .person-title {
        font: 500 0.9rem/1.55 'Libre Franklin', sans-serif;
        color: var(--lbl-dark-gray);
        margin: 0;
        min-height: 4.5rem;
    }

    .person-email {
        font: 500 0.88rem/1.5 'Libre Franklin', sans-serif;
        color: var(--lbl-teal);
        margin-top: 0.7rem;
    }

    .funding-copy {
        font: 500 0.98rem/1.6 'Libre Franklin', sans-serif;
        color: var(--lbl-dark-gray);
        margin: 0.2rem 0 0 0;
        letter-spacing: 0.01em;
    }

    .funding-copy strong {
        color: var(--lbl-blue);
        font-weight: 700;
    }

    div[data-testid="column"] {
        display: flex;
    }

    @media (max-width: 1100px) {
        .hero-grid {
            grid-template-columns: 1fr;
            gap: 1.5rem;
        }

        .team-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }

        .hero-title {
            max-width: 11ch;
        }
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
            padding-top: 0.8rem;
        }

        .topbar {
            flex-direction: column;
            align-items: flex-start;
        }

        .brand-meta {
            text-align: left;
        }

        .hero,
        .section {
            padding: 1.4rem;
        }

        .team-grid {
            grid-template-columns: 1fr;
        }

        .person-photo-frame {
            height: 320px;
        }

        .hero-title {
            font-size: clamp(2rem, 1.7rem + 2vw, 2.8rem);
            max-width: none;
        }

        .hero-copy {
            max-width: none;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="hero">
        <div class="hero-grid">
            <div class="hero-main">
                <div class="kicker">Research platform</div>
                <h1 class="hero-title">2022 U.S. Manufacturing Energy Demand Mapped to the Unit Operation Level</h1>
            </div>
        </div>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="section">
        <h2 class="section-title">Project Statement</h2>
        <p class="section-copy">
            Industry comprises thermodynamic, mechanical, and chemical transformations that are built from distinct unit operations. While the number, order, and configuration of these operations differ by subsector, many core operations recur across manufacturing systems. Despite that common structure, industrial energy demand is still rarely analyzed at the unit-operation level. This project develops a framework to disaggregate industrial processes into unit operations, quantify their energy demand profiles, and identify high-priority operations where technological advances can deliver broad system-wide benefit.
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="section">
        <h2 class="section-title">Data Resources</h2>
        <p class="resource-intro">Access the core datasets and coverage views that support the analytical framework.</p>
        <p class="resource-intro">
            <a href="https://github.com/apatil210/LDRD4/raw/refs/heads/main/2022-Energy-Demand-in-US-Industry.xlsx" target="_blank" rel="noopener noreferrer">
                Click here to download the spreadsheet for the 2022 manufacturing energy data
            </a>
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3, gap="large")

cards = [
    (
        col1,
        "Industry data",
        "Process library",
        "Browse industrial process records and the supporting evidence base assembled for the project.",
        "https://panel1v2py-c84ntaz8ryya3qefuxwux4.streamlit.app/",
    ),
    (
        col2,
        "Unit operation data",
        "Operation insights",
        "Explore mapped unit operations, their functional role in processes, and their energy demand.",
        "https://panel2v2py-f77d26ywjtutbsrsp6bihl.streamlit.app/",
    ),
    (
        col3,
        "NAICS coverage",
        "Sector representation",
        "Review how the developed energy dataset maps across manufacturing sectors classified by NAICS codes.",
        "https://panel3v2py-xe4lhzbjsfgekryipzv6wh.streamlit.app/",
    ),
]

for col, kicker, title, copy, url in cards:
    with col:
        st.markdown(
            f'''
            <a class="nav-link" href="{url}" target="_blank" rel="noopener noreferrer">
                <article class="nav-card">
                    <div>
                        <div class="nav-kicker">{kicker}</div>
                        <div class="nav-title">{title}</div>
                        <div class="nav-copy">{copy}</div>
                    </div>
                    <div class="nav-footer">Open resource →</div>
                </article>
            </a>
            ''',
            unsafe_allow_html=True,
        )

cards_html = "".join(
    f'''
    <article class="person-card">
        <div class="person-photo-wrap">
            <div class="person-photo-frame" role="img" aria-label="Portrait of {c["name"]}" style="background-image: url('{c["photo"]}');"></div>
        </div>
        <div class="person-body">
            <h3 class="person-name">
                <a href="{c["profile"]}" target="_blank" rel="noopener noreferrer">{c["name"]}</a>
            </h3>
            <p class="person-title">{c["title"]}</p>
            <p class="person-email">✉ {c["email"]}</p>
        </div>
    </article>
    '''
    for c in contributors
)

st.markdown(
    f'''
    <section class="section">
        <h2 class="section-title">Research Team</h2>
        <div class="team-grid">{cards_html}</div>
    </section>
    ''',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <section class="section">
        <h2 class="section-title">Funding Acknowledgement</h2>
        <p class="funding-copy">
            Laboratory Directed Research and Development (LDRD) Program (FY 2025–26), sponsored by Lawrence Berkeley National Laboratory (LBNL).
        </p>
    </section>
    """,
    unsafe_allow_html=True,
)
