# KasmVNC Setup

A KasmVNC server with XFCE4 desktop environment is now installed and configured.

## Ports & Address
- Web interface (HTTPS): `https://127.0.1.1:8444`
- Default internal VNC port: `5901` (Display `:1`)

## Credentials
- User: `nailwilson`
- Password: `yyzz13116822`

*(Note: Use these credentials to login via the KasmVNC web interface. The default `root` user is also available.)*

## Services
- Start VNC Server: `echo "1" | kasmvncserver :1`
- Stop VNC Server: `kasmvncserver -kill :1`

## Desktop Environment
The system uses `XFCE4` as its primary desktop environment, launched automatically on startup via `~/.vnc/xstartup`.
