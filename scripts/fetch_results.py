#!/usr/bin/env python3
"""Retrieve only the LA mayoral totals from the official county election JSON.

Safeguards: verified election ID, exact mayoral contest, both named candidates,
valid timestamp, nonempty votes, no regression to an older bulletin, no fabricated totals.
"""
import datetime as dt
import json
import pathlib
import time
import urllib.request
from zoneinfo import ZoneInfo

ROOT=pathlib.Path(__file__).resolve().parents[1]
FILE=ROOT/'data'/'results.json'
URL='https://results.lavote.gov/electionresults/json?electionid=4348'
NOW=lambda:dt.datetime.now(dt.timezone.utc).isoformat(timespec='seconds')

def read_county():
    headers={'User-Agent':'Mozilla/5.0 LA-election-data-tracker/1.0 (GitHub Actions; public results)',
             'Accept':'application/json, text/plain;q=0.9, */*;q=0.8',
             'Cache-Control':'no-cache','Pragma':'no-cache'}
    errors=[]
    for attempt in range(4):
        try:
            req=urllib.request.Request(URL,headers=headers)
            with urllib.request.urlopen(req,timeout=35) as response:
                raw=response.read(12_000_001)
            if len(raw)>12_000_000:raise ValueError('Source exceeded reasonable size limit')
            data=json.loads(raw.decode('utf-8-sig'))
            if not isinstance(data,dict):raise ValueError('County response was not a JSON object')
            return data
        except Exception as exc:
            errors.append(f'Attempt {attempt+1}: {type(exc).__name__}: {exc}')
            if attempt<3:time.sleep(2*(attempt+1))
    raise RuntimeError('LA County official JSON request failed: '+' | '.join(errors))

def parse(data):
    election=data.get('Election')
    if not isinstance(election,dict) or election.get('ID')!=4348:
        raise ValueError('Wrong election ID')
    matches=[]
    for group in election.get('ContestGroups',[]):
        for contest in group.get('Contests',[]):
            if str(contest.get('Title','')).strip().casefold()=='los angeles city general municipal election mayor':
                matches.append(contest)
    if len(matches)!=1:raise ValueError(f'Expected one LA mayoral contest; found {len(matches)}')
    def find_name(name):
        found=[c for c in matches[0].get('Candidates',[]) if str(c.get('Name','')).strip().casefold()==name.casefold()]
        if len(found)!=1:raise ValueError(f'Expected exactly one {name}; got {len(found)}')
        votes=found[0].get('Votes')
        if type(votes) is not int or votes<0:raise ValueError(f'Invalid vote count for {name}')
        return votes
    raman=find_name('NITHYA RAMAN')
    bass=find_name('KAREN RUTH BASS')
    if raman+bass==0:raise ValueError('County has not published votes for this contest yet')
    stamp=data.get('Timestamp')
    if not isinstance(stamp,str):raise ValueError('Missing official timestamp')
    d = dt.datetime.fromisoformat(stamp.replace('Z', '+00:00'))
    if d.tzinfo is None:
        d = d.replace(tzinfo=ZoneInfo("America/Los_Angeles"))
    if d.date() < dt.date(2026, 11, 3):
        raise ValueError('Timestamp predates election day')
    return {'stamp': d.isoformat(), 'raman': raman, 'bass': bass}


def update(previous,new):
    now=NOW()
    history=previous.get('history',[])
    if not isinstance(history,list):history=[]
    old=previous.get('latest')
    if old:
        old_t=dt.datetime.fromisoformat(old['stamp'].replace('Z','+00:00'))
        new_t=dt.datetime.fromisoformat(new['stamp'].replace('Z','+00:00'))
        if new_t<old_t:
            raise ValueError('Source returned an older county bulletin; preserving newer totals')
        if new_t==old_t and (new['raman'],new['bass'])!=(old['raman'],old['bass']):
            raise ValueError('Same timestamp with conflicting counts; preserving prior totals')
        if (old['raman'],old['bass'])==(new['raman'],new['bass']):
            # No new votes. Keep last results and history; update successful poll time.
            new=old
        else:
            history.append(new)
    else:
        history=[new]
    # Cap history so the published JSON remains compact.
    result={'schema_version':1,'election_id':4348,'latest':new,'history':history[-150:],
            'last_checked_at':now,'source_url':URL}
    FILE.parent.mkdir(parents=True,exist_ok=True)
    FILE.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    return result

def main():
    previous=json.loads(FILE.read_text(encoding='utf-8')) if FILE.exists() else {}
    new=parse(read_county())
    result=update(previous,new)
    item=result['latest']
    print('LA County report: '+item['stamp'])
    print(f'Raman: {item["raman"]:,} | Bass: {item["bass"]:,} | Lead: {abs(item["raman"]-item["bass"]):,}')
    print(f'Successful county check: {result["last_checked_at"]}; stored snapshots: {len(result["history"])}')

if __name__=='__main__':main()
