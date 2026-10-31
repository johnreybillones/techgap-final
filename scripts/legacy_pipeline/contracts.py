"""Frozen identities for the first admission-only P2A implementation."""

POLICY_VERSION = "entry-junior-internship-v3-auto"
EXTRACTOR_MODEL = {"id": "fastino/gliner2-base-v1", "revision": "f9634218e53580c56edf0de97ca1a7d3f1c2354e"}
RETRIEVER_MODEL = {"id": "sentence-transformers/all-mpnet-base-v2", "revision": "e8c3b32edf5434bc2275fc9bab85f82640a19130"}
CLASSIFIER_MODEL = {"id": "MoritzLaurer/deberta-v3-base-zeroshot-v2.0", "revision": "8e7e5af5983a0ddb1a5b45a38b129ab69e2258e8"}
TRACKS = {
    "web-mobile": "designs or builds web or mobile software systems",
    "business-analytics": "analyzes organizational data or builds information systems for decisions",
    "service-management": "operates, governs, secures, or supports computing services and infrastructure",
    "networking": "designs, operates, or secures computer networks and communications",
    "shared-core": "performs meaningful cross-track software, data, testing, security, or computing work",
}

