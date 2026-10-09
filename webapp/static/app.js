console.log("APP JS LOADED");

/*
=========================================
ANALYZE DATASET
=========================================
*/

async function analyzeDataset() {

    try {

        console.log("Analyze button clicked");

        const response = await fetch(
            "/analyze",
            {
                method: "POST"
            }
        );

        const data = await response.json();

        console.log(data);

        const resultsDiv =
            document.getElementById("results");

        resultsDiv.innerHTML = `
            <h2>Business Overview</h2>

            <div class="kpi-container">

                <div class="kpi-card">
                    <div class="kpi-title">Revenue</div>
                    <div class="kpi-value">
                        $${data.kpis.total_revenue_usd_m}M
                    </div>
                </div>

                <div class="kpi-card">
                    <div class="kpi-title">QoQ Growth</div>
                    <div class="kpi-value">
                        ${data.kpis.revenue_qoq_growth_pct.toFixed(2)}%
                    </div>
                </div>

                <div class="kpi-card">
                    <div class="kpi-title">Regional NPS</div>
                    <div class="kpi-value">
                        ${data.kpis.unweighted_regional_nps.toFixed(2)}
                    </div>
                </div>

                <div class="kpi-card">
                    <div class="kpi-title">Growth Region</div>
                    <div class="kpi-value">
                        ${data.growth_region}
                    </div>
                </div>

                <div class="kpi-card">
                    <div class="kpi-title">Risk Region</div>
                    <div class="kpi-value">
                        ${data.risk_region}
                    </div>
                </div>

            </div>
        `;

    }
    catch(error) {

        console.error(error);

        alert(
            "Failed to analyze dataset."
        );
    }
}


/*
=========================================
GENERATE AI CONTENT
=========================================
*/

async function generateContent() {

    try {
        const narrativeDiv =
            document.getElementById(
                "narrative"
            );

        narrativeDiv.innerHTML = `
            <div class="card">
                <h2>
                    Generating AI Narrative...
                </h2>

                <p>
                    Gemini is analyzing the
                    data and creating executive
                    insights.
                </p>
            </div>
        `;

        const response =
            await fetch(
                "/generate-content",
                {
                    method: "POST"
                }
            );

        const data =
            await response.json();

        console.log(data);

        let html =
            "<h2>AI Executive Narrative</h2>";

        const content =
            data.content;

        for (const slideKey in content) {

            const slide =
                content[slideKey];

            html += `
                <div class="card">

                    <h3>
                        ${slide.title || slideKey}
                    </h3>
            `;

            if (slide.summary) {

                html += `
                    <p>
                        ${slide.summary}
                    </p>
                `;
            }

            if (slide.insights) {

                html += `
                    <ul>
                `;

                slide.insights.forEach(
                    insight => {

                        html += `
                            <li>
                                ${insight}
                            </li>
                        `;
                    }
                );

                html += `
                    </ul>
                `;
            }

            if (
                slide.recommendations
            ) {

                html += `
                    <h4>
                        Recommendations
                    </h4>

                    <ul>
                `;

                slide.recommendations.forEach(
                    item => {

                        html += `
                            <li>
                                ${item}
                            </li>
                        `;
                    }
                );

                html += `
                    </ul>
                `;
            }

            if (slide.closing) {

                html += `
                    <p>
                        <strong>
                            Closing:
                        </strong>

                        ${slide.closing}
                    </p>
                `;
            }

            html += `
                </div>
            `;
        }

        document.getElementById(
            "narrative"
        ).innerHTML = html;

    }
    catch(error) {

        console.error(error);

        alert(
            "Failed to generate AI content."
        );
    }
}

/*
=========================================
BUILD PRESENTATION
=========================================
*/

async function buildPresentation() {

    try {

        const statusDiv =
            document.getElementById(
                "build-status"
            );

        const button =
            document.getElementById(
                "buildBtn"
            );

        button.disabled = true;

        button.innerText =
            "Building Presentation...";

        statusDiv.innerHTML = `
            <div class="card">

                <h2>
                    Building PowerPoint...
                </h2>

                <p>
                    Running analysis,
                    generating content,
                    rendering slides and
                    saving presentation.
                </p>

            </div>
        `;

        const response =
            await fetch(
                "/build-presentation",
                {
                    method: "POST"
                }
            );

        const data =
            await response.json();

        console.log(data);

        button.disabled = false;

        button.innerText =
            "Build Presentation";

        if (
            data.status === "success"
        ) {

            statusDiv.innerHTML = `

                <div class="card">

                    <h2>
                        ✅ Presentation Created
                    </h2>

                    <p>
                        Quarter:
                        ${data.quarter}
                    </p>

                    <p>
                        Slide Count:
                        ${data.slide_count}
                    </p>

                    <br>

                <a href="/download-ppt" class="btn">
                    Download Presentation
                </a>

                </div>

            `;
        }
        else {

            statusDiv.innerHTML = `
                <div class="card">

                    <h2>
                        ❌ Build Failed
                    </h2>

                    <p>
                        Stage:
                        ${data.stage}
                    </p>

                    <p>
                        ${data.next_step}
                    </p>

                </div>
            `;
        }

    }
    catch(error) {

        console.error(error);

        alert(
            "Failed to build presentation."
        );
    }
}

function showInstructions() {

    document.getElementById(
        "instructionsModal"
    ).style.display = "block";
}

function closeInstructions() {

    document.getElementById(
        "instructionsModal"
    ).style.display = "none";
}