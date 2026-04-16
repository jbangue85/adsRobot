import os
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.advideo import AdVideo
from facebook_business.adobjects.adimage import AdImage
from facebook_business.adobjects.ad import Ad
from facebook_business.adobjects.adset import AdSet
from meta_ads_mcp.client import get_ad_account


def upload_image(image_path: str) -> dict:
    """
    Sube una imagen a la biblioteca de Meta y devuelve su hash.

    Args:
        image_path: Ruta absoluta o relativa al archivo de imagen (JPG, PNG).

    Returns:
        Dict con image_hash y otras propiedades de la imagen subida.
    """
    account = get_ad_account()
    image = AdImage(parent_id=account.get_id())
    image[AdImage.Field.filename] = os.path.abspath(image_path)
    image.remote_create()
    return {
        "image_hash": image[AdImage.Field.hash],
        "url": image.get(AdImage.Field.url, ""),
        "name": os.path.basename(image_path),
    }


def upload_video(
    video_path: str,
    title: str | None = None,
    thumbnail_path: str | None = None,
) -> dict:
    """
    Sube un video a la biblioteca de Meta y devuelve su ID.

    Args:
        video_path: Ruta absoluta o relativa al archivo de video (MP4, MOV).
        title: Título del video en la biblioteca de Meta.
        thumbnail_path: Ruta a la imagen de thumbnail (opcional).

    Returns:
        Dict con video_id y estado de la subida.
    """
    account = get_ad_account()
    video = AdVideo(parent_id=account.get_id())
    video[AdVideo.Field.filepath] = os.path.abspath(video_path)
    if title:
        video[AdVideo.Field.title] = title
    if thumbnail_path:
        video[AdVideo.Field.thumb] = os.path.abspath(thumbnail_path)
    video.remote_create()
    return {
        "video_id": video[AdVideo.Field.id],
        "title": title or os.path.basename(video_path),
        "status": "uploaded",
    }


def create_ad_creative_image(
    name: str,
    image_hash: str,
    headline: str,
    body: str,
    link: str,
    call_to_action: str = "SHOP_NOW",
    description: str | None = None,
    page_id: str | None = None,
    instagram_actor_id: str | None = None,
) -> dict:
    """
    Crea un creativo de imagen para usar en anuncios.

    Args:
        name: Nombre interno del creativo.
        image_hash: Hash de la imagen (obtenido de upload_image).
        headline: Título del anuncio (máx 40 caracteres).
        body: Texto principal del anuncio (máx 125 caracteres).
        link: URL de destino del anuncio.
        call_to_action: Botón de CTA (SHOP_NOW, LEARN_MORE, SIGN_UP, etc.).
        description: Descripción extra opcional (máx 30 caracteres).
        page_id: ID de la página de Facebook (usa META_PAGE_ID del .env si no se pasa).
        instagram_actor_id: ID del actor de Instagram (opcional).
    """
    account = get_ad_account()
    page_id = page_id or os.environ.get("META_PAGE_ID", "")

    object_story_spec: dict = {
        "page_id": page_id,
        "link_data": {
            "image_hash": image_hash,
            "link": link,
            "message": body,
            "name": headline,
            "call_to_action": {"type": call_to_action},
        },
    }
    if description:
        object_story_spec["link_data"]["description"] = description
    if instagram_actor_id:
        object_story_spec["instagram_actor_id"] = instagram_actor_id

    creative = account.create_ad_creative(
        fields=[AdCreative.Field.id, AdCreative.Field.name],
        params={
            AdCreative.Field.name: name,
            AdCreative.Field.object_story_spec: object_story_spec,
        },
    )
    return dict(creative)


def create_ad_creative_video(
    name: str,
    video_id: str,
    headline: str,
    body: str,
    link: str,
    call_to_action: str = "SHOP_NOW",
    description: str | None = None,
    image_hash: str | None = None,
    page_id: str | None = None,
    instagram_actor_id: str | None = None,
) -> dict:
    """
    Crea un creativo de video para usar en anuncios.

    Args:
        name: Nombre interno del creativo.
        video_id: ID del video (obtenido de upload_video).
        headline: Título del anuncio (máx 40 caracteres).
        body: Texto principal del anuncio (máx 125 caracteres).
        link: URL de destino del anuncio.
        call_to_action: Botón de CTA (SHOP_NOW, LEARN_MORE, WATCH_MORE, etc.).
        description: Descripción extra opcional.
        image_hash: Hash del thumbnail (opcional, Meta elige uno automáticamente si se omite).
        page_id: ID de la página de Facebook.
        instagram_actor_id: ID del actor de Instagram (opcional).
    """
    account = get_ad_account()
    page_id = page_id or os.environ.get("META_PAGE_ID", "")

    video_data: dict = {
        "video_id": video_id,
        "message": body,
        "title": headline,
        "call_to_action": {"type": call_to_action, "value": {"link": link}},
    }
    if description:
        video_data["link_description"] = description
    if image_hash:
        video_data["image_hash"] = image_hash

    object_story_spec: dict = {
        "page_id": page_id,
        "video_data": video_data,
    }
    if instagram_actor_id:
        object_story_spec["instagram_actor_id"] = instagram_actor_id

    creative = account.create_ad_creative(
        fields=[AdCreative.Field.id, AdCreative.Field.name],
        params={
            AdCreative.Field.name: name,
            AdCreative.Field.object_story_spec: object_story_spec,
        },
    )
    return dict(creative)


def create_ad(
    ad_set_id: str,
    creative_id: str,
    name: str,
    status: str = "PAUSED",
) -> dict:
    """
    Crea un anuncio combinando un ad set con un creativo.

    Args:
        ad_set_id: ID del ad set donde vivirá el anuncio.
        creative_id: ID del creativo (de create_ad_creative_image o create_ad_creative_video).
        name: Nombre interno del anuncio.
        status: ACTIVE o PAUSED (default: PAUSED).
    """
    account = get_ad_account()
    ad = account.create_ad(
        fields=[Ad.Field.id, Ad.Field.name],
        params={
            Ad.Field.name: name,
            Ad.Field.adset_id: ad_set_id,
            Ad.Field.creative: {"creative_id": creative_id},
            Ad.Field.status: status,
        },
    )
    return dict(ad)
