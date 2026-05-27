# Cloudflare Tunnel — Validation Checklist

Use this checklist:

- after initial install
- after any config change to `/etc/cloudflared/config.yml` or `/opt/traefik/dynamic/loosearrow-public.yml`
- after a prometheus reboot
- after upgrading cloudflared
- if any public route becomes unreachable

---

## A. Service Health

On prometheus:

```bash
sudo systemctl status cloudflared
```

Pass criteria:

- Status is `active (running)`
- No `FATAL` or repeated connection errors in recent journal entries

Check recent logs:

```bash
sudo journalctl -u cloudflared -n 30 --no-pager
```

Pass criteria:

- Logs show `INF Connection established` entries
- All pre-flight checks pass: DNS Resolution, UDP Connectivity, TCP Connectivity, Cloudflare API

---

## B. Tunnel Status in Dashboard

Go to **Cloudflare Zero Trust → Networks → Tunnels**.

Pass criteria:

- Tunnel `prometheus` shows status **Healthy**
- At least one connector is connected

---

## C. Traefik Routing (Local)

On prometheus, test that Traefik routes public hostnames correctly:

```bash
curl -sk -H "Host: chat.loosearrowlabs.com" https://localhost:443/ -o /dev/null -w "chat -> %{http_code}\n"
curl -sk -H "Host: search.loosearrowlabs.com" https://localhost:443/ -o /dev/null -w "search -> %{http_code}\n"
curl -sk -H "Host: comfy.loosearrowlabs.com" https://localhost:443/ -o /dev/null -w "comfy -> %{http_code}\n"
```

Pass criteria:

- `chat` and `search` return HTTP 200
- `comfy` returns HTTP 200 if ComfyUI container is running; 502 if container is stopped (expected)

Check Traefik logs for config errors:

```bash
docker logs traefik --since 60s 2>&1 | grep -i "err\|warn\|loosearrow"
```

Pass criteria:

- No YAML parse errors for `loosearrow-public.yml`

---

## D. DNS Records

Confirm CNAMEs exist and are Cloudflare-proxied:

```bash
# From any machine with dig or nslookup
dig chat.loosearrowlabs.com CNAME
dig search.loosearrowlabs.com CNAME
dig app.loosearrowlabs.com CNAME
```

Pass criteria:

- Each name resolves to a Cloudflare proxy IP (not the tunnel target directly)
- Records are not returning NXDOMAIN

---

## E. End-to-End Reachability

From any external machine or browser:

```bash
curl -sI https://chat.loosearrowlabs.com -o /dev/null -w "%{http_code}\n"
curl -sI https://search.loosearrowlabs.com -o /dev/null -w "%{http_code}\n"
```

Pass criteria (with Cloudflare Access configured):

- Returns HTTP 200 after successful Access login
- Returns HTTP 302 or 403 if not authenticated (Access redirect to login)

Pass criteria (without Cloudflare Access):

- Returns HTTP 200 directly (means Access is NOT configured — fix this)

---

## F. Cloudflare Access Gate

Visit each public URL in a browser without being logged in to Cloudflare Access.

Pass criteria:

- You are redirected to a Cloudflare Access login page
- After logging in with the authorized email, you reach the service

Failure signature:

- Service loads immediately without a login prompt — Access policy is missing or misconfigured

---

## G. Auto-Start on Reboot

Verify the service is enabled:

```bash
sudo systemctl is-enabled cloudflared
```

Pass criteria:

- Returns `enabled`

---

## H. app.loosearrowlabs.com Direct Route

Test the homelable frontend direct route (bypasses Traefik):

```bash
# On prometheus
curl -s http://localhost:3000 -o /dev/null -w "%{http_code}\n"
```

Pass criteria:

- Returns HTTP 200 if `homelable-frontend-1` container is running

---

## Quick Outcome

If A through G pass: tunnel is healthy and all public routes are working correctly.

If F fails (no Access gate): stop and add Cloudflare Access policies before using the service externally.

If C fails: check Traefik dynamic config syntax and container health for the target service.

If B fails (tunnel inactive): restart cloudflared and check logs for auth or connectivity errors.
