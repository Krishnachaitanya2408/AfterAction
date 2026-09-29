"""Validation and deterministic applicability policy. Independent of the LLM."""
import re
from datetime import datetime, timezone

FIELDS = ('service', 'environment', 'architecture', 'symptom', 'action', 'outcome', 'reason', 'observed_at')


def redact(text):
    # Best effort only: sanitized input is still the operator's responsibility.
    text = re.sub(r'(?i)(authorization\s*:\s*bearer\s+)\S+', r'\1[REDACTED]', text)
    text = re.sub(r'(?i)\b(api[_-]?key|password|secret|token)\s*[:=]\s*[^\s,;]+', r'\1=[REDACTED]', text)
    return text


def clean(value, name, limit=2000):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f'{name} must be non-empty text (maximum {limit} characters)')
    return redact(value.strip())


def incident(data):
    if not isinstance(data, dict):
        raise ValueError('Expected a JSON object')
    result = {k: clean(data.get(k), k, 100) for k in ('service', 'environment', 'architecture')}
    for k in result:
        if not re.fullmatch(r'[a-zA-Z0-9][a-zA-Z0-9_.-]*', result[k]):
            raise ValueError(f'{k}: use letters, numbers, dots, underscores or hyphens')
        result[k] = result[k].lower()
    result['symptom'] = clean(data.get('symptom'), 'symptom', 5000)
    return result


def lesson(data):
    row = incident(data)
    row.update({k: clean(data.get(k), k) for k in ('action', 'reason')})
    row['outcome'] = data.get('outcome')
    if row['outcome'] not in ('helped', 'failed', 'inconclusive'):
        raise ValueError('outcome must be helped, failed or inconclusive')
    observed = clean(data.get('observed_at'), 'observed_at', 40)
    try:
        date = datetime.fromisoformat(observed.replace('Z', '+00:00'))
        if not date.tzinfo:
            raise ValueError('Timezone missing')
        if date > datetime.now(timezone.utc):
            raise ValueError('Future timestamp')
    except ValueError:
        raise ValueError('observed_at must be an ISO timestamp with timezone, not in the future') from None
    row['observed_at'] = date.astimezone(timezone.utc).isoformat()
    return row


def tokens(text):
    return set(re.findall(r'[a-z0-9]{3,}', text.lower())) - {'the','and','with','for','was','from','after','during'}


def decide(current, candidates):
    eligible, excluded = [], []
    for row in candidates:
        mismatches = [k for k in ('service', 'environment', 'architecture') if row[k] != current[k]]
        if row.get('retired'):
            mismatches.append('retired by operator')
        if mismatches:
            excluded.append({**row, 'excluded_reason': ', '.join(mismatches)})
        else:
            eligible.append(row)
    groups = {}
    for row in eligible:
        key = ' '.join(row['action'].lower().split())
        groups.setdefault(key, []).append(row)
    proposed, avoided, conflicts, uncertain = [], [], [], []
    for rows in groups.values():
        outcomes = {r['outcome'] for r in rows}
        item = {'action': rows[0]['action'], 'sources': [r['id'] for r in rows],
                'reasons': [r['reason'] for r in rows]}
        if {'helped', 'failed'} <= outcomes:
            conflicts.append(item)
        elif 'failed' in outcomes:
            avoided.append(item)
        elif 'helped' in outcomes:
            proposed.append(item)
        else:
            uncertain.append(item)
    return dict(eligible=eligible, excluded=excluded, proposed=proposed, avoided=avoided,
                conflicts=conflicts, uncertain=uncertain)


BASELINE = [
    'Confirm the affected service, error rate, latency and start time.',
    'Compare the incident onset with recent changes; inspect read-only metrics and logs.',
    'Check dependency saturation and connection pressure before choosing an intervention.',
    'Ask the on-call owner to approve a bounded experiment and define rollback criteria.'
]
