"""Explicitly retain fictional demo records and verify a real Hindsight round trip."""
import sys
from afteraction.config import Config
from afteraction.service import Agent
from afteraction.sample import CURRENT
from afteraction.memory import MemoryUnavailable


def main():
    config = Config.from_env()
    if config.mode != 'hindsight':
        print('Set MEMORY_MODE=hindsight and configure a dedicated demo bank first.')
        return 1
    agent = Agent(config)
    print('Writing three fictional demo outcomes to the configured Hindsight bank...')
    result = agent.seed()
    if result['warnings']:
        print('\n'.join(result['warnings']))
        return 1
    try:
        result = agent.investigate(CURRENT)
    except MemoryUnavailable as exc:
        print(str(exc)); return 1
    decision = result['decision']
    for key in ('proposed','avoided','conflicts'):
        print(key + ': ' + str(len(decision[key])))
    if result['warning'] or not decision['proposed'] or not decision['avoided']:
        print(result['warning'] or 'Expected evidence missing. Check bank, source resolution and indexing; then retry.')
        return 1
    print('PASS: real retain/recall/reflect completed with applicable source evidence.')
    print('Inspect the UI and reflection manually before recording. This is not a benchmark.')
    return 0

if __name__ == '__main__':
    sys.exit(main())
