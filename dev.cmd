@echo off
rem Start the Code Yaar API and web app together.
rem Usage: dev            (defaults: API 8000, app 3000)
rem        dev -Setup     (also install dependencies)
rem        dev -Force     (stop whatever holds the ports, then start)
rem        dev -BackendPort 8001 -FrontendPort 3001
rem Extra arguments are forwarded to scripts\dev.ps1.
powershell -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\dev.ps1" %*
