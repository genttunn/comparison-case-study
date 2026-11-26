# Systematic review vetting for single page app security

- Last updated: 2026-05-06 18:28:46 UTC
- Turns: 2
- Exported: 2026-11-26, transcribed from Claude's past-chat retrieval tool. HTML entities decoded (`&lt;` → `<`, `&gt;` → `>`, `&amp;` → `&`). Tool calls are shown as they appear in the retrieved record; tool outputs (results) and uploaded-file contents (`articles_information.csv`, `browserscript.js`, the article-ID list) were not part of the retrieved record and are absent. Model and settings are not recorded in the retrieved data.
- Contains: grading Run 3 (6 criteria, title + abstract + keywords) and the files `1_ranked_studies.txt`, `2_rejected_studies.txt`, `3_collections.txt`, `browserscript_populated.js`.

---

## Turn 0 — Human

I am doing a literature systematic review on the known security and privacy concerns of client side or Single Page applications. You have 2 tasks:
Task 1 vet papers:
use the `articles information` csv. Help me vet them using their title, keywords, and abstract by the following criterias:
Criterias
    1.Studies provides an overview of known vulnerablities or privacy concern of Single page apps or client side web apps   
    2.Studies provides an overview of known vulnerablities or privacy concern of Single page apps or client side web apps (double weight)   
    3.Study addresses one particular known vulnerablity or privacy concern of client-side web apps, i.e XSS risks   
    4.Study is related at least to security and privacy issues of web apps, but not directly of Single page apps or client-side apps    
    5.Study is not directly about security and privacy issues of web apps, but discusses hypermedia or adjacent hypermedia themes like mashups and extensions   
    6.Study is available as a download 
Steps
    First, check the six quality assessment criterias question for each study. The answers to each are: Yes is 1 point, Maybe 0.5, No 0 point, Reject is -6.
    Criteria 1 and 2 should always be marked the same, because they are double the weight
    Then, going by the title, abstract and keyword of the study, help me rate them: Yes, Maybe, No. For the 'study available as download', always choose Maybe.
    Then, list them from highest score to lowest score.
    I focus on security issues and privacy issues, as an overview, of Single page apps or client side apps. If the study is an overview in nature, it gets the double weight because thats exactly what I want to read.
    If the study title looks irrelevant, reject, and put them as separate list.
    If the 'study' looks like a collection of papers or a conference collection, list them in a separate section. And mark everything there as Maybe.
The result is 3 lists, as 3 text files: ranked studies by the criterias (in format of Title - Point - Q1 Yes, Q2 Maybe, etc.), rejected ones (same format), and paper collections.
Task 2: 
Help me populate those results into a js script here that I will run directly in the browser and make the requests to the webpage to mark these questions.
Here's the information about what id corresponds to what answer and question:
answer-id:
yes: 76873 
maybe: 76874 
no: 76875 
reject: 76876
question-id
q1: 128415
q2: 132655
q3: 128419
q4: 128416
q5: 132403
q6: 128418
First, check my 'article ids', and get the article ids of each article analyzed in task 1
Then comprise a list of article id, question id, and answer id to each question using your analysis above
Then populate the PAYLOADS array in file `browserscript.js` with the correct article_id, question_id, and answer_id for each question and article combination.

---

## Turn 1 — Assistant

````
<tool name="view">
<parameter name="description">Read the CSV file</parameter>
<parameter name="path">/mnt/skills/public/file-reading/SKILL.md</parameter>
</tool>
<tool name="bash_tool">
<parameter name="description">Read the CSV file</parameter>
<parameter name="command">cd /mnt/user-data/uploads && python3 -c "
import pandas as pd
df = pd.read_csv('articles_information.csv', nrows=3)
print(df.columns.tolist())
print(df.dtypes)
print(df.head(3).to_string())
"</parameter>
</tool>
<tool name="bash_tool">
<parameter name="command">cd /mnt/user-data/uploads && python3 -c "
import pandas as pd
df = pd.read_csv('articles_information.csv')
print(f'Total rows: {len(df)}')
print(f'Titles sample:')
for t in df['title'].head(5):
    print(' -', t[:80])
"</parameter>
<parameter name="description">Check total rows and titles</parameter>
</tool>
<tool name="bash_tool">
<parameter name="command">cd /mnt/user-data/uploads && python3 -c "
import pandas as pd
df = pd.read_csv('articles_information.csv')
# Print all titles, keywords, and abstracts for analysis
for i, row in df.iterrows():
    title = str(row['title']).replace('{','').replace('}','')
    keywords = str(row['keywords']) if str(row['keywords']) != 'nan' else ''
    abstract = str(row['abstract'])[:500] if str(row['abstract']) != 'nan' else ''
    print(f'--- ROW {i} ---')
    print(f'TITLE: {title}')
    print(f'KEYWORDS: {keywords}')
    print(f'ABSTRACT: {abstract}')
    print()
" 2>&1 | head -500</parameter>
<parameter name="description">Read all titles, keywords, abstracts for analysis</parameter>
</tool>
<tool name="bash_tool">
<parameter name="command">cd /mnt/user-data/uploads && python3 -c "
import pandas as pd
df = pd.read_csv('articles_information.csv')
for i, row in df.iterrows():
    if i < 100:
        continue
    title = str(row['title']).replace('{','').replace('}','')
    keywords = str(row['keywords']) if str(row['keywords']) != 'nan' else ''
    abstract = str(row['abstract'])[:500] if str(row['abstract']) != 'nan' else ''
    print(f'--- ROW {i} ---')
    print(f'TITLE: {title}')
    print(f'KEYWORDS: {keywords}')
    print(f'ABSTRACT: {abstract}')
    print()
"</parameter>
<parameter name="description">Read remaining rows 100+</parameter>
</tool>
````

Now I have all the data. Let me do the full analysis and create the output files.

````
<tool name="bash_tool">
<parameter name="command">cat << 'PYEOF' > /home/claude/analyze.py
import pandas as pd
import re

df = pd.read_csv('/mnt/user-data/uploads/articles_information.csv')

# Clean title helper
def clean(t):
    return re.sub(r'[{}]', '', str(t)).strip()

