# email_utils.py - エラーハンドリングを強化
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import url_for
import logging

# ロギング設定
logger = logging.getLogger(__name__)

def send_email(to_email, subject, body, html_body=None):
    """メールを送信する関数（デバッグ情報付き）"""
    # 環境変数から設定を取得
    smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
    smtp_port = int(os.getenv('SMTP_PORT', '587'))
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_email = os.getenv('FROM_EMAIL', smtp_username)
    
    # デバッグ情報
    logger.info(f"メール送信試行: {to_email}")
    logger.info(f"SMTP設定: {smtp_server}:{smtp_port}")
    logger.info(f"送信元: {from_email}")
    
    if not smtp_username or not smtp_password:
        logger.error("SMTP認証情報が設定されていません")
        logger.error(f"SMTP_USERNAME: {'設定済み' if smtp_username else '未設定'}")
        logger.error(f"SMTP_PASSWORD: {'設定済み' if smtp_password else '未設定'}")
        return False
    
    try:
        # メッセージの作成
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = from_email
        msg['To'] = to_email
        
        # テキストパート
        text_part = MIMEText(body, 'plain', 'utf-8')
        msg.attach(text_part)
        
        # HTMLパート（オプション）
        if html_body:
            html_part = MIMEText(html_body, 'html', 'utf-8')
            msg.attach(html_part)
        
        # SMTPサーバーに接続して送信
        logger.info("SMTPサーバーに接続中...")
        with smtplib.SMTP(smtp_server, smtp_port, timeout=30) as server:
            server.set_debuglevel(1)  # デバッグ出力を有効化
            
            logger.info("STARTTLS開始...")
            server.starttls()
            
            logger.info("ログイン試行中...")
            server.login(smtp_username, smtp_password)
            
            logger.info("メール送信中...")
            server.send_message(msg)
        
        logger.info(f"✅ メール送信成功: {to_email}")
        return True
        
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f"認証エラー: {e}")
        logger.error("アプリパスワードを使用していることを確認してください")
        
    except smtplib.SMTPServerDisconnected as e:
        logger.error(f"サーバー切断エラー: {e}")
        logger.error("SMTP設定を確認してください")
        
    except smtplib.SMTPException as e:
        logger.error(f"SMTPエラー: {e}")
        
    except Exception as e:
        logger.error(f"予期しないエラー: {type(e).__name__}: {e}")
        
    return False

def send_password_reset_email(user_email, reset_url):
    """パスワードリセットメールを送信"""
    subject = "パスワードリセットのご案内 - Working Log PWA"
    
    body = f"""
こんにちは、

Working Log PWAのパスワードリセットのリクエストを受け付けました。

以下のリンクをクリックして、新しいパスワードを設定してください：
{reset_url}

このリンクは1時間で有効期限が切れます。

もしこのリクエストを行っていない場合は、このメールを無視してください。
あなたのパスワードは変更されません。

ご不明な点がございましたら、サポートまでお問い合わせください。

Working Log PWA チーム
    """
    
    html_body = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
</head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #0066cc;">パスワードリセットのご案内</h2>
        
        <p>こんにちは、</p>
        
        <p>Working Log PWAのパスワードリセットのリクエストを受け付けました。</p>
        
        <p>以下のボタンをクリックして、新しいパスワードを設定してください：</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" 
               style="background-color: #0066cc; color: white; padding: 12px 30px; 
                      text-decoration: none; border-radius: 5px; display: inline-block;">
                パスワードをリセット
            </a>
        </div>
        
        <p style="color: #666; font-size: 14px;">
            またはこちらのURLをコピーしてブラウザに貼り付けてください：<br>
            <span style="word-break: break-all;">{reset_url}</span>
        </p>
        
        <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
        
        <p style="color: #666; font-size: 14px;">
            <strong>注意事項：</strong><br>
            ・このリンクは1時間で有効期限が切れます。<br>
            ・もしこのリクエストを行っていない場合は、このメールを無視してください。<br>
            ・あなたのパスワードは変更されません。
        </p>
        
        <p style="color: #999; font-size: 12px; margin-top: 30px;">
            Working Log PWA チーム
        </p>
    </div>
</body>
</html>
    """
    
    return send_email(user_email, subject, body, html_body)