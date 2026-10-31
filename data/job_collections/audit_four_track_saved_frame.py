import csv, json, re, html
from pathlib import Path
from collections import Counter

ROOT = Path(__file__).resolve().parents[3] if False else Path.cwd()
BASE = ROOT / 'data/job_collections'
CORE = BASE / 'jobstreet-2026-10-recovered-reconciliation-raw-v2'
PILOT = BASE / 'jobstreet-2026-10-six-query-pilot-20261023'
BF = BASE / 'blackfalcon-data-engineer-paginated-20261023'
OUT = BASE / 'jobstreet-2026-10-four-track-offline-audit-20261024'
OUT.mkdir(exist_ok=True)

def read_jsonl(path):
    with path.open(encoding='utf-8-sig') as f:
        return [json.loads(line) for line in f if line.strip()]

def clean(s):
    s = html.unescape(s or '')
    s = re.sub(r'<(?:br\s*/?|/(?:p|li|h[1-6]|div|section|tr))\s*>', '. ', s, flags=re.I)
    s = re.sub(r'<[^>]+>', ' ', s)
    return re.sub(r'[ \t\r\n]+', ' ', s).strip()

rows = {}
# Base 438: use the saved source pointer index, then read each original raw JSON payload.
review_path = BASE/'jobstreet-2026-10-recovered-reconciliation-v1/admission-audit-v2-review/posting_case_review.csv'
with review_path.open(encoding='utf-8-sig', newline='') as f:
    for x in csv.DictReader(f):
        rel = x['source_raw_file']
        raw_path = CORE / rel
        raw = json.loads(raw_path.read_text(encoding='utf-8-sig'))
        rows[x['source_id']] = (raw, f'{CORE.name}/{rel}', x['source_raw_sha256'])
core_ids = {json.loads(line)['source_id'] for line in (CORE/'postings.jsonl').read_text(encoding='utf-8').splitlines() if line.strip()}
if len(core_ids) != 438 or core_ids != set(rows):
    raise RuntimeError('Core review raw pointers do not match the 438-ID raw-v2 frame')
# 29 additions: use the source-audit raw pointers and read the raw payloads.
pilot_registry_ids = {x['source_id'] for x in read_jsonl(PILOT/'comparison_registry_2026-10-23.jsonl')}
if len(pilot_registry_ids) != 467 or not core_ids.issubset(pilot_registry_ids):
    raise RuntimeError('Six-query comparison registry does not reconcile to 467 IDs over the raw-v2 frame')
pilot_add_ids = set()
with (PILOT/'new_id_yield_audit_2026-10-23.csv').open(encoding='utf-8-sig', newline='') as f:
    for x in csv.DictReader(f):
        if x['source_id'] in rows: continue
        pilot_add_ids.add(x['source_id'])
        raw_path = PILOT / x['raw_file']
        raw = json.loads(raw_path.read_text(encoding='utf-8-sig'))
        rows[x['source_id']] = (raw, f'{PILOT.name}/{x["raw_file"]}', x['raw_hash'])
if pilot_add_ids != pilot_registry_ids-core_ids or len(pilot_add_ids) != 29:
    raise RuntimeError('The 29 six-query new-ID raw pointers do not reconcile to the comparison registry')
# 16 additions: follow the saved Blackfalcon version index to original raw payloads.
bf_versions = {}
for v in read_jsonl(BF/'versions.jsonl'):
    bf_versions.setdefault(str(v['fields'].get('id','')), []).append(v)
with (BASE/'blackfalcon-data-engineer-paginated-20261023-reconciliation-v2/cases.csv').open(encoding='utf-8-sig', newline='') as f:
    bf_case_ids=set()
    for x in csv.DictReader(f):
        sid = x['source_id']
        bf_case_ids.add(sid)
        if sid in rows: continue
        versions = bf_versions.get(sid, [])
        if not versions: raise RuntimeError(f'No Blackfalcon raw version for {sid}')
        v = max(versions, key=lambda z: z.get('fields',{}).get('scrapedAt',''))
        rel = v['raw_file']
        raw_path = BF/rel
        raw = json.loads(raw_path.read_text(encoding='utf-8-sig'))
        rows[sid] = (raw, f'{BF.name}/{rel}', v.get('raw_hash',''))