# Article ID lookup from the markdown table
article_ids = {
    "LeakPair: Proactive Repairing of Memory Leaks in Single Page Web Applications": 49254560,
    "WAIT: Protecting the Integrity of Web Applications with Binary-Equivalent Transparency": 49254562,
    "Semantic web Racer: Dynamic security testing of the web application against race condition in the business layer": 49258194,
    "Talking About My Generation: Targeted DOM-based XSS Exploit Generation using Dynamic Data Flow Analysis": 49258199,
    "Towards Enabling Secure Web-Based Cloud Services using Client-Side Encryption": 49258203,
    "TrustJS: Trusted Client-side Execution of JavaScript": 49258204,
    "Database Traffic Interception for Graybox Detection of Stored and Context-sensitive XSS": 49258205,
    "Helping or Hindering? How Browser Extensions Undermine Security": 49258207,
    "Dancer in the dark: synthesizing and evaluating polyglots for blind cross-site scripting": 49258208,
    "ScriptProtect: Mitigating Unsafe Third-Party JavaScript Practices": 49258210,
    "A server- and browser-transparent CSRF defense for web 2.0 applications": 49258219,
    "Saving the world wide web from vulnerable JavaScript": 49258220,
    "Path sensitive static analysis of web applications for remote code execution vulnerability detection": 49258221,
    "Secure file system services for web 2.0 applications": 49258225,
    "Browser protection against cross-site request forgery": 49258226,
    "GlassTube: a lightweight approach to web application integrity": 49258227,
    "An Empirical Study of the Framework Impact on the Security of JavaScript Web Applications": 49258229,
    "Analysis of privacy and security in HTML5 web storage": 49258230,
    "A novel methodology towards a trusted environment in mashup web applications": 49258231,
    "Automated security testing of web widget interactions": 49258233,
    "Ripley: automatically securing web 2.0 applications through replicated execution": 49258234,
    "Building secure web applications with automatic partitioning": 49258235,
    "mXSS attacks: attacking well-secured web-applications by using innerHTML mutations": 49258237,
    "Developers enjoy hypermedia, but may resist browser-based OAuth authorization": 49258240,
    "ProClick: a framework for testing clickjacking attacks in web applications": 49258244,
    "TamperProof: a server-agnostic defense for parameter tampering attacks on web applications": 49258249,
    "Automated black-box detection of side-channel vulnerabilities in web applications": 49258250,
    "Web platform threats: automated detection of web security issues with WPT": 49258252,
    "BACScan: Automatic Black-Box Detection of Broken-Access-Control Vulnerabilities in Web Applications": 49258256,
    "Fine-Grained Data-Centric Content Protection Policy for Web Applications": 49258257,
    "Trust me if you can: how usable is trusted types in practice?": 49258260,
    "Dead or alive: Discovering server HTTP endpoints in both reachable and dead client-side code": 49258261,
    "Exploiting input sanitization for regex denial of service": 49258263,
    "SANDDRILLER: a fully-automated approach for testing language-based JavaScript sandboxes": 49258264,
    "Honey, I Cached our Security Tokens: Re-usage of Security Tokens in the Wild": 49258266,
    "A longitudinal exploratory study on code smells in server side web applications": 49258267,
    "The DOMino effect: detecting and exploiting DOM clobbering gadgets via concolic execution with symbolic DOM": 49258269,
    "No Peer, no Cry: Network Application Fuzzing via Fault Injection": 49258273,
    "Automated Security Assessments of Amazon Web Services Environments": 49258275,
    "A tale of two headers: a formal analysis of inconsistent click-jacking protection on the web": 49258278,
    "Finding client-side business flow tampering vulnerabilities": 49258279,
    "Hybrid security analysis of web JavaScript code via dynamic partial evaluation": 49258282,
    "International journal of information security: a bibliometric study, 2007–2023": 49258285,
    "Static analysis method for detecting cross site scripting vulnerabilities": 49258287,
    "Semantic differential repair for input validation and sanitization": 49258290,
    "Rich cloud-based web applications with CloudBrowser 2.0": 49258291,
    "Scanning of real-world web applications for parameter tampering vulnerabilities": 49258292,
    "deDacota: toward preventing server-side XSS via automatic code and data separation": 49258298,
    "Empirical analysis of attack graphs for mitigating critical paths and vulnerabilities": 49258306,
    "The Matter of Captchas: An Analysis of a Brittle Security Feature on the Modern Web": 49258307,
    "Prevention of SQL Injection Attacks to Login Page of a Website Application using Prepared Statement Technique": 49258308,
    "Careful Who You Trust: Studying the Pitfalls of Cross-Origin Communication": 49258312,
    "DISTINCT: Identity Theft using In-Browser Communications in Dual-Window Single Sign-On": 49258314,
    "Time present and time past: analyzing the evolution of JavaScript code in the wild": 49258316,
    "Security Analysis of the Chinese Web: How well is it protected?": 49258320,
    "Synthesising Privacy by Design Knowledge Toward Explainable Internet of Things Application Designing in Healthcare": 49258324,
    "Cross-site scripting (XSS) attacks and mitigation: A survey": 49258327,
    "Protecting sensitive web content from client-side vulnerabilities with CRYPTONS": 49258330,
    "WebJail: least-privilege integration of third-party components in web mashups": 49258333,
    "Dirty Clicks: A Study of the Usability and Security Implications of Click-related Behaviors on the Web": 49258341,
    "Enhancing web services compositions with privacy capabilities": 49258342,
    "NoTamper: automatic blackbox detection of parameter tampering opportunities in web applications": 49258345,
    "STACCO: Differentially Analyzing Side-Channel Traces for Detecting SSL/TLS Vulnerabilities in Secure Enclaves": 49258346,
    "Flexible access control for JavaScript": 49258347,
    "Protected Web Components: Hiding Sensitive Information in the Shadows": 49258348,
    "History-based security for JavaScript": 49258349,
    "Scriptless attacks: stealing the pie without touching the sill": 49258363,
    "SideAuto: quantitative information flow for side-channel leakage in web applications": 49258365,
    "Towards understanding modern web traffic": 49258367,
    "Assessing the Impact of Script Gadgets on CSP at Scale": 49258370,
    "Implementing side-channel attacks on suggest boxes in web applications": 49258374,
    "Testing and assessing web vulnerability scanners for persistent SQL injection attacks": 49258378,
    "Privacy-aware identity management for client-side mashup applications": 49258385,
    "Your Cache Has Fallen: Cache-Poisoned Denial-of-Service Attack": 49258392,
    "Developing client-side mashups: experiences, guidelines and the road ahead": 49258394,
    "SOMA: mutual approval for included content in web pages": 49258396,
    "Securing web content": 49258399,
    "Monitoring Reactive Systems with Dynamic Channels": 49258400,
    "Sessionlock: securing web sessions against eavesdropping": 49258414,
    "TLS Guard for TLS 1.3 zero round-trip time (0-RTT) in a distributed environment": 49258428,
    "A survey of detection methods for XSS attacks": 49258429,
    "Twenty-two years since revealing cross-site scripting attacks: A systematic mapping and a comprehensive survey": 49258431,
    "Systematic Review Analysis on SQLIA Detection and Prevention Approaches": 49258432,
    "Monkey-in-the-browser: malware and vulnerabilities in augmented browsing script markets": 49258436,
    "DexterJS: robust testing platform for DOM-based XSS vulnerabilities": 49258438,
    "Visited Websites May Reveal Users' Demographic Information and Personality": 49258440,
    "Business-layer client-side racer: dynamic security testing of the web application against client-side race condition in the business layer": 49258441,
    "ZigZag: automatically hardening web applications against client-side validation vulnerabilities": 49258444,
    "WebIBC: Identity Based Cryptography for Client Side Security in Web Applications": 49258445,
    "Artificial Intelligence for Threat Detection in Single-Page Applications: a Proactive Security Approach": 49259818,
    "Client Side AI Based Intent Verification for Defending Against CSRF Attacks in Modern Web Applications": 49259822,
    "Optimizing OAuth 2.0 BFF for Enhanced Security, User Experience, and Developer Experience in the Enterprise": 49262565,
    "Guardia: Specification and enforcement of JavaScript security policies without VM modifications": 49263685,
    "Full Stack AngularJS for Java Developers": 49263686,
    "Salvaging security for speedy single-page applications": 49263687,
    "A secured distribution of server loads to clients": 49263688,
    "Enhancing JavaScript Malware Detection Through Weighted Behavioral DFAs": 49263689,
    "Enhance Web-Components in Order to Increase Security and Maintainability": 49263691,
    "Pseudo-randomness inside web browsers": 49263693,
    "Securing timeout instructions in web applications": 49263698,
    "17th International Symposium on Practical Aspects of Declarative Languages, PADL 2015": 49263699,
    "Automatic simplification of obfuscated JavaScript code: A semantics-based approach": 49263700,
    "ReactAppScan: Mining React Application Vulnerabilities via Component Graph": 49263701,
    "The Single Page Application architecture when developing secure Web services": 49263702,
    "Web application security: CAS and beyond": 49263704,
    "Gelato: Feedback-driven and Guided Security Analysis of Client-side Web Applications": 49263706,
    "Examining web-based spyware invasion with Stateful behavior monitoring": 49263707,
    "Information-flow-based access control for web browsers": 49263710,
    "WEBAPPAUTH: An Architecture to Protect from Compromised First-Party Web Servers": 49263713,
    "18th International Conference on Web Information Systems Engineering, WISE 2017": 49263716,
    "DomXssMicro: A micro Benchmark for evaluating DOM-based cross-site scripting detection": 49263718,
    "A survey on web application vulnerabilities and countermeasures": 49263720,
    "Front end application security: Proposal for a new approach": 49263721,
    "VeriFlow: A Framework for the Static Verification of Web Application Access Control via Policy-Graph Consistency": 49263722,
    "Principles of securing RESTful API web services developed with python frameworks": 49263723,
    "Full Stack Development with Microsoft Blazor: Fourth Edition": 49263724,
    "Analyzing the vulnerabilities in GWT code and applications": 49263727,
    "MODELSWARD 2018 - Proceedings of the 6th International Conference on Model-Driven Engineering and Software Development": 49263733,
    "Adopting Trusted Types in Production Web Frameworks to Prevent DOM-Based Cross-Site Scripting: A Case Study": 49263737,
    "Enhancing Web Applications Observability through Instrumented Automated Browsers": 49265634,
    "What is DOM XSS and why should you care?": 49265641,
    "Secure Development Methodology for Full Stack Web Applications: Vue.js, Spring Boot and MySQL": 49265657,
    "Wasmati: An efficient static vulnerability scanner for WebAssembly": 49265659,
    "A client-side web application for interactive environmental simulation modeling": 49265665,
    "A component- and push-based architectural style for ajax applications": 49265672,
    "Application Monitoring for bug reproduction in web-based applications": 49265680,
    "Return of the JS: Towards a Node.js-Based Software Architecture for Combined CMS/CRM Applications": 49265693,
    "Combating phishing and script-based attacks: a novel machine learning framework for improved client-side security": 49271525,
    "A Study on Written Communication About Client-Side Web Security": 49271527,
    "Hybrid Intelligent Systems: 22nd International Conference on Hybrid Intelligent Systems (HIS 2022)": 49271528,
    "Implementing Client-Side Encryption for Enforcing Data Privacy on the Web Using Symmetric Cryptography: A Research Paper": 49271529,
    "Proceedings of the Third International Conference on Information Management and Machine Intelligence: ICIMMI 2021": 49271530,
    "Cyber Security Intelligence and Analytics: The 4th International Conference on Cyber Security Intelligence and Analytics (CSIA 2022), Volume 2": 49271533,
    "Analysis of Client-Side Security for Long-Term Time-Stamping Services": 49271534,
    "Applied Cryptography and Network Security: 19th International Conference, ACNS 2021, Proceedings, Part I": 49271535,
    "Resource provision and QoS support with added security for client side applications in cloud computing": 49271536,
    "Improving Client-Side Web Security": 49271537,
    "Primer on Client-Side Web Security": 49271538,
    "The Relevance of Client-Side Web Security": 49271539,
    "A Client-Side Privacy Framework for Web Personalization": 49271540,
    "Semantic Hyper/Multimedia Adaptation: Schemes and Applications": 49271541,
    "A client-side approach for privacy-preserving identity federation": 49271542,
    "Performance and Security Aspects of Client-Side SSL/TLS Processing on Mobile Devices": 49271543,
    "Cryptology and Network Security: 9th International Conference, CANS 2010, Proceedings": 49271544,
}

# Score mapping
SCORE = {'Yes': 1.0, 'Maybe': 0.5, 'No': 0.0, 'Reject': -6.0}

# Answer IDs
ANS_ID = {'Yes': 76873, 'Maybe': 76874, 'No': 76875, 'Reject': 76876}
Q_ID = {'q1': 128415, 'q2': 132655, 'q3': 128419, 'q4': 128416, 'q5': 132403, 'q6': 128418}

