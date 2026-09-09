User:
/plan Read `spec_04_case_third_party_deps.md`  for what to do, use `background.md` and previous `Depends on:` dependencies specs as
context, and plan the spec implementation. If there are any points unclear or require decision, pause and ask.

Claude:
Good. Now I have everything I need. Let me write the plan.
(see `plan_spec_04.md`)
Ready to code?

Claude:
Starting with the SPA Vue component, then the HDA template.

Both files written. No backend changes needed — both routes already exist and the pages are fully static.

Spec-04 is done. Both Issue 3 pages show:
- Client-side package table with blast radius (asymmetric: SPA has 4 npm packages, HDA has 1 vendored file)
- Server-side package table with blast radius (identical on both — explicitly called out)
- Side-by-side comparison bullets
- Real-world incidents (event-stream, ua-parser-js, Polyfill.io)
- No payload, no interactive demo

User:
Embed source links to the real world events:
https://safeguard.sh/resources/blog/the-event-stream-npm-attack-explained (event-streams)
https://safeguard.sh/resources/blog/uaparserjs-npm-package-compromise (ua-parser-js)
https://safeguard.sh/resources/blog/polyfill-io-2024-cdn-domain-ownership-supply-chain polyfill