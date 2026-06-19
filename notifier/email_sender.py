import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def _get_smtp_config():
    return {
        "host": os.getenv("SMTP_HOST", "smtp.qq.com"),
        "port": int(os.getenv("SMTP_PORT", "587")),
        "user": os.getenv("SMTP_USER", ""),
        "password": os.getenv("SMTP_PASSWORD", ""),
        "to": os.getenv("NOTIFY_EMAIL", ""),
        "use_tls": os.getenv("SMTP_USE_TLS", "true").lower() == "true",
        "use_ssl": os.getenv("SMTP_USE_SSL", "false").lower() == "true",
    }


def send_email(subject: str, body_html: str) -> bool:
    """Send an email notification. Returns True on success."""
    cfg = _get_smtp_config()
    if not cfg["user"] or not cfg["password"] or not cfg["to"]:
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = cfg["user"]
        msg["To"] = cfg["to"]
        msg.attach(MIMEText(body_html, "html", "utf-8"))

        if cfg["use_ssl"]:
            server = smtplib.SMTP_SSL(cfg["host"], cfg["port"], timeout=15)
        else:
            server = smtplib.SMTP(cfg["host"], cfg["port"], timeout=15)
            if cfg["use_tls"]:
                server.starttls()

        server.login(cfg["user"], cfg["password"])
        server.sendmail(cfg["user"], [cfg["to"]], msg.as_string())
        server.quit()
        return True
    except Exception as e:
        print(f"[Email] Failed to send: {e}", flush=True)
        return False


def build_route_alert_html(article, routes) -> str:
    """Build an HTML email body for route alert."""
    title = article.title
    summary = article.ai_summary_cn or article.summary_raw or "无摘要"
    carrier = article.carrier or "Unknown"

    route_rows = ""
    for r in routes:
        action_map = {
            "new": "新增", "resumed": "恢复", "suspended": "停运",
            "increased_freq": "加密班次", "decreased_freq": "减少班次", "aircraft_change": "机型更换"
        }
        action_cn = action_map.get(r.action, r.action)
        date_str = r.effective_date.strftime("%Y-%m-%d") if r.effective_date else "-"
        route_rows += f"""
        <tr>
            <td style="padding:8px 12px;border-bottom:1px solid #eee;">{r.origin} → {r.destination}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #eee;color:{'#059669' if r.action == 'new' else '#d97706' if r.action == 'suspended' else '#2563eb'};">{action_cn}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #eee;">{date_str}</td>
            <td style="padding:8px 12px;border-bottom:1px solid #eee;">{r.aircraft_type or '-'}</td>
        </tr>"""

    return f"""
    <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;max-width:600px;margin:0 auto;border:1px solid #e5e7eb;border-radius:8px;overflow:hidden;">
        <div style="background:#1e40af;color:white;padding:16px 24px;">
            <h2 style="margin:0;font-size:18px;">MyNewsAVI · 航线变动警报</h2>
        </div>
        <div style="padding:24px;">
            <p style="color:#6b7280;font-size:13px;margin:0 0 8px 0;">{carrier} 航线动态</p>
            <h3 style="margin:0 0 12px 0;font-size:16px;color:#111827;">{title}</h3>
            <div style="background:#eff6ff;border-radius:6px;padding:12px 16px;margin-bottom:16px;font-size:14px;color:#1e3a5f;">
                <strong>AI 摘要：</strong>{summary}
            </div>
            <table style="width:100%;border-collapse:collapse;font-size:13px;">
                <thead>
                    <tr style="background:#f9fafb;text-align:left;">
                        <th style="padding:8px 12px;border-bottom:1px solid #e5e7eb;">航线</th>
                        <th style="padding:8px 12px;border-bottom:1px solid #e5e7eb;">动作</th>
                        <th style="padding:8px 12px;border-bottom:1px solid #e5e7eb;">生效日期</th>
                        <th style="padding:8px 12px;border-bottom:1px solid #e5e7eb;">机型</th>
                    </tr>
                </thead>
                <tbody>{route_rows}</tbody>
            </table>
            <p style="color:#9ca3af;font-size:12px;margin-top:16px;">此邮件由 MyNewsAVI 自动发送 · 详情请返回 Mac 查看完整 Dashboard</p>
        </div>
    </div>"""