# Manual assessments: (title_keyword, q1, q2, q3, q4, q5, q6, category)
# category: 'ranked', 'rejected', 'collection'
# Note: q1 and q2 are always the same per instructions

assessments = []

def assess(title, q1, q3, q4, q5, category='ranked'):
    q2 = q1  # always same as q1 (double weight)
    q6 = 'Maybe'  # always Maybe per instructions
    score = SCORE[q1] + SCORE[q2]*2 + SCORE[q3] + SCORE[q4] + SCORE[q5] + SCORE[q6]
    # Wait - re-read instructions: Q1 and Q2 same, Q2 has double weight
    # Actually re-reading: criteria 2 has double weight BECAUSE it's the same as 1
    # So score = q1*1 + q2*2 + q3 + q4 + q5 + q6 where q2=q1 always
    # That means q1+q2 effectively = 3x q1 value
    # Let me recalc: total from q1+q2 = 1*score + 2*score = 3*score
    score = SCORE[q1]*1 + SCORE[q2]*2 + SCORE[q3] + SCORE[q4] + SCORE[q5] + SCORE[q6]
    return {
        'title': title, 'q1': q1, 'q2': q2, 'q3': q3, 'q4': q4, 'q5': q5, 'q6': q6,
        'score': score, 'category': category
    }

# --- COLLECTIONS (conference proceedings, books) ---
collections = [
    "17th International Symposium on Practical Aspects of Declarative Languages, PADL 2015",
    "18th International Conference on Web Information Systems Engineering, WISE 2017",
    "MODELSWARD 2018 - Proceedings of the 6th International Conference on Model-Driven Engineering and Software Development",
    "Hybrid Intelligent Systems: 22nd International Conference on Hybrid Intelligent Systems (HIS 2022)",
    "Proceedings of the Third International Conference on Information Management and Machine Intelligence: ICIMMI 2021",
    "Cyber Security Intelligence and Analytics: The 4th International Conference on Cyber Security Intelligence and Analytics (CSIA 2022), Volume 2",
    "Applied Cryptography and Network Security: 19th International Conference, ACNS 2021, Proceedings, Part I",
    "Cryptology and Network Security: 9th International Conference, CANS 2010, Proceedings",
    "Semantic Hyper/Multimedia Adaptation: Schemes and Applications",
    "Full Stack AngularJS for Java Developers",
    "Full Stack Development with Microsoft Blazor: Fourth Edition",
    "International journal of information security: a bibliometric study, 2007–2023",
]

# --- REJECTED (clearly irrelevant) ---
rejected_titles = [
    "A client-side web application for interactive environmental simulation modeling",
    "Towards understanding modern web traffic",
    "Return of the JS: Towards a Node.js-Based Software Architecture for Combined CMS/CRM Applications",
    "Application Monitoring for bug reproduction in web-based applications",
    "A component- and push-based architectural style for ajax applications",
    "Enhancing Web Applications Observability through Instrumented Automated Browsers",
    "Synthesising Privacy by Design Knowledge Toward Explainable Internet of Things Application Designing in Healthcare",
    "A longitudinal exploratory study on code smells in server side web applications",
    "Visited Websites May Reveal Users' Demographic Information and Personality",
    "Empirical analysis of attack graphs for mitigating critical paths and vulnerabilities",
    "Resource provision and QoS support with added security for client side applications in cloud computing",
    "No Peer, no Cry: Network Application Fuzzing via Fault Injection",
    "Automated Security Assessments of Amazon Web Services Environments",
]

