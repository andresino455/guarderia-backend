import os
from typing import Optional

import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException


class BrevoEmailService:
    def __init__(self) -> None:
        self.api_key = os.getenv("BREVO_API_KEY")
        self.sender_email = os.getenv("BREVO_SENDER_EMAIL")
        self.sender_name = os.getenv("BREVO_SENDER_NAME", "Sistema")

        if not self.api_key:
            raise ValueError("BREVO_API_KEY no está configurada en el .env")

        if not self.sender_email:
            raise ValueError("BREVO_SENDER_EMAIL no está configurada en el .env")

        configuration = sib_api_v3_sdk.Configuration()
        configuration.api_key["api-key"] = self.api_key

        self.api_client = sib_api_v3_sdk.ApiClient(configuration)
        self.email_api = sib_api_v3_sdk.TransactionalEmailsApi(self.api_client)

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        to_name: Optional[str] = None,
        text_content: Optional[str] = None,
    ):
        send_smtp_email = sib_api_v3_sdk.SendSmtpEmail(
            sender={
                "name": self.sender_name,
                "email": self.sender_email,
            },
            to=[
                {
                    "email": to_email,
                    "name": to_name or to_email,
                }
            ],
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )

        try:
            return self.email_api.send_transac_email(send_smtp_email)
        except ApiException as e:
            raise Exception(f"Error enviando correo con Brevo: {str(e)}")

    def send_codigo_seguridad(
        self,
        to_email: str,
        nombre_destinatario: str,
        nombre_nino: str,
        nombre_persona_autorizada: str,
        codigo_seguridad: str,
    ):
        subject = f"Código de seguridad para recoger a {nombre_nino}"

        html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 24px; background: #f8fafc; border-radius: 16px;">
            <div style="background: #ffffff; border-radius: 16px; padding: 32px; border: 1px solid #e5e7eb;">
                <h2 style="color: #0f172a; margin-top: 0;">Hola {nombre_destinatario}</h2>

                <p style="color: #334155; font-size: 15px; line-height: 1.6;">
                    Se ha generado un código de seguridad para la persona autorizada a recoger a:
                </p>

                <p style="font-size: 18px; font-weight: bold; color: #1e293b;">
                    {nombre_nino}
                </p>

                <p style="color: #334155; font-size: 15px; line-height: 1.6;">
                    Persona autorizada:
                    <strong>{nombre_persona_autorizada}</strong>
                </p>

                <div style="margin: 24px 0; padding: 20px; background: #eff6ff; border: 1px solid #bfdbfe; border-radius: 12px; text-align: center;">
                    <p style="margin: 0 0 8px; color: #1e3a8a; font-size: 14px;">Código de seguridad</p>
                    <p style="margin: 0; font-size: 28px; font-weight: bold; color: #1d4ed8; letter-spacing: 2px;">
                        {codigo_seguridad}
                    </p>
                </div>

                <p style="color: #475569; font-size: 14px; line-height: 1.6;">
                    Presenta este código cuando sea necesario. Si el código es regenerado, el anterior dejará de ser válido.
                </p>

                <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 24px 0;" />

                <p style="color: #64748b; font-size: 12px; margin-bottom: 0;">
                    Este es un mensaje automático del sistema de guardería.
                </p>
            </div>
        </div>
        """

        text_content = (
            f"Hola {nombre_destinatario},\n\n"
            f"Se generó un código de seguridad para recoger a {nombre_nino}.\n"
            f"Persona autorizada: {nombre_persona_autorizada}\n"
            f"Código: {codigo_seguridad}\n\n"
            f"Este es un mensaje automático del sistema."
        )

        return self.send_email(
            to_email=to_email,
            to_name=nombre_destinatario,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
        )