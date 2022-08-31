import requests
import datetime
import json


DRG_API  = 'https://drg.ghostship.dk/events'
STEAMCMD = 'https://api.steamcmd.net/v1/info'


DRG_ID = 548430
DRG_UA = 'FSD/main-CL'
DD_START = datetime.datetime(2019, 9, 26)


def request_build():
    """ Request current DRG build information """

    res = requests.get(f'{STEAMCMD}/{DRG_ID}')
    if res.status_code != 200:
        print(f'[!] Failed to retrieve steam info... Status={res.status_code}')
        return

    if not (data := res.json()['data']):
        print(f'[!] SteamCMD returned invalid app info...')
        return 
    
    try:
        depots = data[f'{DRG_ID}']['depots']
        branch = depots['branches']
        
        manifest = depots['548431']['manifests']['public']
        build_id = branch['public']['buildid']
        updated_at = branch['public']['timeupdated']

        updated_at = datetime.datetime.fromtimestamp(int(updated_at))
        updated_at = updated_at.isoformat()

    except KeyError as err:
        print(json.dumps(data, indent=2), '\n')
        raise err

    return {'build_id': build_id, 'manifest': manifest, 'updated_at': updated_at}


def request_seeds():
    """ Return weekly and deepdive seeds from API """

    wk_seed = requests.get(f'{DRG_API}/weekly', headers={'User-Agent': DRG_UA})
    dd_seed = requests.get(f'{DRG_API}/deepdive', headers={'User-Agent': DRG_UA})

    if not (wk_seed.status_code and dd_seed.status_code == 200):
        print('[!] Error retrieving seed information from DRG...')
        print(f'\t- Weekly status: {wk_seed.status_code}')
        print(f'\t- Deepdive status: {dd_seed.status_code}')
        return

    return {'deepdive': dd_seed.json(), 'weekly': wk_seed.json()}


def main():
    dd_week = (datetime.datetime.now() - DD_START).days // 7 + 1

    with open('weeks.json', "r+") as seedlist:
        seeds = json.load(seedlist)
        seedlist.seek(0)

        if str(dd_week) in seeds:
            print(f'[!] Key for week {dd_week} already exists...')
            exit(-1)

        print('[+] Requesting current build information from steam...')
        drg_build = request_build()
        print('[+] Requesting current seed information from DRG...')
        drg_seeds = request_seeds()

        if not (drg_build and drg_seeds):
            exit(-1)

        print(f'[+] Adding week {dd_week} to week entries...')
        seeds[str(dd_week)] = {'seeds': drg_seeds, 'build': drg_build}
        json.dump(seeds, seedlist, indent=2)

if __name__ == '__main__':
    main()