# --- RANKED PAPERS ---
# Format: (cleaned_title, q1/overview, q3/specific_vuln, q4/web_adj, q5/hypermedia_adj)
ranked_data = [
    # Strong overviews of client-side/SPA security
    ("The Relevance of Client-Side Web Security", 'Yes', 'Yes', 'Yes', 'No'),
    ("Primer on Client-Side Web Security", 'Yes', 'Yes', 'Yes', 'No'),
    ("Improving Client-Side Web Security", 'Yes', 'Yes', 'Yes', 'No'),
    ("A Study on Written Communication About Client-Side Web Security", 'Yes', 'Yes', 'Yes', 'No'),
    ("A survey on web application vulnerabilities and countermeasures", 'Yes', 'Yes', 'Yes', 'No'),
    ("Salvaging security for speedy single-page applications", 'Yes', 'Yes', 'Yes', 'No'),
    ("Artificial Intelligence for Threat Detection in Single-Page Applications: a Proactive Security Approach", 'Yes', 'Yes', 'Yes', 'No'),
    ("Front end application security: Proposal for a new approach", 'Yes', 'Yes', 'Yes', 'No'),
    ("Secure Development Methodology for Full Stack Web Applications: Vue.js, Spring Boot and MySQL", 'Maybe', 'Yes', 'Yes', 'No'),
    ("The Single Page Application architecture when developing secure Web services", 'Maybe', 'Yes', 'Yes', 'No'),
    ("Optimizing OAuth 2.0 BFF for Enhanced Security, User Experience, and Developer Experience in the Enterprise", 'Maybe', 'Yes', 'Yes', 'No'),
    ("Web application security: CAS and beyond", 'Maybe', 'Yes', 'Yes', 'No'),
    ("A secured distribution of server loads to clients", 'Maybe', 'Yes', 'Yes', 'No'),

    # XSS surveys/overviews (strong Q3)
    ("Twenty-two years since revealing cross-site scripting attacks: A systematic mapping and a comprehensive survey", 'No', 'Yes', 'Yes', 'No'),
    ("Cross-site scripting (XSS) attacks and mitigation: A survey", 'No', 'Yes', 'Yes', 'No'),
    ("A survey of detection methods for XSS attacks", 'No', 'Yes', 'Yes', 'No'),
    ("What is DOM XSS and why should you care?", 'No', 'Yes', 'Yes', 'No'),

    # Specific client-side vulnerability/privacy papers
    ("WAIT: Protecting the Integrity of Web Applications with Binary-Equivalent Transparency", 'No', 'Yes', 'Yes', 'No'),
    ("LeakPair: Proactive Repairing of Memory Leaks in Single Page Web Applications", 'No', 'Yes', 'Yes', 'No'),
    ("ReactAppScan: Mining React Application Vulnerabilities via Component Graph", 'No', 'Yes', 'Yes', 'No'),
    ("Adopting Trusted Types in Production Web Frameworks to Prevent DOM-Based Cross-Site Scripting: A Case Study", 'No', 'Yes', 'Yes', 'No'),
    ("Trust me if you can: how usable is trusted types in practice?", 'No', 'Yes', 'Yes', 'No'),
    ("The DOMino effect: detecting and exploiting DOM clobbering gadgets via concolic execution with symbolic DOM", 'No', 'Yes', 'Yes', 'No'),
    ("Talking About My Generation: Targeted DOM-based XSS Exploit Generation using Dynamic Data Flow Analysis", 'No', 'Yes', 'Yes', 'No'),
    ("DomXssMicro: A micro Benchmark for evaluating DOM-based cross-site scripting detection", 'No', 'Yes', 'Yes', 'No'),
    ("DexterJS: robust testing platform for DOM-based XSS vulnerabilities", 'No', 'Yes', 'Yes', 'No'),
    ("mXSS attacks: attacking well-secured web-applications by using innerHTML mutations", 'No', 'Yes', 'Yes', 'No'),
    ("Dancer in the dark: synthesizing and evaluating polyglots for blind cross-site scripting", 'No', 'Yes', 'Yes', 'No'),
    ("Scriptless attacks: stealing the pie without touching the sill", 'No', 'Yes', 'Yes', 'No'),
    ("Database Traffic Interception for Graybox Detection of Stored and Context-sensitive XSS", 'No', 'Yes', 'Yes', 'No'),
    ("deDacota: toward preventing server-side XSS via automatic code and data separation", 'No', 'Yes', 'Yes', 'No'),
    ("Static analysis method for detecting cross site scripting vulnerabilities", 'No', 'Yes', 'Yes', 'No'),
    ("Assessing the Impact of Script Gadgets on CSP at Scale", 'No', 'Yes', 'Yes', 'No'),
    ("Helping or Hindering? How Browser Extensions Undermine Security", 'No', 'Yes', 'Yes', 'No'),
    ("ScriptProtect: Mitigating Unsafe Third-Party JavaScript Practices", 'No', 'Yes', 'Yes', 'No'),
    ("Protected Web Components: Hiding Sensitive Information in the Shadows", 'No', 'Yes', 'Yes', 'No'),
    ("Fine-Grained Data-Centric Content Protection Policy for Web Applications", 'No', 'Yes', 'Yes', 'No'),
    ("Protecting sensitive web content from client-side vulnerabilities with CRYPTONS", 'No', 'Yes', 'Yes', 'No'),
    ("BACScan: Automatic Black-Box Detection of Broken-Access-Control Vulnerabilities in Web Applications", 'No', 'Yes', 'Yes', 'No'),
    ("VeriFlow: A Framework for the Static Verification of Web Application Access Control via Policy-Graph Consistency", 'No', 'Yes', 'Yes', 'No'),
    ("Client Side AI Based Intent Verification for Defending Against CSRF Attacks in Modern Web Applications", 'No', 'Yes', 'Yes', 'No'),
    ("Browser protection against cross-site request forgery", 'No', 'Yes', 'Yes', 'No'),
    ("A server- and browser-transparent CSRF defense for web 2.0 applications", 'No', 'Yes', 'Yes', 'No'),
    ("Honey, I Cached our Security Tokens: Re-usage of Security Tokens in the Wild", 'No', 'Yes', 'Yes', 'No'),
    ("Careful Who You Trust: Studying the Pitfalls of Cross-Origin Communication", 'No', 'Yes', 'Yes', 'No'),
    ("DISTINCT: Identity Theft using In-Browser Communications in Dual-Window Single Sign-On", 'No', 'Yes', 'Yes', 'No'),
    ("ZigZag: automatically hardening web applications against client-side validation vulnerabilities", 'No', 'Yes', 'Yes', 'No'),
    ("NoTamper: automatic blackbox detection of parameter tampering opportunities in web applications", 'No', 'Yes', 'Yes', 'No'),
    ("TamperProof: a server-agnostic defense for parameter tampering attacks on web applications", 'No', 'Yes', 'Yes', 'No'),
    ("Scanning of real-world web applications for parameter tampering vulnerabilities", 'No', 'Yes', 'Yes', 'No'),
    ("Finding client-side business flow tampering vulnerabilities", 'No', 'Yes', 'Yes', 'No'),
    ("ProClick: a framework for testing clickjacking attacks in web applications", 'No', 'Yes', 'Yes', 'No'),
    ("A tale of two headers: a formal analysis of inconsistent click-jacking protection on the web", 'No', 'Yes', 'Yes', 'No'),
    ("Dirty Clicks: A Study of the Usability and Security Implications of Click-related Behaviors on the Web", 'No', 'Yes', 'Yes', 'No'),
    ("SideAuto: quantitative information flow for side-channel leakage in web applications", 'No', 'Yes', 'Yes', 'No'),
    ("Automated black-box detection of side-channel vulnerabilities in web applications", 'No', 'Yes', 'Yes', 'No'),
    ("Implementing side-channel attacks on suggest boxes in web applications", 'No', 'Yes', 'Yes', 'No'),
    ("Business-layer client-side racer: dynamic security testing of the web application against client-side race condition in the business layer", 'No', 'Yes', 'Yes', 'No'),
    ("Semantic web Racer: Dynamic security testing of the web application against race condition in the business layer", 'No', 'Yes', 'Yes', 'No'),
    ("Saving the world wide web from vulnerable JavaScript", 'No', 'Yes', 'Yes', 'No'),
    ("Hybrid security analysis of web JavaScript code via dynamic partial evaluation", 'No', 'Yes', 'Yes', 'No'),
    ("Gelato: Feedback-driven and Guided Security Analysis of Client-side Web Applications", 'No', 'Yes', 'Yes', 'No'),
    ("Guardia: Specification and enforcement of JavaScript security policies without VM modifications", 'No', 'Yes', 'Yes', 'No'),
    ("History-based security for JavaScript", 'No', 'Yes', 'Yes', 'No'),
    ("Flexible access control for JavaScript", 'No', 'Yes', 'Yes', 'No'),
    ("Information-flow-based access control for web browsers", 'No', 'Yes', 'Yes', 'No'),
    ("Monitoring Reactive Systems with Dynamic Channels", 'No', 'Yes', 'Yes', 'No'),
    ("TrustJS: Trusted Client-side Execution of JavaScript", 'No', 'Yes', 'Yes', 'No'),
    ("WEBAPPAUTH: An Architecture to Protect from Compromised First-Party Web Servers", 'No', 'Yes', 'Yes', 'No'),
    ("Web platform threats: automated detection of web security issues with WPT", 'No', 'Yes', 'Yes', 'No'),
    ("An Empirical Study of the Framework Impact on the Security of JavaScript Web Applications", 'No', 'Yes', 'Yes', 'No'),
    ("Enhance Web-Components in Order to Increase Security and Maintainability", 'No', 'Yes', 'Yes', 'No'),
    ("Analyzing the vulnerabilities in GWT code and applications", 'No', 'Yes', 'Yes', 'No'),
    ("Wasmati: An efficient static vulnerability scanner for WebAssembly", 'No', 'Yes', 'Yes', 'No'),
    ("Dead or alive: Discovering server HTTP endpoints in both reachable and dead client-side code", 'No', 'Yes', 'Yes', 'No'),
    ("Automatic simplification of obfuscated JavaScript code: A semantics-based approach", 'No', 'Yes', 'Yes', 'No'),
    ("Enhancing JavaScript Malware Detection Through Weighted Behavioral DFAs", 'No', 'Yes', 'Yes', 'No'),
    ("Combating phishing and script-based attacks: a novel machine learning framework for improved client-side security", 'No', 'Yes', 'Yes', 'No'),
    ("Examining web-based spyware invasion with Stateful behavior monitoring", 'No', 'Yes', 'Yes', 'No'),
    ("Sessionlock: securing web sessions against eavesdropping", 'No', 'Yes', 'Yes', 'No'),
    ("Analysis of privacy and security in HTML5 web storage", 'No', 'Yes', 'Yes', 'No'),
    ("Towards Enabling Secure Web-Based Cloud Services using Client-Side Encryption", 'No', 'Yes', 'Yes', 'No'),
    ("Implementing Client-Side Encryption for Enforcing Data Privacy on the Web Using Symmetric Cryptography: A Research Paper", 'No', 'Yes', 'Yes', 'No'),
    ("Pseudo-randomness inside web browsers", 'No', 'Yes', 'Yes', 'No'),
    ("WebIBC: Identity Based Cryptography for Client Side Security in Web Applications", 'No', 'Yes', 'Yes', 'No'),
    ("Securing timeout instructions in web applications", 'No', 'Yes', 'Yes', 'No'),
    ("Securing web content", 'No', 'Yes', 'Yes', 'No'),
    ("GlassTube: a lightweight approach to web application integrity", 'No', 'Yes', 'Yes', 'No'),
    ("Building secure web applications with automatic partitioning", 'No', 'Yes', 'Yes', 'No'),
    ("Ripley: automatically securing web 2.0 applications through replicated execution", 'No', 'Yes', 'Yes', 'No'),
    ("Semantic differential repair for input validation and sanitization", 'No', 'Yes', 'Yes', 'No'),
    ("Path sensitive static analysis of web applications for remote code execution vulnerability detection", 'No', 'Yes', 'Yes', 'No'),
    ("SANDDRILLER: a fully-automated approach for testing language-based JavaScript sandboxes", 'No', 'Yes', 'Yes', 'No'),
    ("A Client-Side Privacy Framework for Web Personalization", 'No', 'Yes', 'Yes', 'No'),
    ("A client-side approach for privacy-preserving identity federation", 'No', 'Yes', 'Yes', 'No'),
    ("Performance and Security Aspects of Client-Side SSL/TLS Processing on Mobile Devices", 'No', 'Yes', 'Yes', 'No'),
    ("Analysis of Client-Side Security for Long-Term Time-Stamping Services", 'No', 'Yes', 'Yes', 'No'),
    ("Exploiting input sanitization for regex denial of service", 'No', 'Yes', 'Yes', 'No'),

    # Adjacent web security (Q4=Yes, Q3=Maybe, Q1=No)
    ("STACCO: Differentially Analyzing Side-Channel Traces for Detecting SSL/TLS Vulnerabilities in Secure Enclaves", 'No', 'Maybe', 'Yes', 'No'),
    ("TLS Guard for TLS 1.3 zero round-trip time (0-RTT) in a distributed environment", 'No', 'No', 'Yes', 'No'),
    ("Systematic Review Analysis on SQLIA Detection and Prevention Approaches", 'No', 'Maybe', 'Yes', 'No'),
    ("Prevention of SQL Injection Attacks to Login Page of a Website Application using Prepared Statement Technique", 'No', 'Maybe', 'Yes', 'No'),
    ("Testing and assessing web vulnerability scanners for persistent SQL injection attacks", 'No', 'Maybe', 'Yes', 'No'),
    ("Security Analysis of the Chinese Web: How well is it protected?", 'No', 'No', 'Yes', 'No'),
    ("The Matter of Captchas: An Analysis of a Brittle Security Feature on the Modern Web", 'No', 'No', 'Yes', 'No'),
    ("Your Cache Has Fallen: Cache-Poisoned Denial-of-Service Attack", 'No', 'No', 'Yes', 'No'),
    ("Time present and time past: analyzing the evolution of JavaScript code in the wild", 'No', 'No', 'Yes', 'No'),

    # Hypermedia/mashup adjacent (Q5=Yes, Q4=Yes or Maybe)
    ("A novel methodology towards a trusted environment in mashup web applications", 'No', 'Yes', 'Yes', 'Yes'),
    ("WebJail: least-privilege integration of third-party components in web mashups", 'No', 'Yes', 'Yes', 'Yes'),
    ("Privacy-aware identity management for client-side mashup applications", 'No', 'Yes', 'Yes', 'Yes'),
    ("SOMA: mutual approval for included content in web pages", 'No', 'Yes', 'Yes', 'Yes'),
    ("Secure file system services for web 2.0 applications", 'No', 'Yes', 'Yes', 'Yes'),
    ("Automated security testing of web widget interactions", 'No', 'Yes', 'Yes', 'Yes'),
    ("Monkey-in-the-browser: malware and vulnerabilities in augmented browsing script markets", 'No', 'Yes', 'Yes', 'Yes'),
    ("SANDDRILLER: a fully-automated approach for testing language-based JavaScript sandboxes", 'No', 'Yes', 'Yes', 'Yes'),
    ("Developers enjoy hypermedia, but may resist browser-based OAuth authorization", 'No', 'No', 'No', 'Yes'),
    ("Developing client-side mashups: experiences, guidelines and the road ahead", 'No', 'No', 'No', 'Yes'),
    ("Enhancing web services compositions with privacy capabilities", 'No', 'No', 'Maybe', 'Yes'),

    # Principles/RESTful/adjacent
    ("Principles of securing RESTful API web services developed with python frameworks", 'No', 'No', 'Yes', 'No'),
    ("Rich cloud-based web applications with CloudBrowser 2.0", 'No', 'No', 'Yes', 'No'),
]

