<template>
  <div class="view-content">
    <h2 class="page-title">Issue 3: Third-Party Dependencies</h2>
    <p class="page-subtitle">Supply chain attack surface — package inventory and blast radius per layer</p>

    <!-- Client-side packages -->
    <div class="card">
      <h3 style="margin-bottom:14px">Client-side packages (run in the browser)</h3>
      <table style="width:100%;border-collapse:collapse;font-size:13px">
        <thead>
          <tr style="border-bottom:2px solid var(--border);text-align:left">
            <th style="padding:8px 10px">Package</th>
            <th style="padding:8px 10px">Source</th>
            <th style="padding:8px 10px">If compromised, reaches…</th>
          </tr>
        </thead>
        <tbody>
          <tr style="border-bottom:1px solid var(--border)">
            <td style="padding:8px 10px"><code>vue 3.4.x</code></td>
            <td style="padding:8px 10px">npm</td>
            <td style="padding:8px 10px">Full DOM, component state, all reactive data</td>
          </tr>
          <tr style="border-bottom:1px solid var(--border)">
            <td style="padding:8px 10px"><code>vue-router 4.3.x</code></td>
            <td style="padding:8px 10px">npm</td>
            <td style="padding:8px 10px">Navigation history, route params</td>
          </tr>
          <tr style="border-bottom:1px solid var(--border)">
            <td style="padding:8px 10px"><code>@vitejs/plugin-vue 5.x</code></td>
            <td style="padding:8px 10px">npm (build-time)</td>
            <td style="padding:8px 10px">Malicious code injected at build time lands silently in the browser bundle</td>
          </tr>
          <tr style="border-bottom:1px solid var(--border)">
            <td style="padding:8px 10px"><code>vite 5.x</code></td>
            <td style="padding:8px 10px">npm (build-time)</td>
            <td style="padding:8px 10px">Same as above</td>
          </tr>
        </tbody>
      </table>
      <div style="margin-top:12px;padding:10px 12px;background:var(--danger-bg, rgba(220,50,50,0.08));border:1px solid var(--danger-text, #c0392b);border-radius:4px;font-size:13px">
        <strong>Client blast radius:</strong> <code>localStorage</code> (JWT), full DOM, all in-page fetch calls, navigation state. A stolen JWT is usable from any machine until it expires.
      </div>
      <p style="margin-top:10px;font-size:12px;color:var(--text-muted)">
        In a production SPA, CDN-loaded scripts (analytics, error tracking) would also appear here — each one is an additional entry point with the same reach.
      </p>
    </div>

    <!-- Server-side packages -->
    <div class="card">
      <h3 style="margin-bottom:14px">Server-side packages (run on the server)</h3>
      <table style="width:100%;border-collapse:collapse;font-size:13px">
        <thead>
          <tr style="border-bottom:2px solid var(--border);text-align:left">
            <th style="padding:8px 10px">Package</th>
            <th style="padding:8px 10px">Source</th>
            <th style="padding:8px 10px">If compromised, reaches…</th>
          </tr>
        </thead>
        <tbody>
          <tr style="border-bottom:1px solid var(--border)">
            <td style="padding:8px 10px"><code>apiflask</code></td>
            <td style="padding:8px 10px">pip</td>
            <td style="padding:8px 10px">Full request/response pipeline</td>
          </tr>
          <tr style="border-bottom:1px solid var(--border)">
            <td style="padding:8px 10px"><code>PyJWT</code></td>
            <td style="padding:8px 10px">pip</td>
            <td style="padding:8px 10px">JWT signing key — ability to forge tokens for any user</td>
          </tr>
          <tr style="border-bottom:1px solid var(--border)">
            <td style="padding:8px 10px"><code>werkzeug</code></td>
            <td style="padding:8px 10px">pip</td>
            <td style="padding:8px 10px">Password hashes, request parsing</td>
          </tr>
          <tr style="border-bottom:1px solid var(--border)">
            <td style="padding:8px 10px"><code>flask-cors</code></td>
            <td style="padding:8px 10px">pip</td>
            <td style="padding:8px 10px">CORS policy, response headers</td>
          </tr>
          <tr style="border-bottom:1px solid var(--border)">
            <td style="padding:8px 10px"><code>python-dotenv</code></td>
            <td style="padding:8px 10px">pip</td>
            <td style="padding:8px 10px"><code>.env</code> contents including <code>SECRET_KEY</code></td>
          </tr>
        </tbody>
      </table>
      <div style="margin-top:12px;padding:10px 12px;background:var(--danger-bg, rgba(220,50,50,0.08));border:1px solid var(--danger-text, #c0392b);border-radius:4px;font-size:13px">
        <strong>Server blast radius:</strong> Entire database (all users, tasks, comments, password hashes, secret_notes), all active sessions, SECRET_KEY, JWT signing key, filesystem.
      </div>
    </div>

    <!-- Side-by-side narrative -->
    <div class="card">
      <h3 style="margin-bottom:14px">Attack surface comparison</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:20px">
        <div>
          <h4 style="margin-bottom:8px;font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:var(--text-muted)">SPA</h4>
          <ul style="padding-left:16px;font-size:13px;line-height:2">
            <li>4 npm packages run in or inject into the browser</li>
            <li>Full npm transitive dependency graph</li>
            <li>Build-time packages inject into the browser bundle</li>
            <li>Compromised package can read <code>localStorage</code> (JWT)</li>
            <li>JWT stolen client-side is portable until expiry</li>
            <li>Server layer: Flask + pip (5 packages)</li>
          </ul>
        </div>
        <div>
          <h4 style="margin-bottom:8px;font-size:13px;text-transform:uppercase;letter-spacing:.05em;color:var(--text-muted)">HDA</h4>
          <ul style="padding-left:16px;font-size:13px;line-height:2">
            <li>1 vendored file in browser, no transitive npm deps</li>
            <li>No build pipeline touching browser code</li>
            <li>Compromised script reaches DOM + session riding only</li>
            <li>No credential in <code>localStorage</code></li>
            <li>Attack window closes when tab closes</li>
            <li>Server layer: Flask + pip (4 packages)</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Repro / explanation block -->
    <div class="repro-block">
      <h3 style="margin-bottom:8px">Notes</h3>
      <p style="line-height:1.7;font-size:13px">
        A supply chain attack on a <strong>server-side pip package</strong> has the same blast radius on both architectures —
        the server process sees the full database, all sessions, and every secret. Neither architecture offers a structural advantage here.
      </p>
      <p style="margin-top:10px;line-height:1.7;font-size:13px">
        The asymmetry is at the <strong>client layer</strong>. The SPA ships a JavaScript bundle to every browser that visits it.
        Any compromised package in that bundle, either direct or transitive, 
        runs alongside the application with access to everything the page can reach, including the JWT in <code>localStorage</code>.
        A stolen JWT works from any machine until it expires.
      </p>
      <p style="margin-top:10px;line-height:1.7;font-size:13px">
        The HDA ships one vendored file. There is no npm graph to compromise. A rogue script on the page can ride the session,
        but it cannot exfiltrate a portable credential. The attack window is bounded by the user's tab.
      </p>
      <div style="margin-top:14px;padding-top:12px;border-top:1px solid var(--repro-border)">
        <strong>Real-world precedents:</strong>
        <ul style="padding-left:16px;font-size:13px;line-height:2;margin-top:6px">
          <li><strong>event-stream (2018)</strong>: malicious code hidden in a transitive npm dependency; affected thousands of downstream packages (<a href="https://safeguard.sh/resources/blog/the-event-stream-npm-attack-explained" target="_blank" rel="noopener">source</a>)</li>
          <li><strong>ua-parser-js (2021)</strong>: npm account hijacked; published versions shipped a crypto miner and credential stealer (<a href="https://safeguard.sh/resources/blog/uaparserjs-npm-package-compromise" target="_blank" rel="noopener">source</a>)</li>
          <li><strong>Polyfill.io (2024)</strong>: CDN domain sold to a threat actor; served malicious JavaScript to 100,000+ sites that loaded the script tag (<a href="https://safeguard.sh/resources/blog/polyfill-io-2024-cdn-domain-ownership-supply-chain" target="_blank" rel="noopener">source</a>)</li>
        </ul>
      </div>
    </div>
  </div>
</template>