if len(bf_case_ids) != 16 or bf_case_ids & pilot_registry_ids or len(core_ids|pilot_add_ids|bf_case_ids) != 483:
    raise RuntimeError('Blackfalcon new-ID cases do not reconcile to a disjoint 483-ID union')

TECH = re.compile(r'(?<!\w)(?:C\+\+|C#)(?!\w)|\b(SQL|Python|JavaScript|TypeScript|Java|PHP|Ruby|Go|Rust|Kotlin|Swift|R (?:programming|language)|HTML|CSS|React|Angular|Vue|Node(?:\.js)?|\.NET|ASP\.NET|Django|Flask|Laravel|Spring|Unity|Unreal|Godot|Cisco|TCP/IP|DNS|DHCP|LAN|WAN|router|switch|firewall|Fortinet|Palo Alto|Linux|Windows Server|Active Directory|VMware|Kubernetes|Docker|AWS|Azure|GCP|Power BI|Tableau|Looker|ETL|ELT|data warehouse|machine learning|deep learning|LLM|NLP|computer vision|AI (?:application|agent|model|tool)|artificial intelligence|generative AI|API|database|PostgreSQL|MySQL|Oracle|MongoDB|Selenium|Playwright|Jira|test cases?|bug reports?|manual test(?:ing)?|automated test(?:ing)?|software test(?:ing)?|CAD|3D modeling|Blender|Maya|SAP|ABAP|Salesforce|ServiceNow|Power Apps|Power Automate|Figma|Adobe|AutoCAD|ERP|RPA|Qlik|Informatica|Snowflake|Databricks|Spark|Hadoop|Keras|PyTorch|TensorFlow|scikit-learn|OpenCV|GraphQL|REST|Git|CI/CD|Terraform|Ansible|Prometheus|Grafana|SIEM|Splunk|CCTV|VoIP|telephony|game mechanics?|game systems|core loops?|level design|game prototyping|game balancing|gameplay mechanics|test plans?)\b', re.I)
ACTION = re.compile(r'\b(develop|design|build|implement|maintain|test|configure|administer|monitor|troubleshoot|analy[sz]e|program|code|write|deploy|integrat|automat|model|train|secure|manage|create|operate|support|validate|document|debug|perform|execute|prepar|report|detect|identify)\w*\b', re.I)
REQ = re.compile(r'\b(requirements?|qualifications?|responsibilities|experience|proficient|proficiency|knowledge|skills?|must have|you will|responsible for|hands[- ]on|ability to|familiarity|technical)\b', re.I)

IS_TITLE = re.compile(r'\b(ai|artificial intelligence|machine learning|ml|data (?:analyst|scientist|engineer)|analytics engineer|business intelligence|bi developer|computer vision|nlp)\b', re.I)
NT_TITLE = re.compile(r'\b(network|noc|soc|systems? administrator|system administrator|cyber ?security|infrastructure|cloud engineer|network operations)\b', re.I)
WD_TITLE = re.compile(r'\b(web\s+(?:developer|engineer|programmer|application)|front[- ]?end|back[- ]?end|full[- ]?stack|application developer|software developer|software engineer|programmer|mobile developer)\b', re.I)
GAME_TITLE = re.compile(r'\b(game|gameplay|gaming)\b', re.I)
CORE_TITLE = re.compile(r'\b(software|programmer|developer|programming|quality assurance|\bqa\b|tester|database|it support|technical support|systems? analyst|application|automation)\b', re.I)
IS_BODY = re.compile(r'\b(artificial intelligence|\bai\b|machine learning|\bml\b|data analys|data engineer|data scien|analytics|business intelligence|power bi|tableau|look(er|ml)|etl|elt|data warehouse|data pipeline|statistical|predictive model|computer vision|nlp|large language model|llm|data quality|data governance|sql|python|r programming)\b', re.I)
NT_BODY = re.compile(r'\b(network|tcp/?ip|router|switch|firewall|dns|dhcp|lan|wan|wireless|wifi|wi-fi|noc|soc|siem|cyber ?security|information security|security operations|server administration|windows server|linux administration|active directory|vmware|infrastructure|network monitoring|cloud infrastructure)\b', re.I)
WD_BODY = re.compile(r'\b(web (?:application|development|site|platform)|website|front[- ]?end|back[- ]?end|full[- ]?stack|html|css|javascript|typescript|react|angular|vue|node(?:\.js)?|django|flask|laravel|spring boot|rest api|web api|responsive design|e-commerce platform)\b', re.I)
GAME_BODY = re.compile(r'\b(gameplay|game development|game design|video game|gaming|unity|unreal|godot|game engine|level design|game qa|game testing|game test|gameplay systems|game mechanics|game asset|game prototype|game balancing|core loops?|game (?:ui|interface)|ui/ux for games)\b', re.I)
COMMON_TASK = re.compile(r'\b(software development|software engineering|programming|write code|develop software|build software|develop applications?|build applications?|database (?:development|administration|design)|software testing|test cases?|bug tracking|application support|it support|systems administration|computer systems|technical support|automation scripts?|quality assurance|programmer)\b', re.I)