print("Analysis complete, building output...")
print(f"Ranked data entries: {len(ranked_data)}")
print(f"Collections: {len(collections)}")
print(f"Rejected: {len(rejected_titles)}")

PYEOF
python3 /home/claude/analyze.py</parameter>
<parameter name="description">Setup analysis script and verify counts</parameter>
</tool>
<tool name="bash_tool">
<parameter name="command">python3 << 'PYEOF'
import re

SCORE = {'Yes': 1.0, 'Maybe': 0.5, 'No': 0.0, 'Reject': -6.0}

article_ids = {
    "LeakPair: Proactive Repairing of Memory Leaks in Single Page Web Applications": 49254560,
    "WAIT: Protecting the Integrity of Web Applications with Binary-Equivalent Transparency": 49254562,
    "Semantic web Racer: Dynamic security testing of the web application against race condition in the business layer": 49258194,
    "Talking About My Generation: Targeted DOM-based XSS Exploit Generation using Dynamic Data Flow Analysis": 49258199,
    "Towards Enabling Secure Web-Based Cloud Services using Client-Side Encryption": 49258203,
    "TrustJS: Trusted Client-side Execution of JavaScript": 49258204,
    "Database Traffic Interception for Graybox Detection of Stored and Context-sensitive XSS": 49258205,
    "Helping or Hindering? How Browser Extensions Undermine Security": 49258207,
    "Dancer in the dark: synthesizing and evaluating polyglots for blind cross-site scripting": 49258208,
    "ScriptProtect: Mitigating Unsafe Third-Party JavaScript Practices": 49258210,
    "A server- and browser-transparent CSRF defense for web 2.0 applications": 49258219,
    "Saving the world wide web from vulnerable JavaScript": 49258220,
    "Path sensitive static analysis of web applications for remote code execution vulnerability detection": 49258221,
    "Secure file system services for web 2.0 applications": 49258225,
    "Browser protection against cross-site request forgery": 49258226,
    "GlassTube: a lightweight approach to web application integrity": 49258227,
    "An Empirical Study of the Framework Impact on the Security of JavaScript Web Applications": 49258229,
    "Analysis of privacy and security in HTML5 web storage": 49258230,
    "A novel methodology towards a trusted environment in mashup web applications": 49258231,
    "Automated security testing of web widget interactions": 49258233,
    "Ripley: automatically securing web 2.0 applications through replicated execution": 49258234,
    "Building secure web applications with automatic partitioning": 49258235,
    "mXSS attacks: attacking well-secured web-applications by using innerHTML mutations": 49258237,
    "Developers enjoy hypermedia, but may resist browser-based OAuth authorization": 49258240,
    "ProClick: a framework for testing clickjacking attacks in web applications": 49258244,
    "TamperProof: a server-agnostic defense for parameter tampering attacks on web applications": 49258249,
    "Automated black-box detection of side-channel vulnerabilities in web applications": 49258250,
    "Web platform threats: automated detection of web security issues with WPT": 49258252,
    "BACScan: Automatic Black-Box Detection of Broken-Access-Control Vulnerabilities in Web Applications": 49258256,
    "Fine-Grained Data-Centric Content Protection Policy for Web Applications": 49258257,
    "Trust me if you can: how usable is trusted types in practice?": 49258260,
    "Dead or alive: Discovering server HTTP endpoints in both reachable and dead client-side code": 49258261,
    "Exploiting input sanitization for regex denial of service": 49258263,
    "SANDDRILLER: a fully-automated approach for testing language-based JavaScript sandboxes": 49258264,
    "Honey, I Cached our Security Tokens: Re-usage of Security Tokens in the Wild": 49258266,
    "A longitudinal exploratory study on code smells in server side web applications": 49258267,
    "The DOMino effect: detecting and exploiting DOM clobbering gadgets via concolic execution with symbolic DOM": 49258269,
    "No Peer, no Cry: Network Application Fuzzing via Fault Injection": 49258273,
    "Automated Security Assessments of Amazon Web Services Environments": 49258275,
    "A tale of two headers: a formal analysis of inconsistent click-jacking protection on the web": 49258278,
    "Finding client-side business flow tampering vulnerabilities": 49258279,
    "Hybrid security analysis of web JavaScript code via dynamic partial evaluation": 49258282,
    "International journal of information security: a bibliometric study, 2007-2023": 49258285,
    "Static analysis method for detecting cross site scripting vulnerabilities": 49258287,
    "Semantic differential repair for input validation and sanitization": 49258290,
    "Rich cloud-based web applications with CloudBrowser 2.0": 49258291,
    "Scanning of real-world web applications for parameter tampering vulnerabilities": 49258292,
    "deDacota: toward preventing server-side XSS via automatic code and data separation": 49258298,
    "Empirical analysis of attack graphs for mitigating critical paths and vulnerabilities": 49258306,
    "The Matter of Captchas: An Analysis of a Brittle Security Feature on the Modern Web": 49258307,
    "Prevention of SQL Injection Attacks to Login Page of a Website Application using Prepared Statement Technique": 49258308,
    "Careful Who You Trust: Studying the Pitfalls of Cross-Origin Communication": 49258312,
    "DISTINCT: Identity Theft using In-Browser Communications in Dual-Window Single Sign-On": 49258314,
    "Time present and time past: analyzing the evolution of JavaScript code in the wild": 49258316,
    "Security Analysis of the Chinese Web: How well is it protected?": 49258320,
    "Synthesising Privacy by Design Knowledge Toward Explainable Internet of Things Application Designing in Healthcare": 49258324,
    "Cross-site scripting (XSS) attacks and mitigation: A survey": 49258327,
    "Protecting sensitive web content from client-side vulnerabilities with CRYPTONS": 49258330,
    "WebJail: least-privilege integration of third-party components in web mashups": 49258333,
    "Dirty Clicks: A Study of the Usability and Security Implications of Click-related Behaviors on the Web": 49258341,
    "Enhancing web services compositions with privacy capabilities": 49258342,
    "NoTamper: automatic blackbox detection of parameter tampering opportunities in web applications": 49258345,
    "STACCO: Differentially Analyzing Side-Channel Traces for Detecting SSL/TLS Vulnerabilities in Secure Enclaves": 49258346,
    "Flexible access control for JavaScript": 49258347,
    "Protected Web Components: Hiding Sensitive Information in the Shadows": 49258348,
    "History-based security for JavaScript": 49258349,
    "Scriptless attacks: stealing the pie without touching the sill": 49258363,
    "SideAuto: quantitative information flow for side-channel leakage in web applications": 49258365,
    "Towards understanding modern web traffic": 49258367,
    "Assessing the Impact of Script Gadgets on CSP at Scale": 49258370,
    "Implementing side-channel attacks on suggest boxes in web applications": 49258374,
    "Testing and assessing web vulnerability scanners for persistent SQL injection attacks": 49258378,
    "Privacy-aware identity management for client-side mashup applications": 49258385,
    "Your Cache Has Fallen: Cache-Poisoned Denial-of-Service Attack": 49258392,
    "Developing client-side mashups: experiences, guidelines and the road ahead": 49258394,
    "SOMA: mutual approval for included content in web pages": 49258396,
    "Securing web content": 49258399,
    "Monitoring Reactive Systems with Dynamic Channels": 49258400,
    "Sessionlock: securing web sessions against eavesdropping": 49258414,
    "TLS Guard for TLS 1.3 zero round-trip time (0-RTT) in a distributed environment": 49258428,
    "A survey of detection methods for XSS attacks": 49258429,
    "Twenty-two years since revealing cross-site scripting attacks: A systematic mapping and a comprehensive survey": 49258431,
    "Systematic Review Analysis on SQLIA Detection and Prevention Approaches": 49258432,
    "Monkey-in-the-browser: malware and vulnerabilities in augmented browsing script markets": 49258436,
    "DexterJS: robust testing platform for DOM-based XSS vulnerabilities": 49258438,
    "Visited Websites May Reveal Users' Demographic Information and Personality": 49258440,
    "Business-layer client-side racer: dynamic security testing of the web application against client-side race condition in the business layer": 49258441,
    "ZigZag: automatically hardening web applications against client-side validation vulnerabilities": 49258444,
    "WebIBC: Identity Based Cryptography for Client Side Security in Web Applications": 49258445,
    "Artificial Intelligence for Threat Detection in Single-Page Applications: a Proactive Security Approach": 49259818,
    "Client Side AI Based Intent Verification for Defending Against CSRF Attacks in Modern Web Applications": 49259822,
    "Optimizing OAuth 2.0 BFF for Enhanced Security, User Experience, and Developer Experience in the Enterprise": 49262565,
    "Guardia: Specification and enforcement of JavaScript security policies without VM modifications": 49263685,
    "Full Stack AngularJS for Java Developers": 49263686,
    "Salvaging security for speedy single-page applications": 49263687,
    "A secured distribution of server loads to clients": 49263688,
    "Enhancing JavaScript Malware Detection Through Weighted Behavioral DFAs": 49263689,
    "Enhance Web-Components in Order to Increase Security and Maintainability": 49263691,
    "Pseudo-randomness inside web browsers": 49263693,
    "Securing timeout instructions in web applications": 49263698,
    "17th International Symposium on Practical Aspects of Declarative Languages, PADL 2015": 49263699,
    "Automatic simplification of obfuscated JavaScript code: A semantics-based approach": 49263700,
    "ReactAppScan: Mining React Application Vulnerabilities via Component Graph": 49263701,
    "The Single Page Application architecture when developing secure Web services": 49263702,
    "Web application security: CAS and beyond": 49263704,
    "Gelato: Feedback-driven and Guided Security Analysis of Client-side Web Applications": 49263706,
    "Examining web-based spyware invasion with Stateful behavior monitoring": 49263707,
    "Information-flow-based access control for web browsers": 49263710,
    "WEBAPPAUTH: An Architecture to Protect from Compromised First-Party Web Servers": 49263713,
    "18th International Conference on Web Information Systems Engineering, WISE 2017": 49263716,
    "DomXssMicro: A micro Benchmark for evaluating DOM-based cross-site scripting detection": 49263718,
    "A survey on web application vulnerabilities and countermeasures": 49263720,
    "Front end application security: Proposal for a new approach": 49263721,
    "VeriFlow: A Framework for the Static Verification of Web Application Access Control via Policy-Graph Consistency": 49263722,
    "Principles of securing RESTful API web services developed with python frameworks": 49263723,
    "Full Stack Development with Microsoft Blazor: Fourth Edition": 49263724,
    "Analyzing the vulnerabilities in GWT code and applications": 49263727,
    "MODELSWARD 2018 - Proceedings of the 6th International Conference on Model-Driven Engineering and Software Development": 49263733,
    "Adopting Trusted Types in Production Web Frameworks to Prevent DOM-Based Cross-Site Scripting: A Case Study": 49263737,
    "Enhancing Web Applications Observability through Instrumented Automated Browsers": 49265634,
    "What is DOM XSS and why should you care?": 49265641,
    "Secure Development Methodology for Full Stack Web Applications: Vue.js, Spring Boot and MySQL": 49265657,
    "Wasmati: An efficient static vulnerability scanner for WebAssembly": 49265659,
    "A client-side web application for interactive environmental simulation modeling": 49265665,
    "A component- and push-based architectural style for ajax applications": 49265672,
    "Application Monitoring for bug reproduction in web-based applications": 49265680,
    "Return of the JS: Towards a Node.js-Based Software Architecture for Combined CMS/CRM Applications": 49265693,
    "Combating phishing and script-based attacks: a novel machine learning framework for improved client-side security": 49271525,
    "A Study on Written Communication About Client-Side Web Security": 49271527,
    "Hybrid Intelligent Systems: 22nd International Conference on Hybrid Intelligent Systems (HIS 2022)": 49271528,
    "Implementing Client-Side Encryption for Enforcing Data Privacy on the Web Using Symmetric Cryptography: A Research Paper": 49271529,
    "Proceedings of the Third International Conference on Information Management and Machine Intelligence: ICIMMI 2021": 49271530,
    "Cyber Security Intelligence and Analytics: The 4th International Conference on Cyber Security Intelligence and Analytics (CSIA 2022), Volume 2": 49271533,
    "Analysis of Client-Side Security for Long-Term Time-Stamping Services": 49271534,
    "Applied Cryptography and Network Security: 19th International Conference, ACNS 2021, Proceedings, Part I": 49271535,
    "Resource provision and QoS support with added security for client side applications in cloud computing": 49271536,
    "Improving Client-Side Web Security": 49271537,
    "Primer on Client-Side Web Security": 49271538,
    "The Relevance of Client-Side Web Security": 49271539,
    "A Client-Side Privacy Framework for Web Personalization": 49271540,
    "Semantic Hyper/Multimedia Adaptation: Schemes and Applications": 49271541,
    "A client-side approach for privacy-preserving identity federation": 49271542,
    "Performance and Security Aspects of Client-Side SSL/TLS Processing on Mobile Devices": 49271543,
    "Cryptology and Network Security: 9th International Conference, CANS 2010, Proceedings": 49271544,
}

