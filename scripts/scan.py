import argparse
import json
import os
import subprocess
import sys
import time


def gcloud_describe(image_uri):
    r = subprocess.run(
        ['gcloud', 'artifacts', 'docker', 'images', 'describe', image_uri,
         '--show-package-vulnerability', '--format=json'],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        # Surface the real reason instead of silently retrying forever.
        print(f"  gcloud error (rc={r.returncode}): {r.stderr.strip()}", file=sys.stderr)
        # Permission/auth/config errors will never resolve by waiting —
        # fail fast instead of burning the whole timeout window on retries.
        if 'PERMISSION_DENIED' in r.stderr or 'permission' in r.stderr.lower():
            print("  FATAL: permission error detected, not retrying.", file=sys.stderr)
            sys.exit(3)
        return None
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return None


_CLEAN_SCAN = {'package_vulnerability_summary': {'vulnerabilities': {}}}
_SCAN_TERMINAL = ('FINISHED_SUCCESS', 'FINISHED_FAILED', 'FINISHED_UNSUPPORTED')


def scan_finished(data):
    discoveries = data.get('discovery_summary', {}).get('discovery', [])
    return any(
        d.get('discovery', {}).get('analysisStatus', '') in _SCAN_TERMINAL
        for d in discoveries
    )


def poll(image_uri, max_wait, interval):
    elapsed = 0
    while True:
        data = gcloud_describe(image_uri)
        if data and 'package_vulnerability_summary' in data:
            return data
        if data and scan_finished(data):
            print("  Scan complete — no vulnerabilities found.")
            return _CLEAN_SCAN
        if elapsed >= max_wait:
            return None
        print(f"  Scan pending... ({elapsed}s elapsed)")
        time.sleep(interval)
        elapsed += interval


def fixable(vuln):
    return any(
        issue.get('fixedVersion', {}).get('kind') != 'MAXIMUM'
        for issue in vuln.get('vulnerability', {}).get('packageIssue', [])
    )


def split(vulns, severity):
    items = vulns.get(severity, [])
    yes = [v for v in items if fixable(v)]
    no  = [v for v in items if not fixable(v)]
    return items, yes, no


def console_url(image_uri):
    parts    = image_uri.split('/')
    host     = parts[0]
    project  = parts[1]
    repo     = parts[2]
    image    = '/'.join(parts[3:]).split(':')[0].split('@')[0]
    location = host.replace('-docker.pkg.dev', '')
    return (
        f"https://console.cloud.google.com/artifacts/docker/"
        f"{project}/{location}/{repo}/{image}?project={project}"
    )


def print_table(cf, cu, highs, hf, hu, meds, mf, mu, lows, lf, lu):
    print("  +------------+-------+-------------------+----------------+")
    print(f"  | {'Severity':<10} | {'Count':>5} | {'  Fix Available':<17} | {'Action':<14} |")
    print("  |            |       +---------+---------+                |")
    print(f"  |            |       | {'Yes':>7} | {'No':>7} |                |")
    print("  +------------+-------+---------+---------+----------------+")

    def row(sev, total, yes, no, action):
        print(f"  | {sev:<10} | {total:>5} | {yes:>7} | {no:>7} | {action:<14} |")

    row("CRITICAL", cf + cu,     cf,       cu,       "BLOCK" if cf > 0 else "WARN, pass")
    row("HIGH",     len(highs),  len(hf),  len(hu),  "WARN, pass")
    row("MEDIUM",   len(meds),   len(mf),  len(mu),  "pass")
    row("LOW",      len(lows),   len(lf),  len(lu),  "pass")
    print("  +------------+-------+---------+---------+----------------+")


def main():
    parser = argparse.ArgumentParser(
        description='GAR vulnerability gate — Binary Authorization signing decision'
    )
    parser.add_argument('images', nargs='+', metavar='image-uri',
                        help='full GAR image URI(s) to scan')
    parser.add_argument('--timeout', type=int,
                        default=int(os.environ.get('MAX_WAIT', '300')),
                        metavar='SECONDS',
                        help='how long to wait for scan results (default: 300)')
    args = parser.parse_args()

    max_wait  = args.timeout
    interval  = 15
    sign_file = os.environ.get('SIGN_FILE', '/tmp/binauth_sign')

    for uri in args.images:
        print("========================================")
        print(f"Image : {uri}")
        print()

        url  = console_url(uri)
        data = poll(uri, max_wait, interval)

        if data is None:
            print(f"  ERROR: scan timed out after {max_wait}s")
            sys.exit(2)

        vulns = data.get('package_vulnerability_summary', {}).get('vulnerabilities', {})

        _, crit_fix, crit_nofix = split(vulns, 'CRITICAL')
        highs, high_fix, high_nofix = split(vulns, 'HIGH')
        meds,  med_fix,  med_nofix  = split(vulns, 'MEDIUM')
        lows,  low_fix,  low_nofix  = split(vulns, 'LOW')

        cf = len(crit_fix)
        cu = len(crit_nofix)

        if cf > 0:
            status     = "FAIL"
            image_sign = False
        else:
            status     = "PASS"
            image_sign = True

        with open(sign_file, 'w') as sf:
            sf.write('true' if image_sign else 'false')

        print(f"  Status : {status}")
        print()
        print_table(cf, cu, highs, high_fix, high_nofix,
                    meds, med_fix, med_nofix,
                    lows, low_fix, low_nofix)
        print()

        if cf > 0:
            print(f"  [BLOCK] {cf} CRITICAL vuln(s) have patches available — Binary Authorization will NOT sign this image.")
        if cu > 0:
            print(f"  [WARN]  {cu} CRITICAL vuln(s) present — no patch available yet, monitor closely.")
        if highs:
            print(f"  [WARN]  {len(highs)} HIGH vuln(s) detected — review and schedule remediation.")
        print()
        print(f"  GCP Console : {url}")
        print(f"  binauth_sign : {'true' if image_sign else 'false'}")
        print()

    print("========================================")
    sys.exit(0)


if __name__ == '__main__':
    main()
