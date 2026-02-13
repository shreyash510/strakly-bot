from langchain_core.tools import tool
from .base import get_api_client, extract_list


@tool
async def get_document_templates() -> dict:
    """Get list of document/waiver templates.

    Use this tool when user asks about:
    - Document templates
    - Waiver templates
    - What documents are available
    """
    client = get_api_client()
    try:
        response = await client.get("/documents/templates")
        templates = extract_list(response)

        if not templates:
            return {"count": 0, "templates": [], "message": "No document templates found."}

        return {
            "count": len(templates),
            "templates": [
                {
                    "id": t.get("id"),
                    "name": t.get("name"),
                    "type": t.get("type"),
                    "version": t.get("version"),
                    "isActive": t.get("isActive"),
                }
                for t in templates
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_template_details(template_id: int) -> dict:
    """Get full details of a document template including content.

    Args:
        template_id: The ID of the template

    Use this tool when user asks about a specific template's content or details.
    """
    client = get_api_client()
    try:
        response = await client.get(f"/documents/templates/{template_id}")
        return response
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_signed_documents_for_user(user_id: int) -> dict:
    """Get all signed documents for a specific user/member.

    Args:
        user_id: The user ID to look up signed documents for

    Use this tool when user asks about a member's signed documents or waivers.
    """
    client = get_api_client()
    try:
        response = await client.get(f"/documents/user/{user_id}")
        docs = extract_list(response)

        if not docs:
            return {"count": 0, "documents": [], "message": "No signed documents found for this user."}

        return {
            "count": len(docs),
            "documents": [
                {
                    "id": d.get("id"),
                    "templateName": d.get("templateName"),
                    "templateType": d.get("templateType"),
                    "signerName": d.get("signerName"),
                    "agreed": d.get("agreed"),
                    "signedAt": d.get("signedAt"),
                    "versionSigned": d.get("versionSigned"),
                    "pdfUrl": d.get("pdfUrl"),
                }
                for d in docs
            ],
        }
    except Exception as e:
        return {"error": str(e)}


@tool
async def get_signed_document_pdf(signed_doc_id: int) -> dict:
    """Get the PDF URL for a signed document. Generates the PDF on demand if it doesn't exist yet.

    Args:
        signed_doc_id: The ID of the signed document

    Use this tool when user asks for a signed document PDF or download link.
    """
    client = get_api_client()
    try:
        response = await client.get(f"/documents/signed/{signed_doc_id}/pdf")
        return {"pdfUrl": response.get("pdfUrl"), "success": True}
    except Exception as e:
        return {"error": str(e), "success": False}


@tool
async def create_document_template(
    name: str,
    content: str,
    doc_type: str = "waiver",
) -> dict:
    """Create a new document/waiver template.

    IMPORTANT: Only call this tool AFTER showing confirmation to the user and getting their approval.

    Args:
        name: Template name (required)
        content: HTML content of the document (required)
        doc_type: Document type - waiver, contract, par_q, consent, or terms (optional, defaults to waiver)
    """
    valid_types = ["waiver", "contract", "par_q", "consent", "terms"]
    if doc_type not in valid_types:
        return {"error": f"Invalid type. Must be one of: {', '.join(valid_types)}", "success": False}

    client = get_api_client()
    try:
        response = await client.post("/documents/templates", {
            "name": name,
            "type": doc_type,
            "content": content,
        })
        return {
            "success": True,
            "message": f"Template '{name}' created successfully",
            "template": {
                "id": response.get("id"),
                "name": response.get("name"),
                "type": response.get("type"),
            },
        }
    except Exception as e:
        return {"error": str(e), "success": False}