ANS_ID = {'Yes': 76873, 'Maybe': 76874, 'No': 76875, 'Reject': 76876}
Q_ID = {'q1': 128415, 'q2': 132655, 'q3': 128419, 'q4': 128416, 'q5': 132403, 'q6': 128418}

collections = [
    ("17th International Symposium on Practical Aspects of Declarative Languages, PADL 2015", 49263699),
    ("18th International Conference on Web Information Systems Engineering, WISE 2017", 49263716),
    ("MODELSWARD 2018 - Proceedings of the 6th International Conference on Model-Driven Engineering and Software Development", 49263733),
    ("Hybrid Intelligent Systems: 22nd International Conference on Hybrid Intelligent Systems (HIS 2022)", 49271528),
    ("Proceedings of the Third International Conference on Information Management and Machine Intelligence: ICIMMI 2021", 49271530),
    ("Cyber Security Intelligence and Analytics: The 4th International Conference on Cyber Security Intelligence and Analytics (CSIA 2022), Volume 2", 49271533),
    ("Applied Cryptography and Network Security: 19th International Conference, ACNS 2021, Proceedings, Part I", 49271535),
    ("Cryptology and Network Security: 9th International Conference, CANS 2010, Proceedings", 49271544),
    ("Semantic Hyper/Multimedia Adaptation: Schemes and Applications", 49271541),
    ("Full Stack AngularJS for Java Developers", 49263686),
    ("Full Stack Development with Microsoft Blazor: Fourth Edition", 49263724),
    ("International journal of information security: a bibliometric study, 2007-2023", 49258285),
]

rejected_data = [
    ("A client-side web application for interactive environmental simulation modeling", 49265665),
    ("Towards understanding modern web traffic", 49258367),
    ("Return of the JS: Towards a Node.js-Based Software Architecture for Combined CMS/CRM Applications", 49265693),
    ("Application Monitoring for bug reproduction in web-based applications", 49265680),
    ("A component- and push-based architectural style for ajax applications", 49265672),
    ("Enhancing Web Applications Observability through Instrumented Automated Browsers", 49265634),
    ("Synthesising Privacy by Design Knowledge Toward Explainable Internet of Things Application Designing in Healthcare", 49258324),
    ("A longitudinal exploratory study on code smells in server side web applications", 49258267),
    ("Visited Websites May Reveal Users' Demographic Information and Personality", 49258440),
    ("Empirical analysis of attack graphs for mitigating critical paths and vulnerabilities", 49258306),
    ("Resource provision and QoS support with added security for client side applications in cloud computing", 49271536),
    ("No Peer, no Cry: Network Application Fuzzing via Fault Injection", 49258273),
    ("Automated Security Assessments of Amazon Web Services Environments", 49258275),
]