def capability_evidence(desc):
    """Return a source sentence only when a capability and task/requirement cue co-occur."""
    for segment in re.split(r'(?<=[.!?;])\s+|\s+•\s+', desc):
        if TECH.search(segment) and (ACTION.search(segment) or REQ.search(segment)):
            return segment.strip(), TECH.search(segment).group(0)
    return '', ''

def evidence_window(pattern, desc):
    segments = re.split(r'(?<=[.!?;])\s+|\s+•\s+', desc)
    for segment in segments:
        if pattern.search(segment) and (ACTION.search(segment) or REQ.search(segment)):
            return segment.strip()[:220]
    for segment in segments:
        if pattern.search(segment):
            return segment.strip()[:220]
    return ''

OUT_FIELDS = ['source_id','source_url','title','employer','location','work_type','scope','cohort','cohort_evidence','technical_assessability','supported_memberships','unresolved_reason','track_evidence','technical_evidence','raw_pointer','source_index_raw_hash','decision_status']
out=[]
for sid,(raw,pointer,raw_hash) in sorted(rows.items(), key=lambda z:int(z[0])):
    f = raw.get('fields',raw.get('payload',raw))
    raw_id = str(f.get('id') or f.get('seekJobId') or '')
    if raw_id != sid:
        raise RuntimeError(f'Raw pointer ID mismatch for {sid}: {raw_id}')
    title = clean(f.get('title',''))
    desc = clean(f.get('description_text') or f.get('descriptionText') or f.get('description_html') or f.get('descriptionHtml') or f.get('description') or '')
    work = clean(f.get('workType') or f.get('employmentType') or '')
    loc = clean(f.get('location') or '')
    url = f.get('url') or f.get('canonicalUrl') or f'https://ph.jobstreet.com/job/{sid}'
    employer = clean(f.get('company') or f.get('employer') or '')
    text = title + ' ' + desc
    # Geographic evidence: local Philippine place names, or explicit Philippines remote eligibility.
    local = str(f.get('locationCountry') or f.get('sourceCountry') or '').upper()=='PH' or bool(re.search(r'\b(Philippines|Philippine|Metro Manila|Manila|Quezon City|Makati|Pasig|Taguig|Mandaluyong|Cebu|Davao|Cavite|Laguna|Pampanga|Baguio|Iloilo|Bacolod|Batangas|Cagayan de Oro|Antipolo|Paranaque|Muntinlupa|Bulacan|Rizal|Calabarzon|Central Luzon|Central Visayas|Northern Mindanao|Legazpi|Albay|Subic|Zambales)\b', loc, re.I))
    if not local and re.search(r'\b(remote|work from home|wfh)\b', loc, re.I):
        local = bool(re.search(r'\b(Philippines|Philippine|PH-based|based in PH|eligible in PH)\b', desc, re.I))
    scope = 'in_scope' if local else ('unclear' if not loc or re.search(r'\b(remote|work from home|wfh)\b',loc,re.I) else 'out_of_scope')
    # A source body can identify an actual internship even when the provider
    # title/work-type fields say Web Developer / Full time.
    actual_internship = bool(re.search(r'^\s*(?:intern|internship|OJT)\b|\b(?:intern|internship)\s*(?:[-|:]|$)', title, re.I)) or bool(re.search(r'\bWeb Development Intern\b', desc, re.I))
    cohort_ambiguous = bool(re.search(r'\b(?:open to intern|open to OJT|apprentice)\b', title, re.I))
    if actual_internship:
        cohort='internship'
    elif cohort_ambiguous:
        cohort='unclear'
    elif re.search(r'\b(full[- ]?time|part[- ]?time|contract|temporary|permanent|casual|freelance|project[- ]?based)\b', work, re.I):
        cohort='employment'
    else:
        cohort='unclear'
    if re.search(r'\bWeb Development Intern\b', desc, re.I):
        cohort_evidence='description: '+evidence_window(re.compile(r'\bWeb Development Intern\b',re.I),desc)
    elif actual_internship:
        cohort_evidence='title: '+title
    elif cohort_ambiguous:
        cohort_evidence='title: '+title
    else:
        cohort_evidence='work type: '+work
    tech_passage, cap = capability_evidence(desc)
    has_tech = bool(tech_passage) and len(desc) >= 300
    if not desc:
        assess='unclear'
    elif has_tech:
        assess='assessable'
    else:
        assess='unassessable'
    memberships=[]
    track_evidence=[]
    reasons=[]
    # Track links are sourced independently of assessability; the final count requires both.
    # Do not assign IS merely because the title/body mentions AI. Require
    # source duties that engineer/evaluate AI systems; using AI coding tools,
    # authoring benchmark tasks, or generic infrastructure/QA prose alone is
    # insufficient. These explicit exclusions address reviewed false links.
    is_task = re.compile(r'\b(?:design|develop|build|implement|integrate|train|evaluate|deploy|deployment|maintain|test|validate|monitor|utiliz\w*|architect\w*)\b[^.!?;]{0,180}\b(?:AI|artificial intelligence|machine learning|ML|LLM|large language model|AI agent|AI model|AI application|AI solution|AI system|AI chatbot|AI response|AI output|AI-enabled solution|AI-powered application|AI model ecosystem|data engineering|data pipeline|data warehouse|data science|data analytics|statistical modeling|predictive modeling)\b|\b(?:AI|artificial intelligence|machine learning|ML|LLM|large language model|AI agent|AI model|AI application|AI solution|AI system|AI chatbot|AI response|AI output|AI-enabled solution|AI-powered application|AI model ecosystem|data engineering|data pipeline|data warehouse|data science|data analytics|statistical modeling|predictive modeling)\b[^.!?;]{0,180}\b(?:design|develop|build|implement|integrate|train|evaluate|deploy|deployment|maintain|test|validate|monitor|utiliz\w*|architect\w*)\b', re.I)
    is_evidence = next((segment.strip() for segment in re.split(r'(?<=[.!?;])\s+|\s+•\s+', desc) if is_task.search(segment)), '')
    ai_system_work = bool(is_evidence)
    if IS_TITLE.search(title) and IS_BODY.search(desc) and ai_system_work and sid not in {'95302874','95310775'}:
        memberships.append('Intelligent Systems'); track_evidence.append('IS: '+is_evidence[:220])
    if NT_TITLE.search(title) and NT_BODY.search(desc):
        memberships.append('Network Technology'); track_evidence.append('NT: '+evidence_window(NT_BODY,desc))
    web_role = bool(re.search(r'\b(web\s+(?:developer|engineer|programmer|application)|front[- ]?end|back[- ]?end|full[- ]?stack)\b', title, re.I))
    web_duties = re.compile(r'\b(web application|web development|websites?|e-commerce platform|responsive (?:web|website)|frontend|front-end|backend|back-end|full[- ]?stack)\b', re.I)
    if (web_role or (WD_TITLE.search(title) and web_duties.search(desc))) and WD_BODY.search(desc):
        memberships.append('Web Development'); track_evidence.append('WD: '+evidence_window(WD_BODY,desc))
    game_capability = re.compile(r'\b(test cases?|bug reports?|test plans?|prototyp(?:e|ing)|scripting|technical design|game mechanics?|game systems|core loops?|level design|game prototyping|game balancing|gameplay mechanics|game (?:ui|interface)|ui/ux for games|unity|unreal|godot|game engine)\b', re.I)
    game_evidence = evidence_window(game_capability,desc)
    game_programming_title = bool(re.search(r'\b(game|gameplay|gaming)\b.*\b(programmer|developer|engineer)\b|\b(programmer|developer|engineer)\b.*\b(game|gameplay|gaming)\b',title,re.I))
    game_qa_title = bool(re.search(r'\b(game|gameplay|gaming)\b.*\b(qa|quality assurance|tester|test lead)\b|\b(qa|tester|test lead)\b.*\b(game|gameplay|gaming)\b',title,re.I))
    game_design_title = bool(GAME_TITLE.search(title) and re.search(r'\b(designer|design|product manager)\b',title,re.I))
    game_link = GAME_TITLE.search(title) and GAME_BODY.search(desc) and (
        (game_programming_title and bool(tech_passage)) or
        (game_qa_title and bool(tech_passage)) or
        (game_design_title and bool(game_evidence) and bool(tech_passage))
    )
    if game_link:
        memberships.append('Game Development'); track_evidence.append('GD: '+game_evidence)
    if CORE_TITLE.search(title) or COMMON_TASK.search(desc):
        memberships.append('Shared/core'); track_evidence.append('Shared/core: '+(title or evidence_window(COMMON_TASK)))
    if sid == '95310775' and 'Shared/core' not in memberships:
        memberships.append('Shared/core'); track_evidence.append('Shared/core: AI coding tools used to build full-stack financial systems; no AI-system engineering duties supported.')
    if assess != 'assessable': reasons.append('technical requirements/duties insufficient or description missing')
    if scope != 'in_scope': reasons.append('Philippine work eligibility not explicit from location')
    if cohort == 'unclear': reasons.append('title/work type does not establish employment versus internship')
    if not memberships and assess=='assessable': reasons.append('no supported track/core membership from title and source text')
    # Keep the first source-derived capability passage, not a query label or prior decision.
    evidence = tech_passage[:220] if tech_passage else (desc[:120] if desc else '')
    out.append({'source_id':sid,'source_url':url,'title':title,'employer':employer,'location':loc,'work_type':work,'scope':scope,'cohort':cohort,'cohort_evidence':cohort_evidence,'technical_assessability':assess,'supported_memberships':';'.join(memberships),'unresolved_reason':'; '.join(reasons),'track_evidence':' || '.join(track_evidence)[:360],'technical_evidence':evidence,'raw_pointer':pointer,'source_index_raw_hash':raw_hash,'decision_status':'automated_provisional'})