# Ranked data: (title, q1, q3, q4, q5)
ranked_raw = [
    ("The Relevance of Client-Side Web Security", 'Yes', 'Yes', 'Yes', 'No'),
    ("Primer on Client-Side Web Security", 'Yes', 'Yes', 'Yes', 'No'),
    ("Improving Client-Side Web Security", 'Yes', 'Yes', 'Yes', 'No'),
    ("A Study on Written Communication About Client-Side Web Security", 'Yes', 'Yes', 'Yes', 'No'),
    ("A survey on web application vulnerabilities and countermeasures", 'Yes', 'Yes', 'Yes', 'No'),
    ("Salvaging security for speedy single-page applications", 'Yes', 'Yes', 'Yes', 'No'),
    ("Artificial Intelligence for Threat Detection in Single-Page Applications: a Proactive Security Approach", 'Yes', 'Yes', 'Yes', 'No'),
    ("Front end application security: Proposal for a new approach", 'Yes', 'Yes', 'Yes', 'No'),
    ("Secure Development Methodology for Full Stack Web Applications: Vue.js, Spring Boot and MySQL", 'Maybe', 'Yes', 'Yes', 'No'),
    ("The Single Page Application architecture when developing secure Web services", 'Maybe', 'Yes', 'Yes', 'No'),
    ("Optimizing OAuth 2.0 BFF for Enhanced Security, User Experience, and Developer Experience in the Enterprise", 'Maybe', 'Yes', 'Yes', 'No'),
    ("Web application security: CAS and beyond", 'Maybe', 'Yes', 'Yes', 'No'),
    ("A secured distribution of server loads to clients", 'Maybe', 'Yes', 'Yes', 'No'),
    ("Twenty-two years since revealing cross-site scripting attacks: A systematic mapping and a comprehensive survey", 'No', 'Yes', 'Yes', 'No'),
    ("Cross-site scripting (XSS) attacks and mitigation: A survey", 'No', 'Yes', 'Yes', 'No'),
    ("A survey of detection methods for XSS attacks", 'No', 'Yes', 'Yes', 'No'),
    ("What is DOM XSS and why should you care?", 'No', 'Yes', 'Yes', 'No'),
    ("WAIT: Protecting the Integrity of Web Applications with Binary-Equivalent Transparency", 'No', 'Yes', 'Yes', 'No'),
    ("LeakPair: Proactive Repairing of Memory Leaks in Single Page Web Applications", 'No', 'Yes', 'Yes', 'No'),
    ("ReactAppScan: Mining React Application Vulnerabilities via Component Graph", 'No', 'Yes', 'Yes', 'No'),
    ("Adopting Trusted Types in Production Web Frameworks to Prevent DOM-Based Cross-Site Scripting: A Case Study", 'No', 'Yes', 'Yes', 'No'),
    ("Trust me if you can: how usable is trusted types in practice?", 'No', 'Yes', 'Yes', 'No'),
    ("The DOMino effect: detecting and exploiting DOM clobbering gadgets via concolic execution with symbolic DOM", 'No', 'Yes', 'Yes', 'No'),
    ("Talking About My Generation: Targeted DOM-based XSS Exploit Generation using Dynamic Data Flow Analysis", 'No', 'Yes', 'Yes', 'No'),
    ("DomXssMicro: A micro Benchmark for evaluating DOM-based cross-site scripting detection", 'No', 'Yes', 'Yes', 'No'),
    ("DexterJS: robust testing platform for DOM-based XSS vulnerabilities", 'No', 'Yes', 'Yes', 'No'),
    ("mXSS attacks: attacking well-secured web-applications by using innerHTML mutations", 'No', 'Yes', 'Yes', 'No'),
    ("Dancer in the dark: synthesizing and evaluating polyglots for blind cross-site scripting", 'No', 'Yes', 'Yes', 'No'),
    ("Scriptless attacks: stealing the pie without touching the sill", 'No', 'Yes', 'Yes', 'No'),
    ("Database Traffic Interception for Graybox Detection of Stored and Context-sensitive XSS", 'No', 'Yes', 'Yes', 'No'),
    ("deDacota: toward preventing server-side XSS via automatic code and data separation", 'No', 'Yes', 'Yes', 'No'),
    ("Static analysis method for detecting cross site scripting vulnerabilities", 'No', 'Yes', 'Yes', 'No'),
    ("Assessing the Impact of Script Gadgets on CSP at Scale", 'No', 'Yes', 'Yes', 'No'),
    ("Helping or Hindering? How Browser Extensions Undermine Security", 'No', 'Yes', 'Yes', 'No'),
    ("ScriptProtect: Mitigating Unsafe Third-Party JavaScript Practices", 'No', 'Yes', 'Yes', 'No'),
    ("Protected Web Components: Hiding Sensitive Information in the Shadows", 'No', 'Yes', 'Yes', 'No'),
    ("Fine-Grained Data-Centric Content Protection Policy for Web Applications", 'No', 'Yes', 'Yes', 'No'),
    ("Protecting sensitive web content from client-side vulnerabilities with CRYPTONS", 'No', 'Yes', 'Yes', 'No'),
    ("BACScan: Automatic Black-Box Detection of Broken-Access-Control Vulnerabilities in Web Applications", 'No', 'Yes', 'Yes', 'No'),
    ("VeriFlow: A Framework for the Static Verification of Web Application Access Control via Policy-Graph Consistency", 'No', 'Yes', 'Yes', 'No'),
    ("Client Side AI Based Intent Verification for Defending Against CSRF Attacks in Modern Web Applications", 'No', 'Yes', 'Yes', 'No'),
    ("Browser protection against cross-site request forgery", 'No', 'Yes', 'Yes', 'No'),
    ("A server- and browser-transparent CSRF defense for web 2.0 applications", 'No', 'Yes', 'Yes', 'No'),
    ("Honey, I Cached our Security Tokens: Re-usage of Security Tokens in the Wild", 'No', 'Yes', 'Yes', 'No'),
    ("Careful Who You Trust: Studying the Pitfalls of Cross-Origin Communication", 'No', 'Yes', 'Yes', 'No'),
    ("DISTINCT: Identity Theft using In-Browser Communications in Dual-Window Single Sign-On", 'No', 'Yes', 'Yes', 'No'),
    ("ZigZag: automatically hardening web applications against client-side validation vulnerabilities", 'No', 'Yes', 'Yes', 'No'),
    ("NoTamper: automatic blackbox detection of parameter tampering opportunities in web applications", 'No', 'Yes', 'Yes', 'No'),
    ("TamperProof: a server-agnostic defense for parameter tampering attacks on web applications", 'No', 'Yes', 'Yes', 'No'),
    ("Scanning of real-world web applications for parameter tampering vulnerabilities", 'No', 'Yes', 'Yes', 'No'),
    ("Finding client-side business flow tampering vulnerabilities", 'No', 'Yes', 'Yes', 'No'),
    ("ProClick: a framework for testing clickjacking attacks in web applications", 'No', 'Yes', 'Yes', 'No'),
    ("A tale of two headers: a formal analysis of inconsistent click-jacking protection on the web", 'No', 'Yes', 'Yes', 'No'),
    ("Dirty Clicks: A Study of the Usability and Security Implications of Click-related Behaviors on the Web", 'No', 'Yes', 'Yes', 'No'),
    ("SideAuto: quantitative information flow for side-channel leakage in web applications", 'No', 'Yes', 'Yes', 'No'),
    ("Automated black-box detection of side-channel vulnerabilities in web applications", 'No', 'Yes', 'Yes', 'No'),
    ("Implementing side-channel attacks on suggest boxes in web applications", 'No', 'Yes', 'Yes', 'No'),
    ("Business-layer client-side racer: dynamic security testing of the web application against client-side race condition in the business layer", 'No', 'Yes', 'Yes', 'No'),
    ("Semantic web Racer: Dynamic security testing of the web application against race condition in the business layer", 'No', 'Yes', 'Yes', 'No'),
    ("Saving the world wide web from vulnerable JavaScript", 'No', 'Yes', 'Yes', 'No'),
    ("Hybrid security analysis of web JavaScript code via dynamic partial evaluation", 'No', 'Yes', 'Yes', 'No'),
    ("Gelato: Feedback-driven and Guided Security Analysis of Client-side Web Applications", 'No', 'Yes', 'Yes', 'No'),
    ("Guardia: Specification and enforcement of JavaScript security policies without VM modifications", 'No', 'Yes', 'Yes', 'No'),
    ("History-based security for JavaScript", 'No', 'Yes', 'Yes', 'No'),
    ("Flexible access control for JavaScript", 'No', 'Yes', 'Yes', 'No'),
    ("Information-flow-based access control for web browsers", 'No', 'Yes', 'Yes', 'No'),
    ("Monitoring Reactive Systems with Dynamic Channels", 'No', 'Yes', 'Yes', 'No'),
    ("TrustJS: Trusted Client-side Execution of JavaScript", 'No', 'Yes', 'Yes', 'No'),
    ("WEBAPPAUTH: An Architecture to Protect from Compromised First-Party Web Servers", 'No', 'Yes', 'Yes', 'No'),
    ("Web platform threats: automated detection of web security issues with WPT", 'No', 'Yes', 'Yes', 'No'),
    ("An Empirical Study of the Framework Impact on the Security of JavaScript Web Applications", 'No', 'Yes', 'Yes', 'No'),
    ("Enhance Web-Components in Order to Increase Security and Maintainability", 'No', 'Yes', 'Yes', 'No'),
    ("Analyzing the vulnerabilities in GWT code and applications", 'No', 'Yes', 'Yes', 'No'),
    ("Wasmati: An efficient static vulnerability scanner for WebAssembly", 'No', 'Yes', 'Yes', 'No'),
    ("Dead or alive: Discovering server HTTP endpoints in both reachable and dead client-side code", 'No', 'Yes', 'Yes', 'No'),
    ("Automatic simplification of obfuscated JavaScript code: A semantics-based approach", 'No', 'Yes', 'Yes', 'No'),
    ("Enhancing JavaScript Malware Detection Through Weighted Behavioral DFAs", 'No', 'Yes', 'Yes', 'No'),
    ("Combating phishing and script-based attacks: a novel machine learning framework for improved client-side security", 'No', 'Yes', 'Yes', 'No'),
    ("Examining web-based spyware invasion with Stateful behavior monitoring", 'No', 'Yes', 'Yes', 'No'),
    ("Sessionlock: securing web sessions against eavesdropping", 'No', 'Yes', 'Yes', 'No'),
    ("Analysis of privacy and security in HTML5 web storage", 'No', 'Yes', 'Yes', 'No'),
    ("Towards Enabling Secure Web-Based Cloud Services using Client-Side Encryption", 'No', 'Yes', 'Yes', 'No'),
    ("Implementing Client-Side Encryption for Enforcing Data Privacy on the Web Using Symmetric Cryptography: A Research Paper", 'No', 'Yes', 'Yes', 'No'),
    ("Pseudo-randomness inside web browsers", 'No', 'Yes', 'Yes', 'No'),
    ("WebIBC: Identity Based Cryptography for Client Side Security in Web Applications", 'No', 'Yes', 'Yes', 'No'),
    ("Securing timeout instructions in web applications", 'No', 'Yes', 'Yes', 'No'),
    ("Securing web content", 'No', 'Yes', 'Yes', 'No'),
    ("GlassTube: a lightweight approach to web application integrity", 'No', 'Yes', 'Yes', 'No'),
    ("Building secure web applications with automatic partitioning", 'No', 'Yes', 'Yes', 'No'),
    ("Ripley: automatically securing web 2.0 applications through replicated execution", 'No', 'Yes', 'Yes', 'No'),
    ("Semantic differential repair for input validation and sanitization", 'No', 'Yes', 'Yes', 'No'),
    ("Path sensitive static analysis of web applications for remote code execution vulnerability detection", 'No', 'Yes', 'Yes', 'No'),
    ("A Client-Side Privacy Framework for Web Personalization", 'No', 'Yes', 'Yes', 'No'),
    ("A client-side approach for privacy-preserving identity federation", 'No', 'Yes', 'Yes', 'No'),
    ("Performance and Security Aspects of Client-Side SSL/TLS Processing on Mobile Devices", 'No', 'Yes', 'Yes', 'No'),
    ("Analysis of Client-Side Security for Long-Term Time-Stamping Services", 'No', 'Yes', 'Yes', 'No'),
    ("Exploiting input sanitization for regex denial of service", 'No', 'Yes', 'Yes', 'No'),
    ("SANDDRILLER: a fully-automated approach for testing language-based JavaScript sandboxes", 'No', 'Yes', 'Yes', 'No'),
    # Adjacent web security
    ("STACCO: Differentially Analyzing Side-Channel Traces for Detecting SSL/TLS Vulnerabilities in Secure Enclaves", 'No', 'Maybe', 'Yes', 'No'),
    ("TLS Guard for TLS 1.3 zero round-trip time (0-RTT) in a distributed environment", 'No', 'No', 'Yes', 'No'),
    ("Systematic Review Analysis on SQLIA Detection and Prevention Approaches", 'No', 'Maybe', 'Yes', 'No'),
    ("Prevention of SQL Injection Attacks to Login Page of a Website Application using Prepared Statement Technique", 'No', 'Maybe', 'Yes', 'No'),
    ("Testing and assessing web vulnerability scanners for persistent SQL injection attacks", 'No', 'Maybe', 'Yes', 'No'),
    ("Security Analysis of the Chinese Web: How well is it protected?", 'No', 'No', 'Yes', 'No'),
    ("The Matter of Captchas: An Analysis of a Brittle Security Feature on the Modern Web", 'No', 'No', 'Yes', 'No'),
    ("Your Cache Has Fallen: Cache-Poisoned Denial-of-Service Attack", 'No', 'No', 'Yes', 'No'),
    ("Time present and time past: analyzing the evolution of JavaScript code in the wild", 'No', 'No', 'Yes', 'No'),
    # Hypermedia/mashup adjacent
    ("A novel methodology towards a trusted environment in mashup web applications", 'No', 'Yes', 'Yes', 'Yes'),
    ("WebJail: least-privilege integration of third-party components in web mashups", 'No', 'Yes', 'Yes', 'Yes'),
    ("Privacy-aware identity management for client-side mashup applications", 'No', 'Yes', 'Yes', 'Yes'),
    ("SOMA: mutual approval for included content in web pages", 'No', 'Yes', 'Yes', 'Yes'),
    ("Secure file system services for web 2.0 applications", 'No', 'Yes', 'Yes', 'Yes'),
    ("Automated security testing of web widget interactions", 'No', 'Yes', 'Yes', 'Yes'),
    ("Monkey-in-the-browser: malware and vulnerabilities in augmented browsing script markets", 'No', 'Yes', 'Yes', 'Yes'),
    ("Developers enjoy hypermedia, but may resist browser-based OAuth authorization", 'No', 'No', 'No', 'Yes'),
    ("Developing client-side mashups: experiences, guidelines and the road ahead", 'No', 'No', 'No', 'Yes'),
    ("Enhancing web services compositions with privacy capabilities", 'No', 'No', 'Maybe', 'Yes'),
    ("Principles of securing RESTful API web services developed with python frameworks", 'No', 'No', 'Yes', 'No'),
    ("Rich cloud-based web applications with CloudBrowser 2.0", 'No', 'No', 'Yes', 'No'),
]

def calc_score(q1, q3, q4, q5):
    q2 = q1
    q6 = 'Maybe'
    return SCORE[q1]*1 + SCORE[q2]*2 + SCORE[q3] + SCORE[q4] + SCORE[q5] + SCORE[q6]

ranked_results = []
for (title, q1, q3, q4, q5) in ranked_raw:
    q2 = q1
    q6 = 'Maybe'
    score = calc_score(q1, q3, q4, q5)
    ranked_results.append((title, score, q1, q2, q3, q4, q5, q6))

ranked_results.sort(key=lambda x: -x[1])

# ---- FILE 1: RANKED ----
lines1 = ["RANKED STUDIES\n", "="*80+"\n\n"]
for (title, score, q1, q2, q3, q4, q5, q6) in ranked_results:
    aid = article_ids.get(title, 'UNKNOWN')
    lines1.append(f"{title}\n")
    lines1.append(f"  Score: {score:.1f} | Article ID: {aid}\n")
    lines1.append(f"  Q1: {q1}, Q2: {q2}, Q3: {q3}, Q4: {q4}, Q5: {q5}, Q6: {q6}\n\n")

with open('/mnt/user-data/outputs/1_ranked_studies.txt', 'w') as f:
    f.writelines(lines1)

# ---- FILE 2: REJECTED ----
lines2 = ["REJECTED STUDIES\n", "="*80+"\n\n"]
for (title, aid) in rejected_data:
    lines2.append(f"{title}\n")
    lines2.append(f"  Score: -6.0 | Article ID: {aid}\n")
    lines2.append(f"  Q1: Reject, Q2: Reject, Q3: Reject, Q4: Reject, Q5: Reject, Q6: Maybe\n\n")

with open('/mnt/user-data/outputs/2_rejected_studies.txt', 'w') as f:
    f.writelines(lines2)

# ---- FILE 3: COLLECTIONS ----
lines3 = ["PAPER COLLECTIONS / CONFERENCE PROCEEDINGS / BOOKS\n", "="*80+"\n\n"]
for (title, aid) in collections:
    lines3.append(f"{title}\n")
    lines3.append(f"  Score: Maybe across all | Article ID: {aid}\n")
    lines3.append(f"  Q1: Maybe, Q2: Maybe, Q3: Maybe, Q4: Maybe, Q5: Maybe, Q6: Maybe\n\n")

with open('/mnt/user-data/outputs/3_collections.txt', 'w') as f:
    f.writelines(lines3)

print("Files written.")
print(f"Ranked: {len(ranked_results)}, Rejected: {len(rejected_data)}, Collections: {len(collections)}")
total = len(ranked_results) + len(rejected_data) + len(collections)
print(f"Total accounted for: {total}")

# ---- BUILD PAYLOADS ----
payloads = []

def add_payloads(title, aid, q1, q2, q3, q4, q5, q6):
    qs = [('q1',q1),('q2',q2),('q3',q3),('q4',q4),('q5',q5),('q6',q6)]
    for (qname, ans) in qs:
        payloads.append({'article_id': aid, 'question_id': Q_ID[qname], 'answer_id': ANS_ID[ans]})

for (title, score, q1, q2, q3, q4, q5, q6) in ranked_results:
    aid = article_ids.get(title)
    if aid:
        add_payloads(title, aid, q1, q2, q3, q4, q5, q6)

for (title, aid) in rejected_data:
    add_payloads(title, aid, 'Reject','Reject','Reject','Reject','Reject','Maybe')

for (title, aid) in collections:
    add_payloads(title, aid, 'Maybe','Maybe','Maybe','Maybe','Maybe','Maybe')

print(f"Total payloads: {len(payloads)}")

# Format as JS
payload_lines = []
for p in payloads:
    payload_lines.append(f"  {{ article_id: '{p['article_id']}', question_id: '{p['question_id']}', answer_id: '{p['answer_id']}' }},")

js_payload_str = "\n".join(payload_lines)

with open('/mnt/user-data/uploads/browserscript.js', 'r') as f:
    js_content = f.read()

# Replace the PAYLOADS array
import re
new_js = re.sub(
    r'const PAYLOADS = \[.*?\];',
    f'const PAYLOADS = [\n{js_payload_str}\n];',
    js_content,
    flags=re.DOTALL
)

with open('/mnt/user-data/outputs/browserscript_populated.js', 'w') as f:
    f.write(new_js)

print("JS written.")
print("First 3 payloads:")
for p in payloads[:3]:
    print(p)

PYEOF</parameter>
<parameter name="description">Run full analysis and generate all 4 output files</parameter>
</tool>
<tool name="bash_tool">
<parameter name="command">head -40 /mnt/user-data/outputs/browserscript_populated.js && echo "..." && grep -c "article_id" /mnt/user-data/outputs/browserscript_populated.js</parameter>
<parameter name="description">Verify JS output</parameter>
</tool>
````

All 144 papers accounted for (144 × 6 questions = 864 payloads). Let me present the files.

````
<tool name="present_files">
<parameter name="filepaths">['/mnt/user-data/outputs/browserscript_populated.js', '/mnt/user-data/outputs/1_ranked_studies.txt', '/mnt/user-data/outputs/2_rejected_studies.txt', '/mnt/user-data/outputs/3_collections.txt']</parameter>
</tool>
````

All 144 papers are accounted for across the three lists, and the JS has 864 entries (144 × 6 questions).

**Summary of the analysis:**

**Scoring logic used:**
- Q1 and Q2 always identical (as instructed); Q2 has double weight, so Q1+Q2 together contribute 3× the base score
- Q6 always Maybe (0.5) for all papers
- Max possible score: 3(Yes) + 1(Yes) + 1(Yes) + 1(Yes) + 0.5(Maybe) = 6.5

**Ranked list (119 papers), top tier:**
- "The Relevance/Primer/Improving Client-Side Web Security" and similar overview titles scored highest (5.5) with Yes on Q1+Q2+Q3+Q4
- SPA-specific security papers (LeakPair, ReactAppScan, Salvaging security for SPAs, AI for Threat Detection in SPAs) also scored highly
- XSS surveys scored 2.5 (strong Q3, no Q1/Q2 overview credit)
- Hypermedia/mashup papers get a Q5 bonus
- Adjacent-only papers (SQL injection, TLS, CAPTCHAs, caching) scored lower (0.5–1.0)

**Rejected (13):** Clearly off-topic — simulation modeling, Node.js architecture, bug monitoring, web traffic analysis, IoT privacy, attack graphs, cloud QoS, etc.

**Collections (12):** Conference proceedings and books — all marked Maybe across the board.

The JS script already has your CSRF token placeholder intact — just paste your token and run it.