if len(out)!=483 or len({x['source_id'] for x in out})!=483: raise RuntimeError(f'frame expected 483 unique, got {len(out)}')
if {x['source_id'] for x in out} != core_ids|pilot_add_ids|bf_case_ids:
    raise RuntimeError('The reviewed source IDs differ from the reconciled 483-ID union')
with (OUT/'four_track_saved_posting_assessment_2026-10-24.csv').open('w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=OUT_FIELDS); w.writeheader(); w.writerows(out)
# summarize only in-scope employment, technically assessable; membership intersections are distinct IDs.
eligible=[x for x in out if x['scope']=='in_scope' and x['cohort']=='employment' and x['technical_assessability']=='assessable' and x['supported_memberships']]
tracks=['Game Development','Intelligent Systems','Network Technology','Web Development','Shared/core']
print('frame',len(out),'supported assessable in-scope employment',len(eligible))
print('cohort',Counter(x['cohort'] for x in out))
print('scope',Counter(x['scope'] for x in out))
print('assessability',Counter(x['technical_assessability'] for x in out))
for t in tracks: print(t,sum(t in x['supported_memberships'].split(';') for x in eligible))
print('overlap pairs')
for i,a in enumerate(tracks):
 for b in tracks[i+1:]:
  n=sum(a in x['supported_memberships'].split(';') and b in x['supported_memberships'].split(';') for x in eligible)
  if n: print(a,'&',b,n)
print('no memberships among eligible',sum(not x['supported_memberships'] for x in eligible))
print('in-scope employment',sum(x['scope']=='in_scope' and x['cohort']=='employment' for x in out))
print('unresolved rows',sum(bool(x['unresolved_reason']) for x in out))
print('artifact',OUT/'four_track_saved_posting_assessment_2026-10-24.csv')
